# algebra/'s NPV and Restr lines when simplifying with roots and two or
# more letters, against sympy and mpmath, at numbers put in for the
# letters:
#   NPV    every point where a bottom typed is 0, with what is under its
#          roots >= 0, meets some NPV piece (one of the answer's bottoms:
#          an NPV or Ans NPV piece); and every point an NPV piece names
#          makes a bottom typed 0 (Ans NPV: one of the answer's)
#   Restr  where every piece holds, what is under each root typed is
#          >= 0; and each piece is a letter >= 0 (simplifying took it)
#          or what is under a root typed, >= 0
#
#   python3 anpvm.py [count] [seed]    (run from tests/, sympy on PYTHONPATH)
import sys, re, random
from multiprocessing import Pool

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1


def nz(a, b):
    while True:
        r = random.randint(a, b)
        if r:
            return r


def two():
    return random.sample('abxyz', 2)


def lin2(u, v):
    a = random.choice([1, 1, 1, 2, 3])
    b = random.choice([1, 1, 1, -1, -1, 2, -2])
    t = ('%d%s' % (a, u) if a > 1 else u) + ('%+d%s' % (b, v) if abs(b) > 1 else ('+' if b > 0 else '-') + v)
    if random.random() < 0.4:
        t += '%+d' % nz(-6, 6)
    return t


def g_multi():
    u, v = two()
    w = random.choice([c for c in 'abxyz' if c not in (u, v)])
    k = random.randint(1, 4)
    r = random.randrange(16)
    return [
        lambda: 'sqrt(%s)/(sqrt(%s)+sqrt(%s))' % (u, u, v),
        lambda: '(%s-%s)/(sqrt(%s)-sqrt(%s))' % (u, v, u, v),
        lambda: '%d/(sqrt(%s)%+d)' % (nz(-9, 9), lin2(u, v), nz(-5, 5)),
        lambda: '%s/(%s*sqrt(%s))' % (u, v, lin2(u, v)),
        lambda: 'sqrt(%s%s)/(%s*sqrt(%s))' % (u, v, u, v),
        lambda: '(sqrt(%s)+sqrt(%s))/(sqrt(%s)-sqrt(%s))' % (u, v, u, v),
        lambda: '1/(sqrt(%s)+%d)+1/(%s-%s)' % (u, k, v, u),
        lambda: 'sqrt(%s)/(%s)' % (lin2(u, v), random.choice([lin2(u, v), '%s^2-%s^2' % (u, v), '%s%s-%d' % (u, v, k)])),
        lambda: '1/sqrt(%s)' % lin2(u, v),
        lambda: 'sqrt(%s)/(%s*%s-%s^2)' % (u, u, v, v),
        lambda: '%d/(sqrt(%s)-sqrt(%s))' % (nz(-5, 5), lin2(u, v), lin2(v, u)),
        lambda: '(sqrt(%s)-%d)/(%s-%d)' % (u, k, u, k * k),
        lambda: 'sqrt(%s^2*%s)/(%s*%s)' % (u, v, u, v),
        lambda: '1/(sqrt(%s)+sqrt(%s)+sqrt(%s))' % (u, v, w),
        lambda: '%s/(sqrt(%s^2-%s^2))' % (w, u, v),
        lambda: 'sqrt(%s)/(%s+sqrt(%s%s))' % (u, v, u, v),
    ][r]()


def gen(n):
    random.seed(SEED * 1000003 + n)
    if random.random() < 0.6:
        return 'multi', g_multi()
    # the root checker's questions with two or more letters
    for i in range(200):
        name, q = SG(n * 211 + i)
        if len(set(re.findall('[a-z]', q.replace('sqrt', '')))) > 1:
            return 'sfuzz ' + name, q
    return 'multi', g_multi()


SG = None


def init():
    global sp, mp, SG, SYM
    import sympy as sp
    import mpmath as mp
    sys.path.insert(0, '../algebra')
    import algcore
    globals()['go'] = algcore.go
    globals()['st'] = algcore.st
    SYM = dict((c, sp.Symbol(c)) for c in 'abcdefghijklmnopqrstuvwxyz')

    class S(sp.Function):
        nargs = 1
    globals()['S'] = S
    sys.argv = ['x', '../radsimp.py', '1', str(SEED)]
    b = {}
    exec(open('sfuzz.py').read().split('# ---------------------------------------------------------- checking')[0], b)
    SG = b['gen']


def parse(t):
    # the program's text (or a question) as sympy, S for a root
    t = t.replace(' ', '').replace('sqrt(', 'S(')
    t = re.sub(r'~(-?[\d.]+(e-?\d+)?)', r'(\1)', t)
    t = re.sub(r'(\d+)\.(\d+)', lambda m: '(%d/%d)' % (int(m.group(1) + m.group(2)), 10 ** len(m.group(2))), t)
    t = t.replace('^', '**')
    t = re.sub(r'(?<=[\da-z)])(?=[a-zS(])', '*', t)
    loc = dict(SYM)
    loc['S'] = S
    return sp.sympify(t, locals=loc, evaluate=False)


def ev(e, p):
    # e at the point p, in complex numbers (S of below 0 is imaginary)
    f = e.xreplace(dict((SYM[k], v if isinstance(v, sp.Float) else sp.Rational(v)) for k, v in p.items()))
    f = f.replace(S, lambda a: sp.sqrt(a))
    return complex(sp.N(f, 40))


def rads(e):
    return [a.args[0] for a in sp.preorder_traversal(e) if isinstance(a, S)]


def bottoms(e):
    return [p.base for p in sp.preorder_traversal(e) if isinstance(p, sp.Pow) and p.exp.is_number and p.exp < 0]


def zeros(b, v, others):
    # real values of letter v making b 0 (others put in), where what is
    # under b's roots is >= 0
    X = SYM[v]
    g = b.xreplace(dict((SYM[k], sp.Rational(x)) for k, x in others.items()))
    if not g.has(X):
        return []
    ys = []
    pr = []
    h = g
    while True:
        at = [a for a in h.atoms(S) if not a.args[0].atoms(S)]
        if not at:
            break
        for a in at:
            y = sp.Symbol('y%d' % len(ys))
            ys.append(y)
            pr.append(a.args[0])
            h = h.xreplace({a: y})
            pr = [q.xreplace({a: y}) for q in pr]
    G = sp.numer(sp.together(sp.expand(sp.together(h))))
    for i in range(len(ys) - 1, -1, -1):
        t = sp.together(pr[i])
        G = sp.expand(sp.resultant(sp.Poly(G, ys[i]), sp.Poly(sp.denom(t) * ys[i] ** 2 - sp.numer(t), ys[i])).as_expr())
    if G == 0 or not G.has(X):
        return []
    out = []
    for rr in sorted(set(sp.real_roots(sp.Poly(G, X).sqf_part()))):
        x = sp.N(rr, 60)
        ok = True
        for r in rads(g):
            try:
                c = complex(sp.N(r.xreplace({X: x}).replace(S, lambda a: sp.sqrt(a)), 40))
            except (ZeroDivisionError, TypeError):
                ok = False
                break
            if abs(c.imag) > 1e-20 or c.real < -1e-20:
                ok = False
        if not ok:
            continue
        try:
            val = complex(sp.N(g.xreplace({X: x}).replace(S, lambda a: sp.sqrt(a)), 40))
        except (ZeroDivisionError, TypeError):
            continue
        if abs(val) < 1e-25:
            out.append(x)
    return out


def rnd():
    return sp.Rational(random.randint(-12, 12), random.choice([1, 2]))


def npvconds(line):
    # each NPV piece as an expression that is 0 where it is not allowed
    c = []
    for g in line.split('; '):
        if g == 'none':
            continue
        lhs, rhs = g.split('!=', 1)
        if ',' in lhs:
            c += [SYM[v] for v in lhs.split(',')]
            continue
        for val in rhs.split(','):
            c.append(parse(lhs) - parse(val))
    return c


def held(e, p):
    try:
        z = ev(e, p)
    except (ZeroDivisionError, TypeError):
        return True
    return abs(z) < 1e-12


def piece(u):
    # one Restr piece as a test at a point
    if ' or ' in u:
        ts = [piece(v) for v in u.split(' or ')]
        return lambda p: any(t(p) for t in ts)
    m = re.fullmatch(r'(.*)<=(.*)<=(.*)', u)
    if m:
        lo, e, hi = parse(m.group(1)), parse(m.group(2)), parse(m.group(3))
        return lambda p: ev(lo, p).real - 1e-9 <= ev(e, p).real <= ev(hi, p).real + 1e-9
    for op in ('>=', '<=', '>', '='):
        if op in u:
            a, b = u.split(op, 1)
            A, B = parse(a), parse(b)
            f = {'>=': lambda d: d >= -1e-9, '<=': lambda d: d <= 1e-9, '>': lambda d: d > -1e-9,
                 '=': lambda d: abs(d) < 1e-9}[op]
            return lambda p, A=A, B=B, f=f: f(ev(A, p).real - ev(B, p).real)
    raise ValueError('piece ' + u)


def check(n):
    name, q = gen(n)
    errs = []
    try:
        out = [st(l) for l in go(q)]
    except Exception as e:
        return name, q, [], ['Err ' + str(e)]
    if out and out[0].startswith('Err'):
        return name, q, [], out
    f = parse(q)
    V = sorted(set(re.findall('[a-z]', q.replace('sqrt', ''))))
    A = [l[5:] for l in out if l.startswith('Ans: ')]
    qbots = bottoms(f)
    abots = bottoms(parse(A[0])) if A and '|' not in A[0] else []
    P = [l[5:] for l in out if l.startswith('NPV: ')]
    PA = [l[9:] for l in out if l.startswith('Ans NPV: ')]
    try:
        CQ = npvconds(P[0]) if P else []
        CA = npvconds(PA[0]) if PA else []
    except Exception as e:
        return name, q, ['npv line unread: %s %s %s' % (P, PA, e)], out
    # every zero of a bottom typed meets an NPV piece, and every zero of
    # one of the answer's bottoms an NPV or Ans NPV piece
    for b, C in [(b, CQ) for b in qbots] + [(b, CQ + CA) for b in abots]:
        for v in sorted(str(s) for s in b.free_symbols):
            for _ in range(3):
                others = dict((w, rnd()) for w in V if w != v)
                try:
                    zs = zeros(b, v, others)
                except Exception:
                    continue
                for x in zs:
                    p = dict(others)
                    p[v] = x
                    if not [c for c in C if held(c, p)]:
                        errs.append('npv misses %s=0 at %s' % (b, p))
                        break
    # every NPV piece names zeros of a bottom typed, every Ans NPV piece
    # zeros of one of the answer's bottoms
    for c, bots in [(c, qbots) for c in CQ] + [(c, abots + qbots) for c in CA]:
        for v in sorted(str(s) for s in c.free_symbols):
            for _ in range(3):
                others = dict((w, rnd()) for w in V if w != v)
                try:
                    zs = zeros(c, v, others)
                except Exception:
                    continue
                for x in zs:
                    p = dict(others)
                    p[v] = x
                    if not [b for b in bots if held(b, p)]:
                        errs.append('npv piece %s=0 at %s makes no bottom 0' % (c, p))
                        break
    # Restr
    R = [l[7:] for l in out if l.startswith('Restr: ')]
    pieces = R[0].split(', ') if R else []
    try:
        tests = [piece(u) for u in pieces]
    except Exception as e:
        return name, q, errs + ['restr unread %s' % e], out
    rs = [r for r in rads(f) if not r.atoms(S)]
    for _ in range(60):
        p = dict((w, sp.Rational(random.randint(-40, 40), 4)) for w in V)
        try:
            if not all(t(p) for t in tests):
                continue
        except ZeroDivisionError:
            continue
        except TypeError:
            errs.append('restr piece has a letter not typed: %s' % pieces)
            break
        for r in rs:
            z = ev(r, p)
            if z.real < -1e-9:
                errs.append('restr lets %s < 0 at %s' % (r, p))
                break
    for u in pieces:
        if re.fullmatch('[a-z]>=0', u):
            continue
        if '>=0' not in u or ' or ' in u:
            if len(V) > 1:
                errs.append('restr piece %s unlooked-for' % u)
            continue
        e = parse(u[:-3])
        ok = False
        for r in rads(f):
            k = [complex(ev(e, p)) / complex(ev(r, p)) for p in
                 [dict((w, sp.Rational(random.randint(-40, 40), 7)) for w in V) for _ in range(4)]
                 if abs(ev(r, p)) > 1e-9]
            if k and all(abs(z.imag) < 1e-9 and z.real > 0 and abs(z - k[0]) < 1e-9 * abs(k[0]) for z in k):
                ok = True
        if not ok:
            errs.append('restr piece %s is no root typed' % u)
    return name, q, errs, out


if __name__ == '__main__':
    from collections import Counter
    cnt = Counter()
    bad = 0
    with Pool(2, initializer=init) as pool:
        for i, (name, q, errs, out) in enumerate(pool.imap_unordered(check, range(N), chunksize=10)):
            cnt[name.split()[0]] += 1
            if errs:
                bad += 1
                print('BAD', name, repr(q), out, errs[:2], flush=True)
            if (i + 1) % 500 == 0:
                print(i + 1, 'done,', bad, 'bad', flush=True)
    print(dict(cnt))
    print(N, 'questions,', bad, 'bad')
