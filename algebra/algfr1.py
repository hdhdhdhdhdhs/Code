# ALGFR1 - simplifying fractions, part 1: values and reading it in (see
# algebra.py). A value is (p, q, F): p/q times the factors in F,
# {factor: power}, a power below 0 in the bottom
from algfr2 import *
from algcore import DIG, LET, tok, need

FL = [1, 0]  # 1: dividing, only a bottom after the flip is an NPV;
# and 1 once a bottom with a letter is met
TP = [None]  # the top a fraction was typed with (see pterm)


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
            if b[2][k] > 0:
                FL[1] = 1
                if k not in N:
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
            if len(T) > 1:
                TP[0] = None
            return add(T), i


def pterm(ts, i):
    # TP[0] is left as the top it was typed with, when this is top/bottom
    v, i = pfac(ts, i)
    a = None
    while i < len(ts) and ts[i] not in '+-)':
        t = ts[i]
        if t == '*' or t == '/':
            i += 1
        k = len(N)
        w, i = pfac(ts, i)
        if t == '/' and FL[0]:
            fl(k, w)
        a = v if t == '/' and a is None else 0
        v = mul(v, w, -1 if t == '/' else 1)
    TP[0] = a or None
    return v, i


def fl(k, w):
    # dividing by w (or a power below 0): flip it, then find the NPVs.
    # Its bottoms go on top, so they are not NPVs; the top it was typed
    # with is a bottom then, so that is (or, not knowing that top, what
    # cancelled out of w's bottom, as it was in the top too)
    a = TP[0]
    o = [f for f in a[2] if a[2][f] > 0] if a else [f for f in N[k:] if w[2].get(f, 0) >= 0]
    del N[k:]
    for f in o:
        if f not in N:
            N.append(f)


def pfac(ts, i):
    if i >= len(ts):
        raise ValueError('ends too soon')
    k = len(N)
    t = ts[i]
    i += 1
    TP[0] = None
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
        a = TP[0]
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        if e[2] or e[1] != 1 or abs(e[0]) > 99:
            raise ValueError('bad power')
        if e[0] < 0 and FL[0]:
            TP[0] = a
            fl(k, v)
        TP[0] = None
        v = pw(v, e[0])
    return v, i


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
