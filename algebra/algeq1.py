# ALGEQ1 - equations, part 1: reading one in, and squaring the roots
# out of it (see algebra.py)
from algcore import *


def sym(Q):
    # the mask bit for the root of Q, made the first time it is seen
    i = 0
    while i < len(R) and R[i] != Q:
        i += 1
    if i == len(R):
        if i == 4:
            raise ValueError('over 4 roots')
        R.append(Q)
    return 1 << i


def mkrad(v):
    # sqrt(P/d) = sqrt(P*d)/d, and square factors come out front
    P, d = v
    if not P:
        return ({}, 1)
    Q = {}
    g = 0
    for k in P:
        Q[k] = P[k] * d
        g = gcd(g, Q[k])
    for k in Q:
        c = Q[k]
    if len(Q) == 1 and (0, 0) in Q:
        if c < 0:
            raise ValueError('sqrt of negative')
        r = isq(c)
        if r * r == c:
            return tidy({(0, 0): r}, d)
    k = 1
    m = g
    f = 2
    while f < 300 and f * f <= m:
        while m % (f * f) == 0:
            m //= f * f
            k *= f
        f += 1
    for t in Q:
        Q[t] = Q[t] // g * m
    return tidy({(0, sym(Q)): k}, d)


# The parser gives (top, bottom). A bottom that is just a number goes
# into the top; any other is kept (in B, to check), and the equation is
# multiplied through by the bottoms at the end
ONE = ({(0, 0): 1}, 1)
B = []


def fd(X, Y):
    # X/Y; every bottom with the letter is kept in B, to check
    P, d = Y
    if not P:
        raise ValueError('divide by 0')
    if len(P) == 1 and (0, 0) in P:
        return mul(X, ({(0, 0): d}, P[(0, 0)])), ONE
    B.append(P)
    return X, Y


def sr(v):
    # sqrt(top/bottom) = sqrt(top*bottom)/|bottom|, and |bottom| is the
    # root of bottom^2
    if v[1] == ONE:
        return (mkrad(v[0]), ONE)
    return (mkrad(mul(v[0], v[1])), mkrad(mul(v[1], v[1])))


def pexpr(ts, i):
    v = ({}, 1), ONE
    while True:
        s = 1
        while i < len(ts) and ts[i] in '+-':
            if ts[i] == '-':
                s = -s
            i += 1
        t, i = pterm(ts, i)
        v = add(mul(v[0], t[1]), mul(t[0], v[1]), s), mul(v[1], t[1])
        if i >= len(ts) or ts[i] not in '+-':
            return v, i


def pterm(ts, i):
    v, i = pfac(ts, i)
    while i < len(ts) and ts[i] not in '+-)':
        t = ts[i]
        if t == '*' or t == '/':
            i += 1
        w, i = pfac(ts, i)
        if t == '/':
            v = fd(mul(v[0], w[1]), mul(v[1], w[0]))
        else:
            v = mul(v[0], w[0]), mul(v[1], w[1])
    return v, i


def pfac(ts, i):
    if i >= len(ts):
        raise ValueError('ends too soon')
    t = ts[i]
    i += 1
    if t == '(':
        v, i = pexpr(ts, i)
        i = need(ts, i, ')')
    elif t == 'sqrt':
        i = need(ts, i, '(')
        v, i = pexpr(ts, i)
        i = need(ts, i, ')')
        v = sr(v)
    elif t in LET:
        if t not in L:
            L.append(t)
        v = ({(1 << (8 * L.index(t)), 0): 1}, 1), ONE
    elif t[0] in DIG:
        v = num(t), ONE
    elif t == '-':
        v, i = pfac(ts, i)
        return (mul(v[0], ({(0, 0): -1}, 1)), v[1]), i
    else:
        raise ValueError('bad ' + t)
    # power: whole, or a half (1/2, 0.5, 3/2) for a square root, and
    # below 0 for 1 over it. x2 means x^2: the power can follow a
    # letter with no ^ between
    if i < len(ts) and (ts[i] == '^' or (t in LET and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        P, d = e[0]
        n = P.get((0, 0), 0)
        if e[1] != ONE or len(P) != (n != 0) or d > 2 or abs(n) > 24 * d:
            raise ValueError('bad power')
        if d == 2:
            v = sr(v)
        r = (ONE, ONE)
        for _ in range(abs(n)):
            r = mul(r[0], v[0]), mul(r[1], v[1])
        v = fd(r[1], r[0]) if n < 0 else r
    return v, i


def side(s):
    # close brackets left open, the way the calculator does
    k = 0
    for c in s:
        if c == '(':
            k += 1
        elif c == ')':
            k -= 1
    ts = tok(s + ')' * max(k, 0))
    if not ts:
        raise ValueError('nothing at =')
    v, i = pexpr(ts, 0)
    if i != len(ts):
        raise ValueError('bad ' + ts[i])
    return v


def elim(F):
    # square the roots out of F (an expression that is 0): F = A + B*root
    # (the last root made: an outer one before what is inside it), so
    # A = -B*root, and A^2 = B^2*(what is under the root). Gives what is
    # left (no roots) and how many times it was squared
    n = 0
    while True:
        m = 0
        for k in F:
            m |= k[1]
        if not m:
            return F, n
        i = 0
        while m >> (i + 1):
            i += 1
        b = 1 << i
        A = {}
        Q = {}
        for k in F:
            if k[1] & b:
                Q[(k[0], k[1] ^ b)] = F[k]
            else:
                A[k] = F[k]
        F = add((pm(A, A), 1), (pm(pm(Q, Q), R[i]), 1), -1)[0]
        n += 1
        if F:
            F = tidy(F, 0)[0]
