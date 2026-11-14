# radsimp.py (rad.py with no =) against sympy, on hard simplifying questions.
#
# Each question is typed the way it would be on the calculator, and also
# read by sympy (letters positive, as radsimp.py takes them). Its Ans
# must equal the question at several random points to 50 digits, and be
# in simplest form: no root in any bottom, every number under a root
# square-free and every letter under a root to the power 1, and no two
# terms with the same root (like roots added). Nothing may pass 21
# columns.
#   PYTHONPATH must reach sympy:  python3 sfuzz.py ../radsimp.py [count] [seed]
import sys, random, re
from fractions import Fraction as Fr
from multiprocessing import Pool

SRC = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 1

SQ = [8, 12, 18, 20, 24, 27, 28, 32, 40, 44, 45, 48, 50, 54, 63, 72, 75,
      80, 90, 98, 99, 108, 125, 128, 147, 150, 162, 175, 200, 242, 243,
      245, 288, 300, 338, 363, 392, 500, 588, 648, 675, 800, 1000]
PR = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 30]


def nz(a, b):
    v = 0
    while v == 0:
        v = random.randint(a, b)
    return v


def rn():
    return random.choice(SQ + PR + [4, 9, 16, 25, 36])


def cf(allow_frac=True):
    r = random.random()
    if r < 0.7 or not allow_frac:
        return str(nz(-9, 9))
    if r < 0.85:
        return '(%d/%d)' % (nz(-9, 9), random.randint(2, 6))
    return random.choice(['0.5', '1.5', '2.5', '0.25', '-0.5'])


def rt(n):
    return 'sqrt(%s)' % n


def term(c, r):
    if c == '1':
        return r
    if c == '-1':
        return '-' + r
    return c + ('*' if random.random() < 0.15 else '') + r


def join(ts):
    s = ''
    for t in ts:
        if s and t[0] != '-':
            s += '+'
        s += t
    return s


def g_combo():
    return join([term(cf(), rt(rn())) for _ in range(random.randint(2, 5))])


def g_product():
    a = join([term(cf(False), rt(rn())) for _ in range(random.randint(1, 2))])
    b = join([term(cf(False), rt(rn())) if random.random() < 0.8 else cf(False) for _ in range(2)])
    if random.random() < 0.3:
        return '(' + a + ')^2'
    return '(' + a + ')(' + b + ')'


def g_single_div():
    r = random.random()
    if r < 0.4:
        return '%s/%s' % (nz(-30, 30), term(str(nz(1, 9)), rt(rn())))
    if r < 0.7:
        return '%s/%s' % (term(cf(False), rt(rn())), rt(rn()))
    return 'sqrt(%d/%d)' % (random.randint(1, 60), random.randint(2, 60))


def g_conj():
    top = random.choice([cf(False), term(cf(False), rt(rn())),
                         join([cf(False), term(cf(False), rt(rn()))])])
    bot = random.choice([join([str(nz(-9, 9)), term(cf(False), rt(random.choice(PR)))]),
                         join([rt(random.choice(PR)), term(random.choice(['1', '-1', '2']), rt(random.choice(PR)))])])
    return '(' + top + ')/(' + bot + ')'


def g_three():
    ps = random.sample([2, 3, 5, 6, 7, 10, 11], 3)
    bot = join([term(random.choice(['1', '-1', '2']), rt(p)) for p in ps])
    if random.random() < 0.3:
        bot = join([str(nz(-5, 5)), rt(ps[0]), term('-1', rt(ps[1]))])
    return '%d/(%s)' % (nz(-12, 12), bot)


LETS = 'abcmnpwxyz'


def mono():
    k = random.choice([1, 2, 3, 4, 5, 6, 8, 12, 18, 20, 27, 45, 50, 72])
    s = str(k) if k > 1 else ''
    for l in random.sample(LETS, random.randint(1, 2)):
        e = random.randint(1, 5)
        s += l + ('^%d' % e if e > 1 else '')
    return s


def g_letters():
    r = random.random()
    if r < 0.3:
        return rt(mono())
    if r < 0.5:
        return join([term(cf(False), rt(mono())) for _ in range(2)])
    if r < 0.65:
        return rt(mono()) + '*' + rt(mono())
    if r < 0.8:
        l = random.choice(LETS)
        return '%d/%s' % (nz(-9, 9), term(str(nz(1, 5)), rt(str(random.choice([1, 2, 3, 5])) + l)))
    l, m = random.sample(LETS, 2)
    return random.choice(['(sqrt(%s)+sqrt(%s))^2' % (l, m), '(sqrt(%s)+%d)(sqrt(%s)-%d)' % (l, nz(1, 9), l, nz(1, 9)),
                          '(sqrt(%s)+sqrt(%s))(sqrt(%s)-sqrt(%s))' % (l, m, l, m)])


def g_letter_conj():
    l = random.choice(LETS)
    top = random.choice([str(nz(-9, 9)), 'sqrt(%s)' % l, '%d+sqrt(%s)' % (nz(-9, 9), l)])
    bot = random.choice(['sqrt(%s)%+d' % (l, nz(-9, 9)), '%d-sqrt(%s)' % (nz(1, 9), l),
                         '%dsqrt(%s)+%d' % (nz(2, 5), l, nz(1, 9))])
    return '(' + top + ')/(' + bot + ')'


def g_nested():
    return random.choice(['sqrt(%d+%dsqrt(%d))' % (random.randint(3, 20), nz(1, 6), random.choice(PR)),
                          'sqrt(x+%d)*sqrt(x+%d)' % ((random.randint(1, 9),) * 2),
                          'sqrt(%s+1)^2' % random.choice(LETS)])


def g_mixed():
    return join([g_single_div(), g_combo()])


def g_cancel():
    l, m = random.sample(LETS, 2)
    k = nz(1, 9)
    return random.choice(['(%s-%d)/(sqrt(%s)-%d)' % (l, k * k, l, k), '(%d-%s)/(%d+sqrt(%s))' % (k * k, l, k, l),
                          '(%s-%s)/(sqrt(%s)-sqrt(%s))' % (l, m, l, m), '(%s^2-%s^2)/(%s+%s)' % (l, m, l, m),
                          '(%s^2-%d)/(%s+%d)' % (l, k * k, l, k), '(%d%s+%d)/(sqrt(%s+1))^2' % (k, l, k, l),
                          '(%s-%d)/(sqrt(%s)+%d)' % (l, k * k, l, k)])


# ---- sums under roots: what the terms share, squares of sums, a+b*sqrt(n)
def ptext(P):
    # {((letter, power), ...): number} as text, biggest power first
    o = ''
    for k in sorted(P, key=lambda k: (-sum(e for _, e in k), k)):
        c = P[k]
        if c == 0:
            continue
        m = ''.join(l + ('^%d' % e if e > 1 else '') for l, e in k)
        t = (str(abs(c)) if abs(c) != 1 or not m else '') + m
        o += ('-' if c < 0 else '+') + t
    return o[1:] if o.startswith('+') else (o or '0')


def pmul(A, B):
    C = {}
    for a in A:
        for b in B:
            d = dict(a)
            for l, e in b:
                d[l] = d.get(l, 0) + e
            k = tuple(sorted((l, e) for l, e in d.items() if e))
            C[k] = C.get(k, 0) + A[a] * B[b]
    return dict((k, v) for k, v in C.items() if v)


def rpoly(ls, n, lo=-5, hi=5):
    P = {}
    while len(P) < n:
        k = tuple(sorted((l, e) for l, e in ((l, random.randint(0, 2)) for l in ls) if e))
        P[k] = nz(lo, hi)
    return P


def rmono(ls, top=3):
    return {tuple(sorted((l, e) for l, e in ((l, random.randint(0, top)) for l in ls) if e)): 1}


def g_share():
    ls = random.sample(LETS, random.randint(1, 2))
    P = rpoly(ls, random.randint(2, 3), 1 if random.random() < 0.5 else -5)
    c = random.choice([1, 2, 3, 4, 8, 9, 12, 18, 25, 27, 50, 72, 98, 1009 ** 2, 2 * 1013 ** 2])
    Q = pmul(pmul({(): c}, rmono(ls)), P)
    q = 'sqrt(%s)' % ptext(Q)
    r = random.random()
    if r < 0.4:
        return q
    k = random.choice([2, 3, 4, 5, 8, 9, 12])
    Q2 = ptext(pmul({(): k}, pmul(rmono(ls, 2), P)))
    return random.choice(['%s*sqrt(%s)', '%s/sqrt(%s)', '%s+sqrt(%s)', '%s-%d*sqrt(%s)' % ('%s', nz(1, 4), '%s')]) % (q, Q2)


def g_square():
    ls = random.sample(LETS, random.randint(1, 2))
    p = rpoly(ls, random.randint(2, 3), 1 if random.random() < 0.5 else -5)
    k = random.choice([1, 1, 1, 2, 3, 4, 5, 9, 12])
    Q = pmul(pmul({(): k}, pmul(rmono(ls, 1), rmono(ls, 1))), pmul(p, p))
    q = 'sqrt(%s)' % ptext(Q)
    return random.choice([q, q, q, '%s+%s' % (q, ptext(p)), '%d/%s' % (nz(1, 9), q), '%s*sqrt(%d)' % (q, random.choice(PR)),
                          'sqrt((%s)^2)' % ptext(p)])


def g_denest():
    x = random.randint(1, 30)
    y = random.randint(1, 30)
    sg = random.choice('+-')
    r = random.random()
    if r < 0.5:
        q = 'sqrt(%d%s2sqrt(%d))' % (x + y, sg, x * y)
    elif r < 0.7:
        q = 'sqrt(%d%s%dsqrt(%d))' % (random.randint(1, 40), sg, random.randint(1, 9), random.choice(PR))
    elif r < 0.85:
        q = 'sqrt((%d%ssqrt(%d))/%d)' % (x + y, sg, 4 * x * y, random.choice([2, 3, 4, 8, 9]))
    else:
        q = '%d/sqrt(%d%s2sqrt(%d))' % (nz(1, 9), x + y, sg, x * y)
    return q


FAM = [
    ('share', g_share, 8),
    ('square of a sum', g_square, 6),
    ('denest', g_denest, 5),
    ('cancel', g_cancel, 6),
    ('combine', g_combo, 15),
    ('product', g_product, 15),
    ('one-term bottom', g_single_div, 15),
    ('conjugate', g_conj, 15),
    ('three-root bottom', g_three, 6),
    ('letters', g_letters, 15),
    ('letter conjugate', g_letter_conj, 8),
    ('root of a sum', g_nested, 4),
    ('mixed', g_mixed, 7),
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


# ---------------------------------------------------------- checking
def init():
    global sp, mp, SYM
    import sympy as sp
    import mpmath as mp
    SYM = dict((c, sp.Symbol(c, positive=True)) for c in 'abcdefghijklmnopqrstuvwxyz')
    # radsimp.py borrows rad.py's helpers, as on the calculator
    import os
    S = {}
    exec(open(SRC).read(), S)
    G = {}
    r = open(os.path.join(os.path.dirname(SRC), 'rad.py')).read()
    exec(r[:r.index("print('Root equations")], G)
    globals()['go'] = lambda q: S['go'](q, G)
    globals()['wrap'] = G['wrap']
    globals()['W'] = G['W']


def ref_parse(t):
    t = re.sub(r'\|([^|]*)\|', r'A(\1)', t)
    t = t.replace('sqrt(', 'S(')
    t = re.sub(r'(\d+)\.(\d+)', lambda m: '(%d/%d)' % (int(m.group(1) + m.group(2)), 10 ** len(m.group(2))), t)
    t = t.replace('^', '**')
    t = re.sub(r'(?<=[\da-z)])(?=[a-zSA(])', '*', t)
    loc = dict(SYM)
    loc['S'] = sp.sqrt
    loc['A'] = sp.Abs
    return sp.sympify(t, locals=loc)


def bottoms(a):
    # the text after every / at the top level of each term
    o = []
    i = 0
    while i < len(a):
        if a[i] == '/':
            j = i + 1
            if j < len(a) and a[j] == '(':
                d = 0
                while True:
                    d += {'(': 1, ')': -1}.get(a[j], 0)
                    j += 1
                    if d == 0:
                        break
            else:
                while j < len(a) and (a[j].isalnum() or a[j] == '^'):
                    j += 1
            o.append(a[i + 1:j])
            i = j
        else:
            i += 1
    return o


def radicands(a):
    o = []
    i = a.find('sqrt(')
    while i >= 0:
        j = i + 5
        d = 1
        while d:
            d += {'(': 1, ')': -1}.get(a[j], 0)
            j += 1
        o.append(a[i + 5:j - 1])
        i = a.find('sqrt(', i + 1)
    return o


def topterms(a):
    # the root parts of the top-level terms of the top (inside a leading
    # bracket when the answer is (...)/bottom)
    if a.startswith('(') and ')/' in a:
        d = 0
        for j, ch in enumerate(a):
            d += {'(': 1, ')': -1}.get(ch, 0)
            if d == 0:
                break
        a = a[1:j]
    ts = []
    d = 0
    bar = 0
    cur = ''
    for ch in a:
        if ch in '+-' and d == 0 and not bar and cur:
            ts.append(cur)
            cur = ''
        d += {'(': 1, ')': -1}.get(ch, 0)
        bar ^= ch == '|'
        cur += ch
    ts.append(cur)
    return ts


def sqfree(n):
    f = 2
    while f * f <= n:
        if n % (f * f) == 0:
            return False
        f += 1
    return True


def check(i):
    name, q = gen(i)
    errs = []
    try:
        out = go(q)
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    for ln in out:
        for w in wrap(ln):
            if len(w) > W:
                errs.append('wide')
    try:
        ref = ref_parse(q)
    except Exception as e:
        return name, q, out, ['REFERENCE PARSE FAILED ' + repr(e)]
    a = [l for l in out if l.startswith('Ans: ')]
    if not a:
        # only a real division by zero may be refused
        if not (ref.has(sp.zoo) or ref.has(sp.nan)):
            errs.append('no answer')
        return name, q, out, errs
    a = a[0][5:]
    try:
        got = ref_parse(a)
    except Exception as e:
        return name, q, out, errs + ['answer does not parse ' + repr(e)]
    mp.mp.dps = 60
    letters = sorted(set(re.findall(r'[a-z]', q.replace('sqrt', ''))))
    for _ in range(4):
        pt = dict((SYM[l], sp.Rational(random.randint(1, 400), random.randint(1, 37))) for l in letters)
        r1 = sp.N(ref.subs(pt), 55)
        r2 = sp.N(got.subs(pt), 55)
        if r1.has(sp.zoo) or r1.has(sp.nan) or r2.has(sp.zoo) or r2.has(sp.nan):
            # undefined at this point (a conjugate that is 0 there): try another
            continue
        try:
            bad = abs(r1 - r2) > sp.Float('1e-40', 55) * (1 + abs(r1))
        except TypeError:
            bad = True
        if bad:
            errs.append('wrong value %s vs %s' % (sp.N(r2, 12), sp.N(r1, 12)))
            break
    for b in bottoms(a):
        if 'sqrt' in b:
            errs.append('root in a bottom: ' + b)
    for r in radicands(a):
        m = re.fullmatch(r'(\d*)([a-z]*)', r)
        if m:
            if m.group(1) and (not sqfree(int(m.group(1))) or int(m.group(1)) < 2):
                errs.append('not simplified: sqrt(' + r + ')')
            if len(set(m.group(2))) != len(m.group(2)):
                errs.append('letter twice: sqrt(' + r + ')')
        elif '^' in r and '+' not in r and '-' not in r:
            errs.append('power under a root: sqrt(' + r + ')')
        elif 'sqrt' not in r and '/' not in r and '(' not in r:
            # a sum: no square number or letter^2 all terms share, and
            # not the square of a sum (that is written out, or |p|)
            P = sp.Poly(ref_parse(r), *([SYM[l] for l in sorted(set(re.findall('[a-z]', r)))] or [SYM['x']]))
            c, F = sp.factor_list(P.as_expr())
            if all(e % 2 == 0 for _, e in F) and c > 0 and sp.sqrt(c).is_rational:
                errs.append('square under a root: sqrt(' + r + ')')
            g = P.terms_gcd()[0]
            if any(e > 1 for e in g):
                errs.append('letter^2 left under a root: sqrt(' + r + ')')
            if not sqfree(int(abs(P.content()))):
                errs.append('square number left under a root: sqrt(' + r + ')')
        elif 'sqrt' in r and '(' not in r.replace('sqrt(', ''):
            dn = sp.sqrtdenest(sp.sqrt(ref_parse(r)))
            if dn != sp.sqrt(ref_parse(r)) and all(p.exp.q <= 2 for p in dn.atoms(sp.Pow) if p.exp.is_Rational):
                errs.append('could denest: sqrt(' + r + ')')
    seen = []
    for t in topterms(a):
        rs = radicands(t)
        u = re.sub(r'^[-+]?[\d/]*', '', t)
        for r in rs:
            u = u.replace('sqrt(' + r + ')', '', 1)
        ab = re.findall(r'\|[^|]*\|', u)
        for x in ab:
            u = u.replace(x, '', 1)
        k = (tuple(sorted(rs)), tuple(sorted(ab)), tuple(sorted(re.findall(r'[a-z](?:\^\d+)?', u))))
        if k in seen:
            errs.append('like terms not added: ' + a)
            break
        seen.append(k)
    return name, q, out, errs


if __name__ == '__main__':
    with Pool(2, initializer=init) as P:
        st = {}
        bad = []
        for k, (name, q, out, errs) in enumerate(P.imap_unordered(check, range(N), chunksize=20)):
            s = st.setdefault(name, [0, 0])
            s[0] += 1
            if errs:
                s[1] += 1
                bad.append((name, q, out, errs))
                print('BAD', name, q, out, errs, flush=True)
            if (k + 1) % 5000 == 0:
                print(k + 1, 'done,', len(bad), 'bad', flush=True)
        for name in st:
            print('%-18s %6d checked %5d bad' % (name, st[name][0], st[name][1]))
        print(N, 'questions,', len(bad), 'bad')
