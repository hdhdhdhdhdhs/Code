# ALGFR2 - simplifying fractions, part 2: polynomials and factoring
# (see algebra.py). Here a polynomial is {letter powers: number}, letter
# i's power 16 bits at 2^(16i), letters in L (this part's own list)
from algcore import gcd, prim, pdiv, pg, sqf
L = []  # letters in the order typed
N = []  # every bottom met on the way (as factors), for the NPVs


# ---- polynomials: {letter powers packed: whole number}
def dg(k):
    e = []
    while k:
        e.append(k & 65535)
        k >>= 16
    return e


def pm(a, b):
    c = {}
    for i in a:
        for j in b:
            c[i + j] = c.get(i + j, 0) + a[i] * b[j]
    for k in list(c):
        if not c[k]:
            del c[k]
    return c


def lead(P):
    # the number on the term written first
    return P[min(P, key=kk)]


def vs(P):
    # the letters in P
    o = []
    for k in P:
        e = dg(k)
        for i in range(len(e)):
            if e[i] and i not in o:
                o.append(i)
    o.sort()
    return o


def ky(P):
    return tuple(sorted(P.items()))


def ex(F, s):
    # multiply out the factors whose power has sign s (1: top, -1: bottom)
    P = {0: 1}
    for k in F:
        e = F[k] * s
        if e > 0:
            f = dict(k)
            if len(f) > 1 and e * max([max(dg(j) or [0]) for j in f]) > 120:
                raise ValueError('too big')
            for _ in range(e):
                P = pm(P, f)
    return P


# ---- writing it out
def ab():
    return sorted(range(len(L)), key=lambda i: L[i])


def kk(k):
    # term order: biggest total power first, then a before b
    e = dg(k)
    return [-sum(e)] + [-(e[i] if i < len(e) else 0) for i in ab()]


# ---- factoring
def fct(P):
    # P = c times the factors in F; each factor has its biggest term
    # (letters in typed order) > 0
    c = 0
    for k in P:
        c = gcd(c, P[k])
    if lead(P) < 0:
        c = -c
    F = {}
    e = None
    for k in P:
        d = dg(k)
        e = d if e is None else [min(e[i], d[i] if i < len(d) else 0) for i in range(len(e))]
    m = 0
    for i in range(len(e)):
        if e[i]:
            F[((1 << 16 * i, 1),)] = e[i]
            m += e[i] << 16 * i
    Q = {}
    for k in P:
        Q[k - m] = P[k] // c
    for f in spl(Q):
        if lead(f) < 0:
            c = -c
            for k in f:
                f[k] = -f[k]
        k = ky(f)
        F[k] = F.get(k, 0) + 1
    return c, F


def spl(P):
    # P (shares no number or letter) as a list of factors
    if len(P) < 2:
        return []
    v = vs(P)
    t = [sum(dg(k)) for k in P]
    if len(v) == 1 or len(v) == 2 and min(t) == max(t):
        # one letter, or two with every term the same total power:
        # factored as one letter (the other as 1), then put back
        i = v[0]
        j = v[-1]
        n = 0
        for k in P:
            n = max(n, dg(k)[i] if i < len(dg(k)) else 0)
        if n > 30:
            return [P]
        c = [0] * (n + 1)
        for k in P:
            d = dg(k)
            c[d[i] if i < len(d) else 0] = P[k]
        o = []
        for f in uf(c):
            n = len(f) - 1
            g = {}
            for a in range(n + 1):
                if f[a]:
                    g[(a << 16 * i) + ((n - a) << 16 * j if j != i else 0)] = f[a]
            o.append(g)
        return o
    # more letters: as a polynomial in one letter, take out what all
    # its numbers (polynomials in the other letters) share: grouping
    for i in v:
        C = {}
        for k in P:
            d = (k >> 16 * i) & 65535
            if d not in C:
                C[d] = {}
            C[d][k - (d << 16 * i)] = P[k]
        if len(C) < 2:
            continue
        G = None
        for d in C:
            C[d] = fct(C[d])
            F = C[d][1]
            H = {}
            for k in F:
                if G is None or k in G:
                    H[k] = F[k] if G is None else min(G[k], F[k])
            G = H
            if not G:
                break
        if G:
            Q = {}
            for d in C:
                g, F = C[d]
                for k in G:
                    F[k] -= G[k]
                X = ex(F, 1)
                for k in X:
                    Q[k + (d << 16 * i)] = g * X[k]
            o = []
            for k in G:
                o += [dict(k)] * G[k]
            return o + spl(Q)
    # a factor a*x+b, a going into the number on x's top power and b
    # into the term with no x (each a polynomial in the other letters):
    # x^2-y^4 = (x-y^2)(x+y^2)
    for i in v:
        C = {}
        for k in P:
            d = (k >> 16 * i) & 65535
            if d not in C:
                C[d] = {}
            C[d][k - (d << 16 * i)] = P[k]
        n = max(C)
        if n == 1:
            return [P]
        D = dl(C[0])
        for a in dl(C[n]):
            for b in D:
                for s in (1, -1):
                    f = {}
                    for k in b:
                        f[k] = s * b[k]
                    for k in a:
                        f[k + (1 << 16 * i)] = a[k]
                    q = dv(P, f)
                    if q:
                        return [f] + spl(q)
    return [P]


def dl(Q):
    # what divides Q: its number's divisors times its factors' powers
    c, F = fct(Q)
    o = [{0: d} for d in dvs(c)]
    for k in F:
        r = []
        for x in o:
            for _ in range(F[k] + 1):
                r.append(x)
                x = pm(x, dict(k))
        o = r[:60]
    return o


def dv(a, b):
    # a/b exactly, or None
    K = max(b)
    e = dg(K)
    a = dict(a)
    q = {}
    n = 0
    while a:
        k = max(a)
        d = dg(k)
        n += 1
        if n > 300 or a[k] % b[K] or [1 for j in range(len(e)) if e[j] > (d[j] if j < len(d) else 0)]:
            return None
        t = a[k] // b[K]
        q[k - K] = t
        for j in b:
            a[j + k - K] = a.get(j + k - K, 0) - t * b[j]
            if not a[j + k - K]:
                del a[j + k - K]
    return q


def uf(c):
    # c (low power first, c[0] != 0) into factors: repeated factors,
    # zeros p/q, then pieces x^2+bx+c; each one checked by exact
    # division (fix() below still cancels anything this misses)
    o = []
    st = [c]
    while st:
        c = st.pop()
        if len(c) < 3:
            o.append(c)
            continue
        s = sqf(c)
        f = None
        if len(s) < len(c):
            f = s
        elif abs(c[0]) < 10 ** 8 and abs(c[-1]) < 10 ** 8:
            f = root(c)
            if not f and len(c) > 4:
                f = split(c)
        if f:
            st += [f, pdiv(c, f)]
        else:
            o.append(c)
    return o


# ---- one-letter polynomials, low power first (as in fac.py)
def dvs(n):
    n = abs(n)
    o = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            o.append(d)
            if d * d != n:
                o.append(n // d)
        d += 1
    return o


def ev(c, x):
    s = 0
    for i in range(len(c) - 1, -1, -1):
        s = s * x + c[i]
    return s


def root(c):
    # a zero p/q needs q-p to divide c(1) and q+p to divide c(-1)
    a = ev(c, 1)
    b = ev(c, -1)
    for q in dvs(c[-1]):
        for p in dvs(c[0]):
            for p in (p, -p):
                if ((q == p or a % (q - p) == 0) and (q == -p or b % (q + p) == 0)
                        and gcd(p, q) == 1 and pdiv(c, [-p, q]) is not None):
                    return [-p, q]
    return None


def split(c):
    # a quadratic factor through the values at -1, 0 and 1 (small ones)
    if max(abs(ev(c, 1)), abs(ev(c, -1)), abs(c[0])) > 10 ** 8:
        return None
    v0 = dvs(ev(c, 0))
    v1 = dvs(ev(c, 1))
    vm = dvs(ev(c, -1))
    if len(v0) * len(v1) * len(vm) > 4000:
        return None
    for a in v0 + [-x for x in v0]:
        for b in v1 + [-x for x in v1]:
            for d in vm + [-x for x in vm]:
                t = b + d - 2 * a
                if t > 0 and t % 2 == 0 and (b - d) % 2 == 0:
                    g = [a, (b - d) // 2, t // 2]
                    if pdiv(c, g) is not None:
                        return g
    return None
