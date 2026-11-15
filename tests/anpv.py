# algebra/'s new lines against sympy and mpmath:
#   NPV    exactly the values that make some bottom typed 0 (one letter),
#          where that bottom's own roots are all there: from equations
#          and from simplifying with roots (and nothing for fractions to
#          check here: frfuzz.py does those)
#   Restr  when simplifying with roots: every piece is what one root
#          typed needs (>= 0), or the x>=0 that simplifying took; and
#          every root typed that needs something has its piece
#
#   python3 anpv.py [count] [seed]     (run from tests/, sympy on PYTHONPATH)
import sys, re, random
from multiprocessing import Pool

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1


def nz(a, b):
    while True:
        r = random.randint(a, b)
        if r:
            return r


def lin():
    a = random.choice([1, 1, 1, 2, 3])
    return '%dx%+d' % (a, nz(-9, 9)) if a > 1 else 'x%+d' % nz(-9, 9)


def g_rootbottom():
    # simplifying with a root in a bottom
    r = random.random()
    A = random.randint(0, 9)
    k = random.randint(1, 4)
    if r < 0.2:
        return '%d/(sqrt(%s)%+d)' % (nz(-9, 9), lin(), nz(-5, 5))
    if r < 0.35:
        return '(x-%d)/(sqrt(x)-%d)' % (k * k, k)
    if r < 0.5:
        return 'sqrt(%s)/(%s)' % (lin(), random.choice([lin(), 'x^2-%d' % (k * k), 'x^2-%d' % k, 'x^2+%d' % k]))
    if r < 0.6:
        return '1/(1+1/sqrt(%s))' % lin()
    if r < 0.7:
        return 'sqrt(%s)/sqrt(%s)' % (lin(), lin())
    if r < 0.8:
        return '(sqrt(x)+%d)/(sqrt(%s)-sqrt(%s))' % (A, lin(), lin())
    if r < 0.9:
        return '%d/(%d-sqrt(%s))+sqrt(x)/x' % (nz(-5, 5), k, lin())
    return '(%s)^(-1/2)' % lin()


def g_eqbottom():
    # equations with bottoms: roots in them, bottoms in bottoms
    r = random.random()
    k = random.randint(1, 4)
    if r < 0.3:
        return '%d/(sqrt(%s)%+d)=%d' % (nz(-9, 9), lin(), nz(-4, 4), nz(-5, 5))
    if r < 0.5:
        return 'sqrt(x)/(%s)=%d' % (lin(), nz(-3, 3))
    if r < 0.7:
        return '1/(1+%d/(%s))=%d' % (nz(-5, 5), lin(), random.randint(0, 3))
    if r < 0.85:
        return '(x-%d)/(sqrt(x)-%d)=%d' % (k * k, k, nz(1, 9))
    return '%d/(%s)+%d/(%s)=%d' % (nz(-5, 5), lin(), nz(-5, 5), lin(), random.randint(-2, 2))


def gen(n):
    random.seed(SEED * 1000003 + n)
    r = random.random()
    if r < 0.3:
        return 'rootbottom', g_rootbottom()
    if r < 0.6:
        return 'eqbottom', g_eqbottom()
    if r < 0.8:
        return 'rfuzz', EG(n)[1]
    return 'sfuzz', SG(n)[1]


EG = SG = None


def init():
    global sp, mp, go, X, S, EG, SG
    import sympy as sp
    import mpmath as mp
    sys.path.insert(0, '../algebra')
    import algcore
    go = algcore.go
    X = sp.Symbol('x')

    class S(sp.Function):
        nargs = 1
    globals()['S'] = S
    sys.argv = ['x', '../rad.py', '1', str(SEED)]
    a = {}
    exec(open('rfuzz.py').read().split('# ---------------------------------------------------------- reference')[0], a)
    sys.argv = ['x', '../radsimp.py', '1', str(SEED)]
    b = {}
    exec(open('sfuzz.py').read().split('# ---------------------------------------------------------- checking')[0], b)
    EG, SG = a['gen'], b['gen']


def half(s):
    # (...)^(1/2), ^0.5, ^(3/2), ^(-1/2) as S(...)
    for pat, k in (('^(1/2)', '1'), ('^0.5', '1'), ('^(3/2)', '3'), ('^(-1/2)', '-1'), ('^1.5', '3')):
        while pat in s:
            i = s.index(pat)
            j = i - 1
            if s[j] == ')':
                d = 0
                while True:
                    d += (s[j] == ')') - (s[j] == '(')
                    if d == 0:
                        break
                    j -= 1
            s = s[:j] + 'S(' + s[j:i] + ')**(' + k + ')' + s[i + len(pat):]
    return s


def parse(t):
    t = half(t.replace(' ', ''))
    t = t.replace('sqrt(', 'S(')
    t = re.sub(r'(\d+)\.(\d+)', lambda m: '(%d/%d)' % (int(m.group(1) + m.group(2)), 10 ** len(m.group(2))), t)
    t = t.replace('^', '**')
    t = re.sub(r'(?<=[\dx)])(?=[xS(])', '*', t)
    t = re.sub(r'(?<=x)(?=\d)', '**', t)
    return sp.parse_expr(t, local_dict={'S': S, 'x': X}, evaluate=False)


def roots_of(b):
    # real x where b = 0 and every root inside b is there
    g = b
    ys = []
    pr = []
    while True:
        at = [a for a in g.atoms(S) if not a.args[0].atoms(S)]
        if not at:
            break
        for a in at:
            y = sp.Symbol('y%d' % len(ys))
            ys.append(y)
            pr.append(a.args[0])
            g = g.xreplace({a: y})
            pr = [p.xreplace({a: y}) for p in pr]
    G = sp.numer(sp.together(sp.expand(sp.together(g))))
    for i in range(len(ys) - 1, -1, -1):
        t = sp.together(pr[i])
        G = sp.expand(sp.resultant(sp.Poly(G, ys[i]), sp.Poly(sp.denom(t) * ys[i] ** 2 - sp.numer(t), ys[i])).as_expr())
    if G == 0:
        return None
    if not G.has(X):
        return []
    out = []
    f = sp.lambdify([X], b, [{'S': mp.sqrt}, 'mpmath'])
    ins = [sp.lambdify([X], a.args[0], [{'S': mp.sqrt}, 'mpmath']) for a in b.atoms(S)]
    for rr in sorted(set(sp.real_roots(sp.Poly(G, X).sqf_part()))):
        mp.mp.dps = 150
        xv = mp.mpf(sp.N(rr, 170))
        ok = True
        try:
            for d in ins:
                v = d(xv)
                if isinstance(v, mp.mpc) and abs(v.imag) > mp.mpf(10) ** -40 or mp.re(v) < -mp.mpf(10) ** -40:
                    ok = False
            v = f(xv)
        except (ZeroDivisionError, ValueError):
            continue
        if ok and abs(v) < mp.mpf(10) ** -40:
            out.append(float(sp.N(rr, 30)))
    return out


def lab(t):
    if t.startswith('~'):
        return float(t[1:])
    return float(sp.N(sp.sympify(re.sub(r'(?<=[\d)])(?=sqrt)', '*', t)), 30))


def domain(r):
    # where a radicand typed (no root inside) is >= 0, as a test
    return sp.lambdify([X], r, 'mpmath')


def pieceset(u):
    # one Restr piece as a test on x, or None for x>=0 style ones that
    # simplifying took (U)
    if u.endswith('>0') and not u.endswith('>=0'):
        return None
    def val(t):
        return lab(t)
    parts = []
    for v in u.split(' or '):
        if v == 'no x':
            continue
        if v.startswith('x<='):
            parts.append((None, val(v[3:])))
        elif v.startswith('x>='):
            parts.append((val(v[3:]), None))
        elif v.startswith('x='):
            parts.append((val(v[2:]), val(v[2:])))
        else:
            l, r = v.split('<=x<=')
            parts.append((val(l), val(r)))
    return parts


def inp(parts, x):
    return any((lo is None or x >= lo - 1e-9) and (hi is None or x <= hi + 1e-9) for lo, hi in parts)


def check(n):
    name, q = gen(n)
    errs = []
    if re.search('[a-wyz]', q.replace('sqrt', '')):
        return name, q, [], []
    try:
        out = go(q.lower().replace(' ', '').replace('**', '^'))
    except Exception as e:
        return name, q, [], ['Err ' + str(e)]
    if out and out[0].startswith('Err'):
        return name, q, [], out
    e = q.split('=')
    try:
        f = parse(e[0]) if len(e) == 1 else sp.Add(parse(e[0]), -parse(e[1]), evaluate=False)
    except Exception as x:
        return name, q, [], out
    bots = [p.base for p in sp.preorder_traversal(f) if isinstance(p, sp.Pow) and p.exp.is_number and p.exp < 0]
    want = set()
    for b in bots:
        z = roots_of(b)
        if z is None:
            return name, q, [], out
        for v in z:
            want.add(round(v, 6))
    P = [l for l in out if l.startswith('NPV: ')]
    got = set()
    if P and 'range' not in P[0]:
        for t in P[0].split('!=', 1)[1].split(','):
            got.add(round(lab(t), 6))
    if 'x' not in q:
        want = set()
    near = lambda a, B: any(abs(a - b) < 2e-4 * (1 + abs(a)) for b in B)
    if [a for a in want if not near(a, got)] or [a for a in got if not near(a, want)]:
        errs.append('npv: program %s, want %s' % (sorted(got), sorted(want)))
    if len(e) == 1 and 'x' in q:
        # Restr when simplifying
        rads = [a.args[0] for a in sp.preorder_traversal(f) if isinstance(a, S) and not a.args[0].atoms(S)]
        rl = [l for l in out if l.startswith('Restr: ')]
        pieces = rl[0][7:].split(', ') if rl else []
        tests = [domain(r) for r in rads]
        pts = [random.uniform(-40, 40) for _ in range(30)] + [k / 4 for k in range(-40, 41)]
        def same(parts, d):
            for x in pts:
                try:
                    v = d(mp.mpf(x))
                except ZeroDivisionError:
                    continue
                v = mp.re(v)
                if abs(v) < 1e-9:
                    continue
                if inp(parts, x) != (v > 0):
                    return False
            return True
        ps = [pieceset(u) for u in pieces]
        for u, parts in zip(pieces, ps):
            if parts is None or u == 'x>=0':
                continue
            if not [d for d in tests if same(parts, d)]:
                errs.append('restr piece %s matches no root' % u)
        for r, d in zip(rads, tests):
            every = all(mp.re(d(mp.mpf(x))) >= -1e-9 for x in pts)
            if every:
                continue
            if not [p for p in ps if p is not None and same(p, d)]:
                errs.append('root of %s has no restr piece' % r)
    return name, q, errs, out


if __name__ == '__main__':
    from collections import Counter
    cnt = Counter()
    bad = 0
    with Pool(2, initializer=init) as pool:
        for i, (name, q, errs, out) in enumerate(pool.imap_unordered(check, range(N), chunksize=10)):
            cnt[name] += 1
            if errs:
                bad += 1
                print('BAD', name, repr(q), out, errs[:2], flush=True)
            if (i + 1) % 500 == 0:
                print(i + 1, 'done,', bad, 'bad', flush=True)
    print(dict(cnt))
    print(N, 'questions,', bad, 'bad')
