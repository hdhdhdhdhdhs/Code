# rad.py against an independent solver, on hard random equations.
#
# Each equation is typed the way it would be on the calculator, and
# also read by sympy with its own parser. The reference puts a symbol in
# for every root, removes them one by one with resultants, finds every
# real zero of what is left exactly, and keeps the zeros that make the
# original equation hold at 60 digits. rad.py's Ans line must list
# exactly those, exact ones exactly and ~ ones to 6 digits.
#
#   PYTHONPATH must reach sympy:  python3 rfuzz.py ../rad.py [count] [seed]
import sys, random, re
from fractions import Fraction as Fr
from multiprocessing import Pool

SRC = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 1


# ---------------------------------------------------------- generator
def nz(a, b):
    v = 0
    while v == 0:
        v = random.randint(a, b)
    return v


def numstr(f, paren=True):
    # a Fraction as the calculator would be typed
    f = Fr(f)
    if f.denominator == 1:
        return str(f.numerator)
    d = f.denominator
    if d in (2, 4, 5, 8, 10, 20, 25) and random.random() < 0.5:
        s = '%r' % float(f)
        return s
    s = '%d/%d' % (f.numerator, d)
    return '(' + s + ')' if paren else s


def coefx(a, mono):
    # a * mono (mono is 'x', 'x^2', 'sqrt(...)' ...)
    a = Fr(a)
    if a == 1:
        return mono
    if a == -1:
        return '-' + mono
    if a.denominator != 1 and random.random() < 0.3 and a.numerator in (1, -1):
        return ('-' if a < 0 else '') + mono + '/' + str(a.denominator)
    s = numstr(a)
    if random.random() < 0.15:
        return s + '*' + mono
    return s + mono


def join(terms):
    s = ''
    for t in terms:
        if t == '' or t == '0':
            continue
        if s and t[0] != '-':
            s += '+'
        s += t
    return s or '0'


def poly(cs):
    # cs high power first
    n = len(cs) - 1
    t = []
    for i, c in enumerate(cs):
        p = n - i
        if c == 0:
            continue
        if p == 0:
            t.append(numstr(c))
        else:
            t.append(coefx(c, 'x' if p == 1 else 'x^%d' % p))
    return join(t)


def rt(inner, simple=False):
    # a square root, mostly with the root key, sometimes as a power
    r = random.random()
    if not simple and r < 0.06:
        return '(' + inner + ')^(1/2)'
    if not simple and r < 0.1:
        return '(' + inner + ')^0.5'
    return 'sqrt(' + inner + ')'


def x0pick():
    r = random.random()
    if r < 0.7:
        return Fr(random.randint(-8, 20))
    return Fr(random.randint(-20, 40), random.randint(2, 5))


def sval():
    r = random.random()
    if r < 0.8:
        return Fr(random.randint(0, 9))
    return Fr(random.randint(0, 20), random.randint(2, 4))


def lin_at(x0, s, small=False):
    # a x + b with value s^2 at x0
    a = Fr(nz(-9, 9)) if random.random() < 0.85 else Fr(nz(-9, 9), random.randint(2, 4))
    b = s * s - a * x0
    return [a, b]


def quad_at(x0, s):
    a = Fr(nz(-5, 5))
    b = Fr(random.randint(-9, 9))
    c = s * s - a * x0 * x0 - b * x0
    return [a, b, c]


def coef():
    r = random.random()
    if r < 0.75:
        return Fr(nz(-6, 6))
    return Fr(nz(-9, 9), random.randint(2, 4))


def eqn(terms, const):
    # terms: list of term strings with their values at x0 summing to const
    # randomly move terms across the =, flipping signs
    left = []
    right = []
    for t, v in terms:
        if random.random() < 0.65:
            left.append(t)
        else:
            right.append(neg(t))
    if random.random() < 0.5:
        right.append(numstr(const))
    else:
        left.append(numstr(-const))
    if not left:
        left.append('0')
    if not right:
        right.append('0')
    return join(left) + '=' + join(right)


def neg(t):
    if t.startswith('-'):
        return t[1:]
    return '-' + t


def g_two():
    x0 = x0pick()
    ts = []
    tot = Fr(0)
    for _ in range(2):
        s = sval()
        L = lin_at(x0, s)
        a = coef()
        ts.append((coefx(a, rt(poly(L))), a * s))
        tot += a * s
    return eqn(ts, tot)


def g_many(k):
    x0 = x0pick()
    ts = []
    tot = Fr(0)
    for _ in range(k):
        s = sval()
        L = lin_at(x0, s) if random.random() < 0.8 else quad_at(x0, s)
        a = coef()
        ts.append((coefx(a, rt(poly(L))), a * s))
        tot += a * s
    if random.random() < 0.4:
        a = coef()
        ts.append((coefx(a, 'x'), a * x0))
        tot += a * x0
    return eqn(ts, tot)


def g_rootsum():
    # sqrt(L1) + sqrt(L2) = sqrt(L3)
    x0 = x0pick()
    s1, s2 = sval(), sval()
    a1, a2 = coef(), coef()
    s3 = abs(a1 * s1 + a2 * s2)
    L1, L2, L3 = lin_at(x0, s1), lin_at(x0, s2), lin_at(x0, s3)
    return join([coefx(a1, rt(poly(L1))), coefx(a2, rt(poly(L2)))]) + '=' + rt(poly(L3))


def g_quadrad():
    # sqrt(Q) = m x + k, both planted values meet at x0
    x0 = x0pick()
    m = coef()
    k = Fr(random.randint(-9, 9))
    s = m * x0 + k
    if s < 0:
        m, k, s = -m, -k, -s
    Q = quad_at(x0, s)
    return rt(poly(Q)) + '=' + poly([m, k])


def g_form():
    # a sqrt(L) + b x + c = 0
    x0 = x0pick()
    s = sval()
    L = lin_at(x0, s)
    a, b = coef(), coef()
    c = -(a * s + b * x0)
    return eqn([(coefx(a, rt(poly(L))), a * s), (coefx(b, 'x'), b * x0)], -c)


def g_nested():
    x0 = x0pick()
    s2 = sval()
    L2 = lin_at(x0, s2)
    k = coef()
    c = sval()
    a1 = Fr(nz(-6, 6))
    b1 = c * c - k * s2 - a1 * x0
    inner = join([poly([a1, b1]), coefx(k, rt(poly(L2), True))])
    if random.random() < 0.5:
        return rt(inner, True) + '=' + numstr(c)
    # with another root beside it
    s3 = sval()
    L3 = lin_at(x0, s3)
    d = coef()
    return join([rt(inner, True), coefx(d, rt(poly(L3)))]) + '=' + numstr(c + d * s3)


def g_product():
    x0 = x0pick()
    s1, s2 = sval(), sval()
    L1, L2 = lin_at(x0, s1), lin_at(x0, s2)
    a = coef()
    m = coef()
    k = a * s1 * s2 - m * x0
    p = rt(poly(L1)) + ('*' if random.random() < 0.5 else '') + rt(poly(L2))
    return coefx(a, p) if False else numstr(a) + '*' + p + '=' + poly([m, k])


def g_quad2():
    # sqrt(Q1) - sqrt(Q2) = m x + k
    x0 = x0pick()
    s1, s2 = sval(), sval()
    Q1, Q2 = quad_at(x0, s1), quad_at(x0, s2)
    m = coef()
    k = s1 - s2 - m * x0
    return rt(poly(Q1)) + '-' + rt(poly(Q2)) + '=' + poly([m, k])


def g_random():
    k = random.randint(2, 3)
    ts = []
    for _ in range(k):
        L = [Fr(nz(-9, 9)), Fr(random.randint(-15, 15))]
        ts.append(coefx(coef(), rt(poly(L))))
    if random.random() < 0.5:
        ts.append(coefx(coef(), 'x'))
    return join(ts) + '=' + numstr(Fr(random.randint(-12, 12)))


def g_power():
    x0 = x0pick()
    s = sval()
    L = lin_at(x0, s)
    r = random.random()
    if r < 0.5:
        a = Fr(random.randint(-6, 6))
        # (sqrt(L)+a)^2 = m x + k
        m = coef()
        k = (s + a) ** 2 - m * x0
        return '(' + join([rt(poly(L), True), numstr(a)]) + ')^2=' + poly([m, k])
    # L^(3/2) = s^3
    return '(' + poly(L) + ')^(3/2)=' + numstr(s ** 3)


def g_tangent():
    m = coef()
    k = Fr(random.randint(-9, 9))
    x0 = x0pick()
    v = m * x0 + k
    if v < 0:
        m, k, v = -m, -k, -v
    a = 2 * m * v
    if a == 0:
        a = Fr(1)
    b = v * v - a * x0
    return rt(poly([a, b])) + '=' + poly([m, k])


def g_abs():
    # sqrt((p x + q)^2) written out = m x + k
    p, q = nz(-5, 5), random.randint(-9, 9)
    m, k = coef(), Fr(random.randint(-9, 9))
    return rt(poly([p * p, 2 * p * q, q * q])) + '=' + poly([m, k])


def g_constroot():
    # roots of plain numbers mixed in
    a = random.choice([2, 3, 5, 8, 12, 18, 50])
    L = [Fr(nz(-9, 9)), Fr(random.randint(-9, 9))]
    return coefx(coef(), 'sqrt(%d)' % a) + 'x+' + rt(poly(L)) + '=' + numstr(Fr(random.randint(-9, 9)))


FAM = [
    ('two roots', g_two, 20),
    ('three roots', lambda: g_many(3), 12),
    ('four roots', lambda: g_many(4), 4),
    ('sum of roots', g_rootsum, 8),
    ('quadratic inside', g_quadrad, 8),
    ('quadratic form', g_form, 8),
    ('root in root', g_nested, 8),
    ('product', g_product, 6),
    ('two quadratics', g_quad2, 6),
    ('random', g_random, 8),
    ('powers', g_power, 5),
    ('tangent', g_tangent, 3),
    ('perfect square', g_abs, 3),
    ('number roots', g_constroot, 3),
]


def gen(i):
    random.seed(SEED * 1000003 + i)
    tot = sum(w for _, _, w in FAM)
    r = random.random() * tot
    for name, f, w in FAM:
        r -= w
        if r < 0:
            return name, f()
    return FAM[-1][0], FAM[-1][1]()


# ---------------------------------------------------------- reference
def ref_init():
    global sp, X, Sf, mp
    import sympy as sp
    import mpmath as mp
    X = sp.Symbol('x')

    class Sf(sp.Function):
        nargs = 1
    globals()['Sf'] = Sf
    s = open(SRC).read()
    exec(s[:s.index("print('Root equations")], globals())


def half_powers(s):
    # (...)^(1/2), (...)^0.5, (...)^(3/2) -> S(...), S(...)**3
    for pat, k in (('^(1/2)', 1), ('^0.5', 1), ('^(3/2)', 3)):
        while pat in s:
            i = s.index(pat)
            j = i - 1
            if s[j] == ')':
                d = 0
                while True:
                    if s[j] == ')':
                        d += 1
                    elif s[j] == '(':
                        d -= 1
                        if d == 0:
                            break
                    j -= 1
                base = s[j:i]
            else:
                base = s[j:i]
            rep = 'S(' + base + ')' + ('**%d' % k if k > 1 else '')
            s = s[:j] + rep + s[i + len(pat):]
    return s


def ref_parse(t):
    t = half_powers(t)
    t = t.replace('sqrt(', 'S(')
    t = re.sub(r'(\d+)\.(\d+)', lambda m: '(%d/%d)' % (int(m.group(1) + m.group(2)), 10 ** len(m.group(2))), t)
    t = t.replace('^', '**')
    t = re.sub(r'(?<=[\dx)])(?=[xS(])', '*', t)
    return sp.sympify(t, locals={'S': Sf, 'x': X})


def reference(eq):
    l, r = eq.split('=')
    f = ref_parse(l) - ref_parse(r)
    ys = []
    pr = []
    g = f
    while True:
        at = [a for a in g.atoms(Sf) if not a.args[0].atoms(Sf)]
        if not at:
            break
        for a in at:
            y = sp.Symbol('y%d' % len(ys))
            ys.append(y)
            pr.append(sp.expand(a.args[0]))
            g = g.xreplace({a: y})
            pr = [p.xreplace({a: y}) for p in pr]
    G = sp.expand(sp.together(g))
    G = sp.numer(sp.together(G))
    for i in range(len(ys) - 1, -1, -1):
        G = sp.resultant(sp.Poly(G, ys[i]), sp.Poly(ys[i] ** 2 - pr[i], ys[i])).as_expr()
        G = sp.expand(G)
    if G == 0:
        return ('all', g, pr, ys)
    P = sp.Poly(G, X)
    if P.degree() <= 0:
        return []
    out = []
    mp.mp.dps = 120
    fl = sp.lambdify([X] + ys, g, 'mpmath')
    pl = [sp.lambdify([X] + ys, p, 'mpmath') for p in pr]
    for rr in sorted(set(sp.real_roots(P.sqf_part()))):
        xv = mp.mpf(sp.N(rr, 130))
        vals = []
        bad = False
        for p in pl:
            v = p(xv, *(vals + [0] * (len(ys) - len(vals))))
            if v < mp.mpf('-1e-90'):
                bad = True
                break
            vals.append(mp.sqrt(max(v, 0)))
        if bad:
            continue
        if abs(fl(xv, *vals)) < mp.mpf('1e-40'):
            out.append(rr)
    return out


class Slow(Exception):
    pass


def alarm(*a):
    raise Slow()


def val(t):
    if t.startswith('~'):
        return mp.mpf(t[1:])
    v = ref_parse(t)
    return mp.mpf(sp.N(v.replace(Sf, lambda a: sp.sqrt(a)), 60))


def rangecheck(a, ref):
    _, g, pr, ys = ref
    mp.mp.dps = 120
    fl = sp.lambdify([X] + ys, g, 'mpmath')
    pl = [sp.lambdify([X] + ys, p, 'mpmath') for p in pr]

    def holds(xv):
        vals = []
        for p in pl:
            v = p(xv, *(vals + [0] * (len(ys) - len(vals))))
            if v < mp.mpf('-1e-90'):
                return False
            vals.append(mp.sqrt(max(v, 0)))
        return abs(fl(xv, *vals)) < mp.mpf('1e-40')
    sp_ = [] if a == 'no solution' else a.split(', ')
    ivs = []
    ends = []
    for t in sp_:
        if t == 'every x':
            ivs.append((None, None))
        elif t.startswith('x<='):
            ivs.append((None, val(t[3:])))
        elif t.startswith('x>='):
            ivs.append((val(t[3:]), None))
        elif t.startswith('x='):
            v = val(t[2:])
            ivs.append((v, v))
        else:
            l, r = t.split('<=x<=')
            ivs.append((val(l), val(r)))
    for lo, hi in ivs:
        ends += [e for e in (lo, hi) if e is not None]

    def inside(xv):
        for lo, hi in ivs:
            if (lo is None or xv >= lo - mp.mpf('1e-50')) and (hi is None or xv <= hi + mp.mpf('1e-50')):
                return True
        return False
    pts = [mp.mpf(random.uniform(-60, 60)) for _ in range(40)] + [mp.mpf(-1000), mp.mpf(1000)]
    for e in ends:
        pts += [e, e - mp.mpf('1e-6'), e + mp.mpf('1e-6')]
    bad = [p for p in pts if holds(p) != inside(p)]
    return ['range wrong near x=%s' % mp.nstr(bad[0], 8)] if bad else []


def check(i):
    import signal
    signal.signal(signal.SIGALRM, alarm)
    name, eq = gen(i)
    errs = []
    signal.alarm(10)
    try:
        out = solve(eq)
    except Slow:
        return name, eq, [], ['PROGRAM TOOK OVER 10s']
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    signal.alarm(0)
    for ln in out:
        for w in wrap(ln):
            if len(w) > W:
                errs.append('wide')
    signal.alarm(120)
    try:
        ref = reference(eq)
    except Slow:
        return name, eq, out, ['REFERENCE TOOK OVER 120s']
    except Exception as e:
        return name, eq, out, ['REFERENCE FAILED ' + repr(e)]
    signal.alarm(0)
    a = [l for l in out if l.startswith('Ans:')]
    if isinstance(ref, tuple):
        # a range: test points inside, outside and at every end
        if not a:
            if any('check by hand' in l or 'every x' in l for l in out):
                return name, eq, out, errs + ['style: range left to check by hand']
            return name, eq, out, errs + ['no Ans line for a range']
        return name, eq, out, errs + rangecheck(a[0][5:], ref)
    if out[0].startswith('Err'):
        return name, eq, out, errs + ['error']
    if not a:
        return name, eq, out, errs + ['no Ans line']
    a = a[0][5:]
    got = [] if a == 'no solution' else a.split(', ')
    if len(got) != len(ref):
        return name, eq, out, errs + ['want %d answers: %s' % (len(ref), [sp.N(r, 8) for r in ref])]
    gv = []
    for t in got:
        if t.startswith('x='):
            v = ref_parse(t[2:].replace('sqrt(', 'sqrt('))
            v = sp.N(v.replace(Sf, lambda a: sp.sqrt(a)), 60)
            gv.append((mp.mpf(v), 1, t))
        else:
            gv.append((mp.mpf(t[2:]), 0, t))
    gv.sort(key=lambda t: t[0])
    for (v, ex, t), rr in zip(gv, ref):
        rv = mp.mpf(sp.N(rr, 60))
        if ex:
            if abs(v - rv) > mp.mpf('1e-40') * (1 + abs(rv)):
                errs.append('wrong ' + t)
        else:
            if abs(v - rv) > 6e-6 * max(1, abs(rv)):
                errs.append('wrong ' + t)
            if rr.is_rational:
                errs.append('style: fraction shown as decimal ' + t)
    return name, eq, out, errs


if __name__ == '__main__':
    with Pool(2, initializer=ref_init) as P:
        st = {}
        bad = []
        style = 0
        for k, (name, eq, out, errs) in enumerate(P.imap_unordered(check, range(N), chunksize=20)):
            s = st.setdefault(name, [0, 0])
            s[0] += 1
            real = [e for e in errs if not e.startswith('style')]
            if len(real) < len(errs):
                style += 1
            if real:
                s[1] += 1
                bad.append((name, eq, out, errs))
                print('BAD', name, eq, out, errs, flush=True)
            if (k + 1) % 5000 == 0:
                print(k + 1, 'done,', len(bad), 'bad', flush=True)
        for name in st:
            print('%-17s %6d checked %5d bad' % (name, st[name][0], st[name][1]))
        print(N, 'equations,', len(bad), 'bad,', style, 'with a fraction shown as a decimal')
        for b in bad[:25]:
            print(b)
