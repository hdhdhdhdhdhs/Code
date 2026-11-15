# algebra/'s equations whose bottoms share a factor (1/(x+2)+1/(x^2-4)),
# against sympy: Ans is every real answer that makes no bottom 0, and
# Fails is exactly what fails by hand over the lowest common bottom
# (so x=-2 in (4x-1)/(x+2)-(x+1)/(x-2)=(x^2-4x+24)/(x^2-4), not x=2 too)
#
#   python3 alcd.py [count] [seed]     (run from tests/, sympy on PYTHONPATH)
import sys, random, re
from functools import reduce
sys.path.insert(0, '../algebra')
import sympy as sp
from algcore import go, st
x = sp.Symbol('x')
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
def nz(a, b):
    while True:
        r = random.randint(a, b)
        if r: return r
def lin():
    return '%sx%+d' % (random.choice(['', '', '2', '3']), nz(-6, 6))
bad = 0
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
for n in range(N):
    a = random.randint(1, 5); b = nz(-5, 5)
    p, q = lin(), lin()
    forms = [
        '(%s)/(x+%d)-(%s)/(x-%d)=(%s)/(x^2-%d)' % (lin(), a, lin(), a, 'x^2' + '%+dx%+d' % (nz(-9, 9), nz(-30, 30)), a * a),
        '%d/(x-%d)+%d/(x+%d)=%d/(x^2-%d)' % (nz(-5, 5), a, nz(-5, 5), a, nz(-9, 9), a * a),
        '%d/(%s)+%d/(%s)^2=%d' % (nz(-5, 5), p, nz(-5, 5), p, nz(-3, 3)),
        'x/(%s)=%d/(%s)+%d' % (p, nz(-5, 5), p, nz(-3, 3)),
        '(%s)/(x^2-%dx)=%d/x+%d/(x-%d)' % (lin(), a, nz(-5, 5), nz(-5, 5), a),
        '%d/(x^2-%d)+%d/(x-%d)=%d/(x+%d)' % (nz(-9, 9), a * a, nz(-5, 5), a, nz(-5, 5), a),
    ]
    s = random.choice(forms)
    try:
        out = [st(l) for l in go(s)]
    except Exception as e:
        out = ['Err: %s' % e]
    L, R = s.split('=')
    P = lambda t: sp.sympify(re.sub(r'(\d)x', r'\1*x', t.replace('^', '**')))
    e = P(L) - P(R)
    num, den = sp.fraction(sp.together(e))
    bots = [p.base for p in sp.preorder_traversal(e) if isinstance(p, sp.Pow) and p.exp.is_number and p.exp < 0]
    sols = set()
    if sp.simplify(e) == 0:
        continue
    for r in sp.Poly(num, x).real_roots() if num.has(x) else []:
        if all(abs(sp.N(bb.subs(x, r))) > 1e-12 for bb in bots):
            sols.add(round(float(r), 6))
    A = [l for l in out if l.startswith('Ans: ')]
    got = set()
    if A and 'no solution' not in A[0]:
        for t in A[0][5:].split(', '):
            t = t.split('=')[-1].split('~')[-1]
            got.add(round(float(sp.N(sp.sympify(re.sub(r'(?<=[\d)])(?=sqrt)', '*', t)))), 6))
    F = [l for l in out if l.startswith('Fails: ')]
    fails = []
    if F:
        for t in F[0][7:].split(', '):
            t = t.split('=')[-1].split('~')[-1]
            fails.append(float(sp.N(sp.sympify(re.sub(r'(?<=[\d)])(?=sqrt)', '*', t)))))
    ok = len(got) == len(sols) and all(any(abs(g - s2) < 1e-4 for s2 in sols) for g in got)
    # every fail makes a bottom 0
    ok = ok and all(any(abs(sp.N(bb.subs(x, f))) < 1e-6 for bb in bots) for f in fails)
    # and what fails is what fails by hand: over the lowest common bottom
    LCD = reduce(sp.lcm, [sp.factor(bb) for bb in bots], sp.Integer(1))
    Np = sp.cancel(sp.together(e * LCD))
    hf = set()
    if Np.has(x):
        for r in sp.Poly(sp.numer(Np), x).real_roots():
            if any(abs(sp.N(bb.subs(x, r))) < 1e-12 for bb in bots):
                hf.add(round(float(r), 6))
    if set(round(f, 6) for f in fails) != hf:
        ok = False
    if not ok:
        bad += 1
        print('BAD', s, out, sorted(sols))
print(N, 'equations,', bad, 'bad')
