# ALGFR1 - simplifying fractions, part 1: values, reading it in, and the
# answer with its NPVs (see algebra.py). A value is (p, q, F): p/q times
# the factors in F, {factor: power}, a power below 0 in the bottom
from algfr2 import *
from algcore import DIG, LET, tok, need


# ---- values: (p, q, F) is p/q times the factors in F, {key: power};
# a power below 0 is in the bottom
def val(p, q, F):
    if not p:
        return (0, 1, {})
    g = gcd(p, q)
    if q < 0:
        g = -g
    G = {}
    for k in F:
        if F[k]:
            G[k] = F[k]
    return (p // g, q // g, G)


def mul(a, b, s=1):
    # a*b, or a/b with s=-1: then b's top factors are bottoms (kept in N)
    if s < 0:
        if not b[0]:
            raise ValueError('divide by 0')
        for k in b[2]:
            if b[2][k] > 0 and k not in N:
                N.append(k)
        b = (b[1], b[0], b[2])
    F = dict(a[2])
    for k in b[2]:
        F[k] = F.get(k, 0) + s * b[2][k]
    return val(a[0] * b[0], a[1] * b[1], F)


def pw(a, n):
    if n < 0:
        return mul((1, 1, {}), pw(a, -n), -1)
    F = {}
    for k in a[2]:
        F[k] = a[2][k] * n
    return val(a[0] ** n, a[1] ** n, F)


def add(T):
    # a sum of (sign, value): over the smallest common bottom, with the
    # factors every term has kept out, then the top factored again
    T = [t for t in T if t[1][0]]
    if len(T) < 2:
        return (T[0][0] * T[0][1][0], T[0][1][1], T[0][1][2]) if T else (0, 1, {})
    D = {}
    G = None
    q = 1
    for s, v in T:
        q = q * v[1] // gcd(q, v[1])
        for k in v[2]:
            if v[2][k] < 0:
                D[k] = min(D.get(k, 0), v[2][k])
        H = {}
        for k in v[2]:
            if v[2][k] > 0 and (G is None or k in G):
                H[k] = v[2][k] if G is None else min(G[k], v[2][k])
        G = H
    P = {}
    for s, v in T:
        F = dict(v[2])
        for k in D:
            F[k] = F.get(k, 0) - D[k]
        for k in G:
            F[k] -= G[k]
        c = s * v[0] * (q // v[1])
        X = ex(F, 1)
        for k in X:
            P[k] = P.get(k, 0) + c * X[k]
            if not P[k]:
                del P[k]
    if not P:
        return (0, 1, {})
    c, F = fct(P)
    for H in (G, D):
        for k in H:
            F[k] = F.get(k, 0) + H[k]
    return val(c, q, F)


def num(t):
    i = t.find('.')
    if t == '.' or (i >= 0 and t.find('.', i + 1) >= 0):
        raise ValueError('bad number')
    if i < 0:
        return (int(t), 1, {})
    f = t[i + 1:]
    return val(int(t[:i] + f), 10 ** len(f), {})


def pexpr(ts, i):
    T = []
    while True:
        s = 1
        while i < len(ts) and ts[i] in '+-':
            if ts[i] == '-':
                s = -s
            i += 1
        t, i = pterm(ts, i)
        T.append((s, t))
        if i >= len(ts) or ts[i] not in '+-':
            return add(T), i


def pterm(ts, i):
    v, i = pfac(ts, i)
    while i < len(ts) and ts[i] not in '+-)':
        t = ts[i]
        if t == '*' or t == '/':
            i += 1
        w, i = pfac(ts, i)
        v = mul(v, w, -1 if t == '/' else 1)
    return v, i


def pfac(ts, i):
    if i >= len(ts):
        raise ValueError('ends too soon')
    t = ts[i]
    i += 1
    if t == '(':
        v, i = pexpr(ts, i)
        i = need(ts, i, ')')
    elif t in LET:
        if t not in L:
            L.append(t)
        v = (1, 1, {((1 << 16 * L.index(t), 1),): 1})
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return (-v[0], v[1], v[2]), i
    else:
        raise ValueError('bad ' + t)
    # power: a whole number, below 0 too. x2 means x^2
    if i < len(ts) and (ts[i] == '^' or (t in LET and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        if e[2] or e[1] != 1 or abs(e[0]) > 99:
            raise ValueError('bad power')
        v = pw(v, e[0])
    return v, i


def mo(k):
    s = ''
    e = dg(k)
    for i in ab():
        if i < len(e) and e[i]:
            s += L[i] + ('^' + str(e[i]) if e[i] > 1 else '')
    return s


def es(P):
    if not P:
        return '0'
    s = ''
    t = sorted(P, key=kk)
    # a + term first when one is as big as the first: x-c, not -c+x
    for k in t:
        if sum(dg(k)) < sum(dg(t[0])):
            break
        if P[k] > 0:
            t.remove(k)
            t.insert(0, k)
            break
    for k in t:
        c = P[k]
        m = mo(k)
        s += ('-' if c < 0 else '+') + (str(abs(c)) if abs(c) != 1 or not m else '') + m
    return s[1:] if s[0] == '+' else s


def fac(v):
    # the top multiplied out, over the bottom factored: number,
    # letters, then (factors)
    p, q, F = v
    c = q
    m = 0
    t = ''
    n = c != 1
    for k in sorted(F, key=lambda k: (len(k) > 1, es(dict(k)))):
        e = -F[k]
        if e > 0 and len(k) == 1:
            m += k[0][0] * e
        elif e > 0:
            t += '(' + es(dict(k)) + ')' + ('^' + str(e) if e > 1 else '')
            n += 1
    n += len(vs({m: 1})) if m else 0
    b = (str(c) if c != 1 or not (m or t) else '') + mo(m) + t
    a = pm({0: p}, ex(F, 1))
    t = es(a)
    if b == '1':
        return t
    # brackets round a top or bottom with a power or more than one piece,
    # so 2y^8/9 can not be read as 2y^(8/9): (2y^8)/9
    if n > 1 or '^' in b and b[-1] != ')':
        b = '(' + b + ')'
    return ('(' + t + ')' if len(a) > 1 or '^' in t else t) + '/' + b


def npv():
    # each bottom met: the values that make it 0
    Z = []
    V = {}
    O = []
    for k in N:
        P = dict(k)
        v = vs(P)
        i = v[0]
        x = L[i]
        if len(P) == 1:
            Z.append(x)
            continue
        if P.get(0, 0) > 0 and [1 for j in P if P[j] < 0 or [1 for e in dg(j) if e % 2]] == []:
            # even powers, + only and a number (like x^4+4): never 0
            continue
        if len(v) > 1:
            x, t = one(P)
            if not x:
                O.append(t)
                continue
            if x not in V:
                V[x] = []
            V[x].append((9e99, t))
            continue
        n = max(dg(max(P)))
        c = [0] * (n + 1)
        for j in P:
            c[dg(j)[i] if j else 0] = P[j]
        if x not in V:
            V[x] = []
        z = V[x]
        if n == 1:
            g = gcd(c[0], c[1])
            z.append((-c[0] / c[1], str(-c[0] // g) + ('/' + str(c[1] // g)) * (c[1] > g)))
        elif n == 2:
            # (-b+sqrt(D))/(2a) and (-b-sqrt(D))/(2a), squares taken out
            C, B, A = c
            D = B * B - 4 * A * C
            if D > 0:
                s = 1
                j = 2
                while j < 1000 and j * j <= D:
                    while D % (j * j) == 0:
                        D //= j * j
                        s *= j
                    j += 1
                g = gcd(gcd(B, s), 2 * A)
                r = (str(s // g) if s > g else '') + 'sqrt(' + str(D) + ')'
                for h in '+-':
                    t = (str(-B // g) + h if B else '-' * (h == '-')) + r
                    if 2 * A > g:
                        t = ('(' + t + ')' if B else t) + '/' + str(2 * A // g)
                    z.append(((-B + (1 if h == '+' else -1) * s * D ** 0.5) / 2 / A, t))
        else:
            O.append(es(P))
    o = []
    for x in Z:
        if x in V:
            V[x].append((0, '0'))
        else:
            o.append(x)
    o.sort()
    o = [','.join(o) + '!=0'] if o else []
    for x in sorted(V):
        z = V[x]
        z.sort()
        if z:
            o.append(x + '!=' + ','.join([t[1] for t in z]))
    O.sort()
    for t in O:
        o.append(t + '!=0')
    return o


def one(P):
    # x+y -> x!=-y: a letter alone in one term, times 1 or -1, and in no
    # other term
    for i in ab():
        n = 0
        for j in P:
            d = dg(j)
            n += i < len(d) and d[i] > 0
        k = 1 << 16 * i
        if n == 1 and abs(P.get(k, 0)) == 1:
            Q = {}
            for j in P:
                if j != k:
                    Q[j] = -P[j] * P[k]
            return L[i], es(Q)
    return None, es(P)


def go(s):
    s = s.lower().replace(' ', '').replace('**', '^')
    if '=' in s:
        raise ValueError('no =: it simplifies')
    for t in (L, N):
        while t:
            t.pop()
    k = 0
    for c in s:
        k += (c == '(') - (c == ')')
    ts = tok(s + ')' * max(k, 0))
    if not ts:
        raise ValueError('nothing typed')
    v, i = pexpr(ts, 0)
    if i != len(ts):
        raise ValueError('bad ' + ts[i])
    v = fix(v)
    o = ['Ans: ' + fac(v)]
    if N:
        o.append('NPV: ' + ('; '.join(npv()) or 'none'))
    return o


def fix(v):
    # a one-letter top factor and bottom factor that share a piece the
    # factoring missed (too big for it): split both, so it cancels
    p, q, F = v
    for a in list(F):
        for b in list(F):
            if a in F and b in F and F[a] > 0 > F[b] and len(a) > 1 < len(b) and vs(dict(a)) == vs(dict(b)) == vs(dict(a))[:1]:
                i = vs(dict(a))[0]
                c = [uc(a, i), uc(b, i)]
                h = pg(c[0], c[1])
                if len(h) > 1:
                    for k in (a, b):
                        e = F.pop(k)
                        for t in (h, pdiv(uc(k, i), h)):
                            g, G = fct(dict([(j << 16 * i, t[j]) for j in range(len(t)) if t[j]]))
                            if e > 0:
                                p *= g ** e
                            else:
                                q *= g ** -e
                            for j in G:
                                F[j] = F.get(j, 0) + G[j] * e
    return val(p, q, F)


def uc(k, i):
    # factor k (one letter, letter i) as numbers, low power first
    c = [0] * (max([j >> 16 * i for j, _ in k]) + 1)
    for j, x in k:
        c[j >> 16 * i] = x
    return c
