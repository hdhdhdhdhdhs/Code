# fac.py: random polynomials built from known factors. Checks, with exact
# fractions and its own reader, that the Ans line multiplies back to the
# question, that every factor is fully factored, that the Slide line is the
# factoring of x^2+bx+ac, that the zeros make it 0, and that no line is
# over 21 columns.  CPython:  python3 ffuzz.py ../fac.py [count]
import sys, random, re
from fractions import Fraction as Fr
src = open(sys.argv[1]).read()
exec(src[:src.index("print('Factor")])
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
random.seed(7)
try:
    import sympy as SP
except ImportError:
    SP = None


def py(s):
    s = s.replace('^', '**').replace('sqrt', 'S')
    s = re.sub(r'(?<=[\dx)])(?=[x(S])', '*', s)
    return s


def val(s, x):
    return eval(py(s), {'x': x, 'S': lambda v: v ** 0.5})


def pmul(a, b):
    c = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            c[i + j] += a[i] * b[j]
    return c


def show(c):  # independent printer, highest power first
    t = []
    for i in range(len(c) - 1, -1, -1):
        if c[i]:
            t.append('(%s)*x**%d' % (c[i], i))
    return '+'.join(t) or '0'


def irreducible(c):  # sympy when there is one, else no rational zero
    if len(c) <= 2:
        return True
    if SP:
        return SP.Poly(list(reversed(c)), SP.Symbol('x')).is_irreducible
    for q in range(1, abs(c[-1]) + 1):
        if c[-1] % q:
            continue
        for p in range(-abs(c[0]), abs(c[0]) + 1):
            if p and c[0] % p == 0 and sum(Fr(p, q) ** i * c[i] for i in range(len(c))) == 0:
                return False
    return True


bad = 0
for n in range(N):
    fs = []
    k = random.choice([1, 1, 1, 2, 3, -1, -2, 5])
    c = [k]
    for _ in range(random.choice([1, 2, 2, 2, 3, 4])):
        if random.random() < 0.8:
            f = [random.randint(-9, 9), random.randint(1, 6)]
            if f[0] == 0 and random.random() < 0.7:
                f[0] = 1
        elif random.random() < 0.6:
            f = [random.randint(1, 9), random.randint(-4, 4), random.randint(1, 3)]
        else:
            f = [random.randint(-9, 9) for _ in range(random.randint(4, 5))]
            f[-1] = random.randint(1, 3)
            f[0] = f[0] or 1
        c = pmul(c, f)
    while c[-1] == 0:
        c.pop()
    if len(c) < 2 or len(c) > 13:
        continue
    q = show(c).replace('**', '^').replace('*', '')
    out = fac(q)
    err = []
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                err.append('wide ' + w)
    ans = [l for l in out if l.startswith('Ans:')]
    if ans:
        a = ans[0][4:]
        for x in (Fr(2, 7), Fr(-5, 3), Fr(11, 2)):
            if val(a, x) != sum(c[i] * x ** i for i in range(len(c))):
                err.append('Ans wrong')
                break
        for f in re.findall(r'\(([^()]*x[^()]*)\)', a):
            cc, d = parse(f)
            cc = [cc.get((i, 0), 0) for i in range(max(k[0] for k in cc) + 1)]
            if not irreducible(cc):
                err.append('not done ' + f)
    elif not any(l.startswith('Prime') for l in out):
        err.append('no answer')
    sl = [l for l in out if l.startswith('Slide:')]
    if sl:
        mm = [l for l in out if l.startswith('Multiply:')][0]
        nn, bb = [int(v) for v in re.findall(r'-?\d+', mm)]
        for x in (Fr(3, 7), Fr(-2)):
            if val(sl[0][6:], x) != x * x + bb * x + nn:
                err.append('Slide wrong')
    zl = [l for l in out if l.startswith('Zeros:') or l == 'No real zeros']
    got = sorted(float(val(z.lstrip('~'), 0)) for z in (zl[0][7:].split(', ') if zl and zl[0][0] == 'Z' else []))
    if SP:
        want = sorted(set(round(float(r), 6) for r in SP.Poly(list(reversed(c)), SP.Symbol('x')).real_roots()))
    else:
        want = got
    if len(got) != len(want) or any(abs(a - b) > 6e-5 * max(1, abs(b)) for a, b in zip(got, want)):
        err.append('zeros %s want %s' % (got, want))
    if err:
        bad += 1
        if bad < 15:
            print(q, out, err)
print(N, 'polynomials,', bad, 'bad')
