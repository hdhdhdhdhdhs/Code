# fac.py with two letters: products of random same-power pieces in x and y,
# times a random monomial. The Ans line must multiply back to the question
# and hold as many pieces as sympy's factor_list.
#   PYTHONPATH must reach sympy:  python3 fxy.py ../fac.py [count]
import sys, random, re
import sympy as S
src = open(sys.argv[1]).read()
exec(src[:src.index("print('Factor")])
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
x, y = S.symbols('x y')
random.seed(5)


def sx(t):
    t = re.sub(r'(\d|\)|x|y)(?=[xy(])', r'\1*', t)
    return S.sympify(t.replace('^', '**'))


bad = 0
for n in range(N):
    e = random.choice([1, 2, 3, -1, 5, 6]) * x ** random.choice([0, 0, 1, 2]) * y ** random.choice([0, 0, 1, 2])
    for _ in range(random.randint(1, 3)):
        d = random.randint(1, 3)
        f = sum(random.randint(-6, 6) * x ** i * y ** (d - i) for i in range(d)) + random.randint(1, 4) * x ** d
        e *= f
    P = S.expand(e)
    if P == 0 or S.Poly(P, x, y).total_degree() > 12:
        continue
    q = str(P).replace('**', '^').replace('*', '')
    out = fac(q)
    err = []
    a = [l for l in out if l.startswith('Ans:') or l.startswith('Prime') or l.startswith('Err')][0]
    want = sum(k for f, k in S.factor_list(P)[1])
    if a.startswith('Ans:'):
        A = sx(a[4:])
        if S.expand(A - P) != 0:
            err.append('Ans wrong')
        got = sum(k for f, k in S.factor_list(A)[1])
        # every printed piece must itself be finished
        for f, k in re.findall(r'\(([^()]*)\)(?:\^(\d+))?', a[4:]):
            if len(S.factor_list(sx(f))[1]) > 1 or S.factor_list(sx(f))[1][0][1] > 1:
                err.append('piece not done ' + f)
    elif a.startswith('Prime'):
        if want != 1:
            err.append('not prime')
    else:
        err.append(a)
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                err.append('wide')
    if err:
        bad += 1
        if bad < 8:
            print(q, out, err)
print(N, 'two-letter polynomials,', bad, 'bad')
