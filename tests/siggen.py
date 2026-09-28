"""Build the question sets and check the calculator three ways:
   1. the answer's VALUE against exact-fraction arithmetic
   2. the SIG FIG COUNT against the rules applied independently
   3. the PRINTED answer re-read - it must show the figures it claims"""
import random, sys
sys.path.insert(0, '.')
import sigref as R

NUM = ['2.5', '3.0', '1.2', '4.50', '12.0', '0.50', '100.', '7',
       '25.0', '0.025', '6.02', '1.008', '9.99', '150.', '0.10',
       '45.6', '3.14', '2.00', '18', '0.0050', '1000.', '8.0',
       '0.75', '33.3', '5.0', '10.0', '4.995', '12.11', '1.013', '60']
OPS = '+-*/'


def simple(rng):
    n = rng.randint(2, 3)
    parts = [rng.choice(NUM)]
    for _ in range(n - 1):
        parts.append(rng.choice(OPS))
        parts.append(rng.choice(NUM))
    return ''.join(parts)


def hard(rng, depth=0):
    r = rng.random()
    if depth >= 2 or r < 0.3:
        return rng.choice(NUM)
    n = rng.randint(2, 4)
    out = []
    for i in range(n):
        if i:
            out.append(rng.choice(OPS))
        if rng.random() < 0.45:
            out.append('(' + hard(rng, depth + 1) + ')')
        else:
            out.append(rng.choice(NUM))
    s = ''.join(out)
    if depth == 0 and rng.random() < 0.35:
        s = '(' + s + ')' + rng.choice(OPS) + rng.choice(NUM)
    return s


def build(gen, seed, n):
    rng = random.Random(seed)
    out = []
    seen = set()
    while len(out) < n:
        e = gen(rng)
        if e in seen:
            continue
        try:
            R.solve(e)
        except Exception:
            continue
        seen.add(e)
        out.append(e)
    return out


def run(name, eqs, S, show=6):
    bad = []
    for e in eqs:
        try:
            txt, sig = S.calculate(e)
        except Exception as ex:
            bad.append((e, 'CRASH ' + str(ex), ''))
            continue
        wv, ws = R.solve(e)
        why = []
        if sig != ws:
            why.append('sig %d want %d' % (sig, ws))
        try:
            gv = R.read(txt)
            if gv != wv:
                why.append('value %s want %s' % (txt, str(float(wv))))
        except Exception:
            why.append('unreadable %r' % txt)
        rr = S.count_sigfigs(txt)
        if rr != sig:
            why.append('prints %r which reads as %d not %d' % (txt, rr, sig))
        if why:
            bad.append((e, txt + ' (' + str(sig) + ' sf)', '; '.join(why)))
    print('%-22s %3d asked, %3d wrong' % (name, len(eqs), len(bad)))
    for b in bad[:show]:
        print('    %-28s -> %-16s %s' % b)
    return len(bad)
