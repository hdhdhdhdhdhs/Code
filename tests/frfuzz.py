# frac.py against sympy and exact fractions.
#
# Every question is built from known factors, then for each one:
#   value  Ans and Fac equal the question at random fraction points
#          (exact, with Python's Fraction), away from the NPVs
#   lowest Ans's top and bottom share no factor (sympy gcd)
#   factor every bracket in Fac does not split further (sympy)
#   npv    the NPVs are exactly the values that make some bottom typed
#          0 (every x^-n, every /(...) as typed, inner ones too):
#          one-letter ones as numbers, others as factors
#   width  no line over 21 after wrapping
#
#   python3 frfuzz.py [count] [seed]      (run from tests/)
import sys, random, re
from fractions import Fraction as Fr
from multiprocessing import Pool

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
SRC = '../frac.py'


def nz(a, b):
    while True:
        r = random.randint(a, b)
        if r:
            return r


# ---------------------------------------------------------- questions
# each piece is (text with * and **, for Python and sympy)
def lin(v):
    a = random.choice([1, 1, 1, 2, 3])
    b = nz(-9, 9)
    while Fr(b, a).denominator != a and a > 1 and b % a == 0:
        b = nz(-9, 9)
    s = random.choice([1, 1, 1, -1])
    return '(%d*%s%+d)' % (a * s, v, b * s) if a * s != 1 else '(%s%+d)' % (v, b)


def quad(v):
    return '(%s)' % random.choice(['%s**2+1', '%s**2+%s+1', '%s**2-2', '2*%s**2+3', '%s**2-%s-1',
                                   '%s**2+4', '3*%s**2-5']).replace('%s', v)


def piece(vs):
    v = random.choice(vs)
    r = random.random()
    if r < 0.6:
        return lin(v)
    if r < 0.75:
        return quad(v)
    if r < 0.9:
        return v + ('**%d' % random.randint(2, 3) if random.random() < 0.4 else '')
    if len(vs) > 1:
        w = random.choice([u for u in vs if u != v])
        return '(%s%+d*%s)' % (v, nz(-3, 3), w)
    return str(nz(2, 9))


def prod(ps):
    return '*'.join(ps) if ps else '1'


def expand(t):
    import sympy as sp
    return str(sp.expand(sp.sympify(t, locals=SYMS))).replace(' ', '')


def frac(vs, shared=None, top=None, bot=None):
    sh = shared if shared is not None else [piece(vs) for _ in range(random.randint(0, 2))]
    t = [piece(vs) for _ in range(random.randint(0, 2) if top is None else top)]
    b = [piece(vs) for _ in range(random.randint(1, 2) if bot is None else bot)]
    c = random.choice([1, 1, 1, 2, 3, -1, 4, 6])
    d = random.choice([1, 1, 1, 2, 3, 5])
    T = expand('%d*%s' % (c, prod(t + sh)))
    B = expand('%d*%s' % (d, prod(b + sh)))
    return '(%s)/(%s)' % (T, B)


def letters():
    r = random.random()
    if r < 0.6:
        return [random.choice('xxxxxabmnt')]
    if r < 0.85:
        return random.sample('xyab', 2)
    return random.sample('abcxyz', 3)


def g_cancel():
    return frac(letters())


def g_times():
    vs = letters()
    s = frac(vs) + '*' + frac(vs)
    return s + ('*' + frac(vs) if random.random() < 0.3 else '')


def g_divide():
    vs = letters()
    return frac(vs) + '/(' + frac(vs) + ')'


def g_add():
    vs = letters()
    o = ''
    for i in range(random.randint(2, 3)):
        n = expand(prod([piece(vs) for _ in range(random.randint(0, 1))]) + '*%d' % nz(-5, 5))
        d = expand(prod([piece(vs) for _ in range(random.randint(1, 2))]))
        o += random.choice('+-') + '(%s)/(%s)' % (n, d)
    return o.lstrip('+')


def g_complex():
    vs = letters()
    v = vs[0]
    w = vs[-1]
    r = random.random()
    if r < 0.3:
        return '(1/%s%s1/%s)/(1/%s%s1/%s)' % (v, random.choice('+-'), w, v, random.choice('+-'), w)
    a = '%d/%s%s%d' % (nz(-5, 5), lin(v), random.choice('+-'), nz(1, 5))
    b = '%d/%s%s%d/%s' % (nz(-5, 5), lin(v), random.choice('+-'), nz(1, 5), lin(w))
    return '(%s)/(%s)' % (a, b)


def g_exps():
    vs = letters()
    def mono():
        return '%d*' % nz(-12, 12) + '*'.join('%s**%d' % (v, nz(-7, 7)) for v in vs)
    s = '(%s)/(%s)' % (mono(), mono())
    if random.random() < 0.4:
        s = '(%s)**%d' % (s, nz(-3, 3))
    if random.random() < 0.3:
        s += '*(%s)' % mono()
    return s


def g_two():
    vs = random.sample('xyab', 2)
    x, y = vs
    P = ['(%s+%s)' % (x, y), '(%s-%s)' % (x, y), '(%s-2*%s)' % (x, y), '(2*%s+3*%s)' % (x, y),
         '(%s**2+%s**2)' % (x, y), '(%s**2+%s*%s+%s**2)' % (x, x, y, y), x, y]
    def f():
        sh = random.sample(P, random.randint(0, 2))
        return '(%s)/(%s)' % (expand(prod(sh + random.sample(P, random.randint(0, 2)))),
                              expand(prod(sh + random.sample(P, random.randint(1, 2)))))
    return f() + random.choice(['*', '/', '+', '-']) + f()


def g_group():
    x, y = random.sample('xyab', 2)
    A = '(%s%+d)' % (x, nz(-6, 6))
    B = '(%s%+d)' % (y, nz(-6, 6))
    C = random.choice([A, B, '(%s%+d)' % (x, nz(-6, 6)), '(%s+%s)' % (x, y)])
    return '(%s)/(%s)' % (expand(A + '*' + B), expand(C + '*' + random.choice([A, B, '1', x])))


def g_big():
    vs = [random.choice('xxab')]
    ps = [piece(vs) for _ in range(random.randint(3, 5))]
    qs = random.sample(ps, random.randint(1, 3)) + [piece(vs) for _ in range(random.randint(0, 2))]
    return '(%s)/(%s)' % (expand(prod(ps)), expand(prod(qs)))


def g_hard():
    # one letter, pieces with no zero p/q: x^2+2x+2, x^3-2, x^2-3 ...
    v = random.choice('xxa')
    H = ['(%s**2+2*%s+2)', '(%s**2-2*%s+2)', '(%s**3-2)', '(%s**3+%s+1)', '(%s**2-3)', '(%s**4+%s+1)',
         '(%s+1)**3', '(2*%s-1)**2', '(%s**2+1)**2']
    def p():
        return random.choice(H).replace('%s', v) if random.random() < 0.6 else lin(v)
    sh = [p() for _ in range(random.randint(1, 2))]
    return '(%s)/(%s)' % (expand(prod(sh + [p() for _ in range(random.randint(0, 2))])),
                          expand(prod(sh + [p() for _ in range(random.randint(0, 2))])))


def g_nums():
    # fractions and decimals as numbers: typed 0.5x or (1/2)x
    v = random.choice('xxy')
    a = Fr(nz(-9, 9), random.choice([1, 2, 4, 5, 10]))
    b = Fr(nz(-9, 9), random.choice([1, 2, 4, 5]))
    def t(f):
        return '(%d/%d)' % (f.numerator, f.denominator)
    return '(%s*%s**2%s%s*%s)/(%s*%s%s%s)' % (t(a), v, '+', t(b), v, t(b), v, '+', t(a * b))


def g_letters():
    vs = random.sample('abcdefghkmnpqrsuvwz', random.randint(4, 6))
    def mono():
        return '%d*' % nz(-20, 20) + '*'.join('%s**%d' % (v, nz(-5, 5)) for v in vs if random.random() < 0.8)
    return '(%s)/(%s)*(%s)' % (mono().rstrip('*'), mono().rstrip('*'), mono().rstrip('*'))


def g_nest():
    v = random.choice('xxt')
    s = v
    for _ in range(random.randint(2, 4)):
        s = '%d/(%d%s%s)' % (nz(1, 3), nz(-3, 3), random.choice('+-'), s)
    return s


def g_powers():
    v = random.choice('xxab')
    f = '(%s/%s)' % (lin(v), lin(v))
    g = '(%s/%s)' % (lin(v), lin(v))
    return '%s**%d*%s**%d' % (f, nz(-3, 3), g, nz(-3, 3))


def g_multi():
    # several letters, pieces that need a*x+b found: x-y^2, xy+1, x-y+1
    x, y = random.sample('xyab', 2)
    P = ['(%s-%s**2)' % (x, y), '(%s+%s**2)' % (x, y), '(%s*%s+1)' % (x, y), '(%s*%s-2)' % (x, y),
         '(%s-%s+1)' % (x, y), '(%s+%s-1)' % (x, y), '(%s**2+%s)' % (x, y), '(2*%s-%s**2)' % (x, y),
         '(%s%+d)' % (x, nz(-4, 4)), '(%s%+d)' % (y, nz(-4, 4))]
    sh = random.sample(P, random.randint(1, 2))
    return '(%s)/(%s)' % (expand(prod(sh + random.sample(P, random.randint(0, 1)))),
                          expand(prod(sh + random.sample(P, random.randint(0, 2)))))


FAM = [('several letters', g_multi, 4), ('hard one letter', g_hard, 3), ('numbers', g_nums, 2), ('many letters', g_letters, 2),
       ('nested', g_nest, 2), ('powers', g_powers, 3),
       ('cancel', g_cancel, 5), ('times', g_times, 4), ('divide', g_divide, 4), ('add', g_add, 5),
       ('complex', g_complex, 3), ('exponents', g_exps, 4), ('two letters', g_two, 4), ('grouping', g_group, 2),
       ('big', g_big, 2)]


def typed(s, r):
    # as it might be typed: ^ or **, * left out, spaces
    s = s.replace('**', '^' if r.random() < 0.8 else '**')
    if r.random() < 0.7:
        s = re.sub(r'(?<=[\d)a-z])\*(?=[a-z(])', '', s)
    if r.random() < 0.1:
        s = ' '.join(s)
    return s


SYMS = {}


def gen(n):
    random.seed(SEED * 1000003 + n)
    tot = sum(w for _, _, w in FAM)
    k = random.uniform(0, tot)
    for name, f, w in FAM:
        k -= w
        if k <= 0:
            break
    q = f()
    return name, q, typed(q, random)


# ---------------------------------------------------------- checking
def init():
    global sp, go, wrap, W, SYMS
    import sympy as sp
    for c in 'abcdefghijklmnopqrstuvwxyz':
        SYMS[c] = sp.Symbol(c)
    s = open(SRC).read()
    G = {}
    exec(s[:s.index("print('Rational expressions")], G)
    # the screen shows each line through st (x^2*y): check that
    go = lambda q: [G['st'](l) for l in G['go'](q)]
    wrap, W = G['wrap'], G['W']


def pyexpr(t):
    # program text -> Python: * where it is left out, ** for ^
    t = t.replace('^', '**').replace(' ', '').replace('sqrt', 'Q')
    t = re.sub(r'(?<=[\d)a-z])(?=[a-zQ(])', '*', t)
    t = re.sub(r'(?<=[a-z)])(?=\d)', '**', t)
    return t.replace('Q', 'sqrt')


def ev(t, pt):
    return eval(re.sub(r'(\d+)', r'Fr(\1)', pyexpr(t)), {'Fr': Fr}, pt)


def split_top(t):
    d = 0
    for i, c in enumerate(t):
        d += (c == '(') - (c == ')')
        if c == '/' and d == 0:
            return t[:i], t[i + 1:]
    return t, '1'


def bases(e):
    o = []
    for p in sp.preorder_traversal(e):
        if isinstance(p, sp.Pow) and p.exp.is_number and p.exp < 0:
            o.append(p.base)
    return o


def norm(f):
    f = sp.Poly(f, *sorted(f.free_symbols, key=str)).primitive()[1].as_expr()
    c = sp.Poly(f, *sorted(f.free_symbols, key=str)).coeffs()[0]
    return sp.expand(-f if c < 0 else f)


def refnpv(e):
    one = {}
    multi = set()
    for b in bases(e):
        num = sp.numer(sp.together(b))
        if num.is_number:
            continue
        for f, _ in sp.factor_list(num)[1]:
            fs = f.free_symbols
            if len(fs) == 1:
                v = str(list(fs)[0])
                one.setdefault(v, set())
                for r in sp.Poly(f, list(fs)[0]).real_roots():
                    one[v].add(round(float(r), 4))
            else:
                multi.add(norm(f))
    return one, multi


def prognpv(line):
    one = {}
    multi = set()
    for g in line.split('; '):
        if g == 'none':
            continue
        lhs, rhs = g.split('!=')
        if ',' in lhs or lhs in SYMS and rhs == '0' and False:
            for v in lhs.split(','):
                one.setdefault(v, set()).add(0.0)
            continue
        for val in rhs.split(','):
            if lhs in SYMS and not re.search('[a-z]', val.replace('sqrt', '')):
                x = float(val[1:]) if val.startswith('~') else float(sp.sympify(pyexpr(val), locals=SYMS))
                one.setdefault(lhs, set()).add(round(x, 4))
            else:
                p = sp.sympify(pyexpr(lhs), locals=SYMS) - sp.sympify(pyexpr(val), locals=SYMS)
                for f, _ in sp.factor_list(p)[1]:
                    if len(f.free_symbols) == 1:
                        v = str(list(f.free_symbols)[0])
                        for r in sp.Poly(f, list(f.free_symbols)[0]).real_roots():
                            one.setdefault(v, set()).add(round(float(r), 4))
                    else:
                        multi.add(norm(f))
    return one, multi


def check(n):
    name, full, q = gen(n)
    errs = []
    try:
        out = go(q)
    except Exception as e:
        if str(e) == 'divide by 0':
            e2 = sp.parse_expr(full, local_dict=SYMS, evaluate=False)
            if any(sp.simplify(b) == 0 for b in bases(e2)):
                return name, q, [], []
        return name, q, ['crash: %r' % e], []
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                errs.append('wide: ' + w)
    A = [l[5:] for l in out if l.startswith('Ans: ')]
    if not A:
        return name, q, ['no Ans: %s' % out], out
    a = A[0]
    F = [l[5:] for l in out if l.startswith('Fac: ')]
    P = [l[5:] for l in out if l.startswith('NPV: ')]
    e = sp.parse_expr(full, local_dict=SYMS, evaluate=False)
    # value
    vs = sorted(set(re.findall('[a-z]', full)))
    good = 0
    r = random.Random(n)
    for _ in range(12):
        pt = dict((v, Fr(r.randint(-40, 40), r.randint(1, 9))) for v in vs)
        try:
            want = eval(full, {'Fr': Fr}, pt) if 0 else ev(full, pt)
        except ZeroDivisionError:
            continue
        good += 1
        for t in [a] + F:
            try:
                got = ev(t, pt)
            except ZeroDivisionError:
                errs.append('value: %s is 1/0 at %s' % (t, pt))
                continue
            if got != want:
                errs.append('value: %s gives %s, question %s at %s' % (t, got, want, pt))
        if good >= 4:
            break
    # lowest terms
    tp, bt = split_top(a)
    T = sp.sympify(pyexpr(tp), locals=SYMS)
    B = sp.sympify(pyexpr(bt), locals=SYMS)
    if not sp.gcd(sp.expand(T), sp.expand(B)).is_number:
        errs.append('not lowest terms: %s' % a)
    # factored
    for f in re.findall(r'\(([^()]*)\)', F[0] if F else ''):
        if not re.search('[+-]', f[1:]):
            continue
        x = sp.sympify(pyexpr(f), locals=SYMS)
        fl = sp.factor_list(x)[1]
        if len(fl) > 1 or fl and fl[0][1] > 1:
            errs.append('not fully factored: (%s)' % f)
    # npv
    ro, rm = refnpv(e)
    if P:
        po, pmu = prognpv(P[0])
    else:
        po, pmu = {}, set()
    ro = dict((k, v) for k, v in ro.items() if v)
    po = dict((k, v) for k, v in po.items() if v)
    if ro != po or rm != pmu:
        errs.append('npv: program %s %s, want %s %s' % (po, pmu, ro, rm))
    return name, q, errs, out


if __name__ == '__main__':
    from collections import Counter
    cnt = Counter()
    badc = Counter()
    nbad = 0
    with Pool(2, initializer=init) as pool:
        for i, (name, q, errs, out) in enumerate(pool.imap_unordered(check, range(N), chunksize=20)):
            cnt[name] += 1
            if errs:
                badc[name] += 1
                nbad += 1
                print('BAD', name, repr(q), out, errs[:3], flush=True)
            if (i + 1) % 1000 == 0:
                print(i + 1, 'done,', nbad, 'bad', flush=True)
    for name, _, _ in FAM:
        print('%-14s %6d checked %5d bad' % (name, cnt[name], badc[name]))
    print(N, 'questions,', nbad, 'bad')
