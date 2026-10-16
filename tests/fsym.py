# fac.py against sympy's factor_list: random polynomials, some built from
# random pieces, compared factor by factor (with powers).
# PYTHONPATH must reach sympy:  python3 fsym.py ../fac.py [count]
import sys, random, re
import sympy as S
src = open(sys.argv[1]).read()
exec(src[:src.index("print('Factor")])
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
X = S.Symbol('x')
random.seed(11)
bad = 0
for n in range(N):
    e = 1
    for _ in range(random.randint(1, 4)):
        d = random.randint(1, 4)
        e *= S.Poly([random.randint(1, 4)] + [random.randint(-6, 6) for _ in range(d)], X).as_expr() ** random.choice([1, 1, 1, 2])
    p = S.Poly(S.expand(e), X)
    if p.degree() > 12 or p.degree() < 1:
        continue
    q = str(p.as_expr()).replace('**', '^').replace('*', '')
    out = fac(q)
    want = sorted((str(S.Poly(f, X).all_coeffs()), k) for f, k in S.factor_list(p.as_expr())[1] if S.Poly(f, X).degree() > 0)
    a = [l for l in out if l.startswith('Ans:') or l.startswith('Prime')][0]
    if a.startswith('Prime'):
        got = want if len(want) == 1 and want[0][1] == 1 else [('prime?', 0)]
    else:
        got = []
        for f, k in re.findall(r'\(([^()]*x[^()]*)\)(?:\^(\d+))?', a[4:]) + ([] if '(' in a else [(a[4:], '')]):
            pf = S.Poly(S.sympify(re.sub(r'(\d)x', r'\1*x', f).replace('^', '**')), X)
            got.append((str(pf.all_coeffs()), int(k or 1)))
        head = a[4:].split('(')[0] if '(' in a[4:] else ''
        m = re.search(r'x(\^(\d+))?$', head)
        if m:
            got.append((str([1, 0]), int(m.group(2) or 1)))
        got.sort()
    if got != want:
        bad += 1
        if bad < 10:
            print(q, out, want, got)
print(N, 'checked against sympy,', bad, 'bad')
