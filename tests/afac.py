# algebra/'s Fac line (a polynomial, or a whole number, factored) against
# sympy: it multiplies out to the answer, and it is factored all the way
# (as many factors, and the same ones, as sympy's factor_list finds)
#
#   python3 afac.py [count] [seed]     (run from tests/, sympy on PYTHONPATH)
import sys, random, re
sys.path.insert(0, '../algebra')
import sympy as sp
from algcore import go, st

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
S = dict((c, sp.Symbol(c)) for c in 'abcdefghijklmnopqrstuvwxyz')


def nz(a, b):
    while True:
        r = random.randint(a, b)
        if r:
            return r


def factor():
    v = random.sample('xyab', random.choice([1, 1, 1, 2]))
    r = random.random()
    x = v[0]
    if len(v) == 1:
        if r < 0.5:
            return '(%d%s%+d)' % (random.choice([1, 1, 2, 3]), x, nz(-9, 9))
        if r < 0.7:
            return '(%s^2%+d)' % (x, random.choice([1, 2, 3, 4, 5, -2, -3]))
        if r < 0.85:
            return '(%s^2%+d%s%+d)' % (x, nz(-4, 4), x, random.choice([1, 2, 3, 5, 7]))
        return x
    y = v[1]
    if r < 0.6:
        return '(%d%s%+d%s)' % (random.choice([1, 1, 2, 3]), x, nz(-5, 5), y)
    if r < 0.8:
        return '(%s^2%+d%s%s%+d%s^2)' % (x, nz(-3, 3), x, y, random.choice([1, 2, 3, 5]), y)
    return x + y


def text(e):
    t = str(sp.expand(e)).replace('**', '^').replace(' ', '')
    return t.replace('*', '')


def parse(t):
    t = t.replace('^', '**')
    t = re.sub(r'(?<=[\da-z)])(?=[a-z(])', '*', t)
    return sp.sympify(t, locals=S)


bad = 0
seen = 0
for n in range(N):
    if random.random() < 0.1:
        q = str(random.randint(2, 10 ** random.randint(2, 7)))
    else:
        k = random.randint(1, 4)
        q = '*'.join(factor() for _ in range(k))
        if random.random() < 0.3:
            q = '%d*' % nz(-12, 12) + q
        q = text(parse(q))
    try:
        out = [st(l) for l in go(q)]
    except Exception as e:
        print('ERR', q, e)
        bad += 1
        continue
    A = [l[5:] for l in out if l[:5] == 'Ans: '][0]
    F = [l[5:] for l in out if l[:5] == 'Fac: ']
    E = parse(A)
    c, fl = sp.factor_list(E)
    # how many pieces sympy finds (a number other than +-1 is one)
    want = sum(m for f, m in fl if f.is_number is False) + (abs(c) != 1 if c.is_Integer else 0)
    if E.is_Integer:
        want = sum(sp.factorint(abs(int(E))).values())
    if not F:
        # one term (a number times letters) is factored already
        if want > 1 and not (E.is_Integer and abs(E) < 2) and len(sp.Add.make_args(sp.expand(E))) > 1:
            print('NO FAC', q, out)
            bad += 1
        continue
    seen += 1
    f = F[0]
    if E.is_Integer:
        got = sp.Mul(*[sp.Integer(int(b)) ** int(e) for b, e in re.findall(r'(\d+)(?:\^(\d+))?', f.replace('^', '^')) for e in [e or 1]])
        got *= -1 if f.startswith('-') else 1
        if got != E or any(not sp.isprime(int(b)) for b, _ in re.findall(r'(\d+)(?:\^(\d+))?', f)):
            print('BAD NUMBER', q, out)
            bad += 1
        continue
    G = parse(f.replace('*', '') if '(' in f else f)
    if sp.expand(G - E) != 0:
        print('BAD VALUE', q, out)
        bad += 1
        continue
    # each bracket, and the number in front, as sympy finds them
    pieces = re.findall(r'\(([^()]*)\)(?:\^(\d+))?', f)
    gotf = [(sp.expand(parse(p)), int(e or 1)) for p, e in pieces]
    wantf = []
    for g, m in fl:
        g = sp.expand(g)
        if len(sp.Add.make_args(g)) > 1:
            if sp.Poly(g, *sorted(g.free_symbols, key=str)).LC() < 0:
                g = -g
            wantf.append((g, m))
    wantf.sort(key=str)
    gf = sorted([(sp.expand(g if sp.Poly(g, *sorted(g.free_symbols, key=str)).LC() > 0 else -g), m) for g, m in gotf],
                key=str)
    if gf != wantf:
        print('NOT FULLY', q, out, wantf)
        bad += 1
print(N, 'polynomials and numbers,', seen, 'with Fac,', bad, 'bad')
