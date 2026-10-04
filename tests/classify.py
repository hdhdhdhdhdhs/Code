"""Sort every disagreement into a cause, so nothing hides in the pile."""
import sys, random
from fractions import Fraction
sys.path.insert(0, '.')
import sigref as R, siglib as S, torture as T


def cause(e, txt, sig, wv, ws):
    if any(z in e for z in ['0.0', '0.00', '0.000']) and \
       not any(c.isdigit() and c != '0' for c in
               ''.join(x for x in e if x in '0123456789.')[:0] or '1'):
        pass
    # zero literal present?
    import re
    for m in re.findall(r'\d*\.?\d+(?:[eE][-+]?\d+)?', e):
        try:
            if float(m) == 0:
                return 'zero literal'
        except Exception:
            pass
    if txt.startswith('-0') and R.read(txt) == 0:
        return 'minus zero'
    # is the exact value sitting on a rounding boundary?
    try:
        exact = R.P(e).expr()[0]
        dec = None
        p = R.P(e)
        _v, _s, dec = p.expr()
        if exact != 0:
            scaled = abs(exact) * Fraction(10) ** dec
            frac = scaled - int(scaled)
            d = abs(frac - Fraction(1, 2))
            if d < Fraction(1, 10 ** 7):
                return 'half boundary (1e-9 nudge / float)'
    except Exception:
        pass
    # magnitude just under a power of ten?
    try:
        v = float(abs(R.read(txt)))
        m = ('%e' % v)
        if m.startswith('1.000000') and v < 10 ** int(m.split('e')[1]):
            return 'magnitude under a power of ten'
    except Exception:
        pass
    # did a float lose a small term against a huge one?
    try:
        import re as _re
        ms = [abs(float(x)) for x in
              _re.findall(r'\d*\.?\d+(?:[eE][-+]?\d+)?', e) if x not in '.']
        ms = [m for m in ms if m > 0]
        if ms and max(ms) / min(ms) > 1e14:
            return 'float cancellation (huge vs tiny)'
    except Exception:
        pass
    return 'UNEXPLAINED'


def sweep(eqs, label):
    counts = {}
    unexplained = []
    n = 0
    for e in eqs:
        try:
            wv, ws = R.solve(e)
        except Exception:
            continue
        n += 1
        try:
            txt, sig = S.calculate(e)
        except Exception:
            counts['crash'] = counts.get('crash', 0) + 1
            continue
        ok = (sig == ws)
        if ok:
            try:
                ok = (R.read(txt) == wv)
            except Exception:
                ok = False
        if ok and S.count_sigfigs(txt) != sig:
            ok = False
        if ok:
            continue
        c = cause(e, txt, sig, wv, ws)
        counts[c] = counts.get(c, 0) + 1
        if c == 'UNEXPLAINED' and len(unexplained) < 12:
            unexplained.append((e, txt, sig, str(wv), ws))
    print('%-34s %7d checked' % (label, n))
    for k in sorted(counts, key=lambda x: -counts[x]):
        print('      %-38s %5d' % (k, counts[k]))
    for u in unexplained:
        print('      !! %s' % (u,))
    return counts
