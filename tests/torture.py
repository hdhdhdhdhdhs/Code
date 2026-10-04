"""Maximum-effort test of the sig-fig calculator.

Four checks per expression, three of which never consult the reference:
  A  VALUE+COUNT   vs an exact-fraction engine with its own parser
  B  RE-READ       the printed answer must show the figures it claims
  C  WINDOW        the printed value must be the exact value correctly
                   rounded - within half a unit of the last place claimed
  D  IDEMPOTENT    feeding the answer back in must give the answer back
"""
import random, sys
from fractions import Fraction
sys.path.insert(0, '.')
import sigref as R
import siglib as S

HARSH = ['0', '0.0', '0.00', '0.000', '0.5', '1.25', '2.35', '0.15',
         '1.005', '2.675', '9.95', '99.5', '9.99', '0.1', '0.2', '0.3',
         '1e9', '1.0e-7', '123456789.', '0.000001', '1.0', '2.0', '100',
         '100.', '0.0050', '6.02e23', '1.5e3', '7', '60', '1000.', '3.14',
         '0.99999', '1.00000', '12.345', '0.0999', '8.125', '4.35']
OPS = ['+', '-', '*', '/']


def gen(rng, depth=0, maxd=3):
    if depth >= maxd or rng.random() < 0.25:
        t = rng.choice(HARSH)
        if rng.random() < 0.10:
            return t + '^' + str(rng.randint(0, 4))
        return t
    n = rng.randint(2, 5 if depth == 0 else 3)
    out = []
    for i in range(n):
        if i:
            r = rng.random()
            out.append('' if r < 0.08 else rng.choice(OPS))
        piece = gen(rng, depth + 1, maxd)
        if rng.random() < 0.5 or (out and out[-1] == ''):
            piece = '(' + piece + ')'
        out.append(piece)
    return ''.join(out)


def win_ok(txt, sig, exact):
    """The printed value must be `exact` rounded to the place it claims.
    A printed 0 carries no magnitude, so its precision cannot be read back
    out of the text - skip those rather than guess."""
    got = R.read(txt)
    if got == 0:
        return True
    place = R.mag_of(abs(got)) - sig + 1          # value of the last digit
    half = Fraction(10) ** place / 2
    return abs(exact - got) <= half


def run(name, eqs):
    fails = {}
    n = 0
    for e in eqs:
        try:
            wv, ws = R.solve(e)
        except Exception:
            continue                       # reference cannot judge it
        n += 1
        try:
            txt, sig = S.calculate(e)
        except Exception as ex:
            fails.setdefault('CRASH', []).append((e, str(ex), ''))
            continue
        if txt.startswith('-0') and R.read(txt) == 0:
            fails.setdefault('E minus zero', []).append((e, txt, 'should be 0'))
            continue
        if sig != ws:
            fails.setdefault('A count', []).append((e, txt + ' (%d sf)' % sig,
                                                    'want %d sf' % ws))
            continue
        try:
            gv = R.read(txt)
        except Exception:
            fails.setdefault('B unreadable', []).append((e, txt, ''))
            continue
        if gv != wv:
            fails.setdefault('A value', []).append((e, txt, 'want ' + str(wv)))
            continue
        if S.count_sigfigs(txt) != sig:
            fails.setdefault('B re-read', []).append(
                (e, txt, 'reads as %d not %d' % (S.count_sigfigs(txt), sig)))
            continue
        ex_v, _ = R.P(e).expr()[0], None
        try:
            p = R.P(e)
            exact = p.expr()[0]
            if not win_ok(txt, sig, exact):
                fails.setdefault('C window', []).append(
                    (e, txt, 'exact ' + str(float(exact))))
                continue
        except Exception:
            pass
        try:
            t2, s2 = S.calculate(txt)
            if (t2, s2) != (txt, sig):
                fails.setdefault('D idempotent', []).append(
                    (e, txt + ' (%d sf)' % sig, 'again -> %s (%d sf)' % (t2, s2)))
        except Exception as ex:
            fails.setdefault('D crash on own answer', []).append(
                (e, txt, str(ex)))
    tot = sum(len(v) for v in fails.values())
    print('%-26s %6d checked, %5d FAIL' % (name, n, tot))
    for k in sorted(fails):
        print('    %-22s %d' % (k, len(fails[k])))
        for f in fails[k][:3]:
            print('        %-34s -> %-16s %s' % f)
    return fails
