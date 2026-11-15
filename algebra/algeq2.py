# ALGEQ2 - equations, part 2: the real zeros of a polynomial, exactly
# (see algebra.py). Each zero is pinned between two fractions with
# whole-number maths (Sturm's sign changes), then named: a fraction p/q,
# (a+sqrt(b))/c for a quadratic, or a decimal ~
from algcore import *


def hz(c, p, q):
    # q^n * c(p/q), exactly: 0 means p/q is a zero
    n = len(c) - 1
    s = c[n]
    t = 1
    for i in range(n - 1, -1, -1):
        t *= q
        s = s * p + c[i] * t
    return s


def sgn(v):
    return (v > 0) - (v < 0)


def sturm(c):
    # Sturm's chain: counts the real zeros between any two points
    S = [c, prim([i * c[i] for i in range(1, len(c))], 0)]
    while len(S[-1]) > 1:
        a = S[-2]
        b = S[-1]
        r = a[:]
        m = abs(b[-1])
        t = sgn(b[-1])
        while len(r) >= len(b):
            h = r[-1]
            d = len(r) - len(b)
            r = [x * m for x in r]
            for j in range(len(b)):
                r[d + j] -= t * h * b[j]
            r.pop()
        while r and r[-1] == 0:
            r.pop()
        if not r:
            break
        S.append(prim([-x for x in r], 0))
    return S


def vc(S, p, k):
    # sign changes along the chain at p/2^k
    n = 0
    l = 0
    for P in S:
        s = sgn(hz(P, p, 1 << k))
        if s:
            if l and s != l:
                n += 1
            l = s
    return n


def isolate(c):
    # an interval (lo, hi] / 2^k around each real zero, left to right
    S = sturm(c)
    n = len(c) - 1
    B = 1
    for i in range(n):
        while abs(c[i]) > abs(c[-1]) * B ** (n - i):
            B *= 2
    B *= 4
    st = [(-B, B, 0, vc(S, -B, 0), vc(S, B, 0))]
    o = []
    while st:
        lo, hi, k, a, b = st.pop()
        if a - b == 1:
            o.append([lo, hi, k])
        elif a - b > 1:
            if k > 400:
                raise ValueError('could not solve')
            lo *= 2
            hi *= 2
            k += 1
            m = (lo + hi) // 2
            v = vc(S, m, k)
            st.append((m, hi, k, v, b))
            st.append((lo, m, k, a, v))
    return o


def refine(c, t, bits, A=0):
    # halve until the width is 2^-bits of the size, and below 1/(2A);
    # [m, m, k] if exact
    lo, hi, k = t
    if lo == hi:
        return t
    sh = sgn(hz(c, hi, 1 << k))
    if sh == 0:
        return [hi, hi, k]
    while (hi - lo) << bits > max(abs(hi), 1 << k) or (hi - lo) * A * 2 >= 1 << k:
        lo *= 2
        hi *= 2
        k += 1
        m = (lo + hi) // 2
        s = sgn(hz(c, m, 1 << k))
        if s == 0:
            return [m, m, k]
        if s == sh:
            hi = m
        else:
            lo = m
    return [lo, hi, k]


def ratin(c, t):
    # the fraction in (lo, hi] that is a zero, if there is one. Its
    # bottom goes into A, the number on the top power, so A*zero is a
    # whole number: t is narrower than 1/(2A), so there is one to try
    lo, hi, k = t
    A = abs(c[-1])
    p = hi
    q = 1 << k
    if lo < hi:
        p = (A * hi) >> k
        q = A
        if p << k <= A * lo:
            return None
    if hz(c, p, q):
        return None
    g = gcd(p, q)
    return (p // g, q // g)


def fr(p, q):
    g = gcd(p, q)
    if q < 0:
        g = -g
    p //= g
    q //= g
    return str(p) if q == 1 else str(p) + '/' + str(q)


def fq(p, q):
    try:
        return p / q
    except OverflowError:
        return 1e300 if (p < 0) == (q < 0) else -1e300


def mid(t):
    return fq(t[0] + t[1], 1 << (t[2] + 1))


def qlab(c):
    # the two zeros of an irreducible quadratic, smaller first
    C, Bq, A = c
    D = Bq * Bq - 4 * A * C
    s = 1
    m = D
    i = 2
    while i < 1000 and i * i <= m:
        while m % (i * i) == 0:
            m //= i * i
            s *= i
        i += 1
    g = gcd(gcd(Bq, s), 2 * A)
    b = -Bq // g
    s //= g
    a = 2 * A // g
    r = (str(s) if s > 1 else '') + 'sqrt(' + str(m) + ')'
    o = []
    for k in (1, 0):
        t = (str(b) + '+-'[k] if b else ('-' if k else '')) + r
        if a != 1:
            t = ('(' + t + ')' if b else t) + '/' + str(a)
        o.append(t)
    return o


def zeros(c, f=1):
    # every real zero: [label, (p, q) if a fraction, decimal, interval]
    # f=0: c is already free of repeated factors
    z = []
    while c[0] == 0:
        c = c[1:]
        if not z:
            z.append(['0', (0, 1), 0.0, None])
    if len(c) < 2:
        return z
    if f:
        c = prim(sqf(c))
    left = []
    d = c
    for t in isolate(c):
        t = refine(c, t, 64, abs(c[-1]))
        r = ratin(c, t)
        if r:
            z.append([fr(r[0], r[1]), r, fq(r[0], r[1]), None])
            d = pdiv(d, [-r[0], r[1]])
        else:
            left.append(t)
    # what is left after the fractions: one zero is a fraction too,
    # two zeros of a quadratic are written exactly
    if len(d) == 2 and len(left) == 1:
        r = (-d[0], d[1])
        z.append([fr(r[0], r[1]), r, fq(r[0], r[1]), None])
        left = []
    if len(d) == 3 and len(left) == 2:
        a, b = qlab(d)
        z.append([a, None, mid(left[0]), left[0]])
        z.append([b, None, mid(left[1]), left[1]])
        left = []
    for t in left:
        z.append([dec(mid(t)), None, mid(t), t])
    z.sort(key=lambda t: t[2])
    return z