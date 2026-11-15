# ALGRT1 - simplifying with roots, part 1: reading it in, making roots
# and clearing them out of bottoms (see algebra.py)
from algcore import *
U = []   # letters taken as >= 0 (each shown in Restr)
ST = []  # what tops and bottoms were multiplied by (shown as Times)
BX = []  # every bottom met, for the NPVs when there are many letters


def sym(Q):
    # the mask bit for the root of Q, made the first time it is seen
    i = 0
    while i < len(R) and R[i] != Q:
        i += 1
    if i == len(R):
        if i == 20:
            raise ValueError('over 20 roots')
        R.append(Q)
    return 1 << i


def mkrad(v):
    # sqrt(P/d) = sqrt(P*d)/d, and square factors come out front
    P, d = v
    from algrt2 import pf, sq
    if not P:
        return ({}, 1)
    Q = {}
    g = 0
    for k in P:
        Q[k] = P[k] * d
        g = gcd(g, Q[k])
    # a+b*sqrt(n) that is a square: sqrt(4+2sqrt(3)) = 1+sqrt(3)
    if len(Q) == 2 and (0, 0) in Q:
        for k in Q:
            if k[1] and not k[0]:
                n = 1
                j = 0
                m = k[1]
                while m:
                    if m & 1:
                        n *= R[j].get((0, 0), 0) if len(R[j]) == 1 else 0
                    m >>= 1
                    j += 1
                a = Q[(0, 0)]
                b = Q[k]
                D = a * a - b * b * n
                r = isq(D) if D > 0 else -1
                if n and a > 0 and r * r == D:
                    return mul(add(mkrad(({(0, 0): a + r}, 2)), mkrad(({(0, 0): a - r}, 2)),
                                   1 if b > 0 else -1), ({(0, 0): 1}, d))
    for k in Q:
        c = Q[k]
    if len(Q) == 1 and (0, 0) in Q and c < 0:
        raise ValueError('sqrt of negative')
    # numbers: squares come out, and each prime left inside gets a
    # root of its own, so they always combine. One term below 0 or
    # with a root in it stays one root
    one = len(Q) == 1 and (k[1] or c < 0)
    r = 1
    n = 1
    m = 0
    f = pf(g)
    f.sort()
    i = 0
    while i < len(f):
        if i + 1 < len(f) and f[i] == f[i + 1]:
            r *= f[i]
            i += 2
        else:
            n *= f[i]
            if not one:
                m |= sym({(0, 0): f[i]})
            i += 1
    if one:
        for k in Q:
            Q[k] = Q[k] // g * n
        return tidy({(0, sym(Q)): r}, d)
    # letters: the power every term has comes out the same way
    o = 0
    z = 0
    for i in range(len(L)):
        t = 99
        for k in Q:
            e = dg(k[0])
            t = min(t, e[i] if i < len(e) else 0)
        if t:
            if L[i] not in U:
                U.append(L[i])
            z += t << (8 * i)
            o += (t >> 1) << (8 * i)
            if t & 1:
                m |= sym({(1 << (8 * i), 0): 1})
    P = {}
    for k in Q:
        P[(k[0] - z, k[1])] = Q[k] // g
    if len(P) > 1:
        p = sq(P)
        if p and min(p.values()) > 0:
            # the square of a sum that is >= 0: sqrt(x^2+6x+9) = x+3
            for k in p:
                e = dg(k[0])
                for i in range(len(e)):
                    if e[i] and L[i] not in U:
                        U.append(L[i])
            return mul(tidy({(o, m): r}, d), (p, 1))
        m |= sym(P)
    return tidy({(o, m): r}, d)


def pexpr(ts, i):
    v = ({}, 1)
    while True:
        s = 1
        while i < len(ts) and ts[i] in '+-':
            if ts[i] == '-':
                s = -s
            i += 1
        t, i = pterm(ts, i)
        v = add(v, t, s)
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
            w, v = rat(w, v)
        v = mul(v, w)
    return v, i


def rat(w, v):
    # 1/w, after clearing the roots out of w: top and bottom times
    # its conjugate (or just the root, when w is one term)
    BX.append(w)
    while True:
        if not w[0]:
            raise ValueError('divide by 0')
        m = 0
        for k in w[0]:
            m |= k[1]
        if not m:
            break
        b = 1
        while m >= b + b:
            b += b
        c = {}
        h = 0
        for k in w[0]:
            c[k] = -w[0][k] if k[1] & b else w[0][k]
            h += c[k] < 0
        if len(c) == 1:
            c = {(0, k[1]): 1}
            h = 0
        # the smallest whole numbers, mostly + : 1-sqrt(3), not -3-3sqrt(3)
        g = 0
        for k in c:
            g = gcd(g, c[k])
        if h + h > len(c):
            g = -g
        for k in c:
            c[k] //= g
        ST.append(c)
        v = mul(v, (c, 1))
        w = mul(w, (c, 1))
    if len(w[0]) > 1:
        # a bottom like x-4 stays as it is, written like a letter; a
        # number all its terms share comes out, so it can cancel
        g = 0
        for k in w[0]:
            g = gcd(g, w[0][k])
        P = {}
        for k in w[0]:
            P[k] = w[0][k] // g
        # when the bottom goes into the top exactly, it cancels
        q = dv(v[0], P)
        if q is not None:
            return ({(0, 0): w[1]}, 1), (q, v[1] * g)
        from algrt2 import es
        t = '(' + es(P, 1) + ')'
        if t not in L:
            L.append(t)
        return ({(-1 << (8 * L.index(t)), 0): w[1]}, g), v
    for k in w[0]:
        c = w[0][k]
    return ({(-k[0], 0): w[1]}, c), v


def dv(a, P):
    # a / P exactly (P has no roots), or None: long division, biggest
    # power first, done for each root part of a on its own
    for k in list(a) + list(P):
        for e in dg(k[0]):
            if e < 0:
                return None
    p = max([k[0] for k in P])
    a = dict(a)
    q = {}
    while a:
        k = (-1, 0)
        for t in a:
            if (t[1], t[0]) > (k[1], k[0]):
                k = t
        e = k[0] - p
        if a[k] % P[(p, 0)]:
            return None
        for x in dg(e):
            if x < 0:
                return None
        c = a[k] // P[(p, 0)]
        q[(e, k[1])] = c
        for t in P:
            j = (t[0] + e, k[1])
            a[j] = a.get(j, 0) - c * P[t]
            if not a[j]:
                del a[j]
    return q


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
        v = mkrad(v)
    elif t in LET:
        if t not in L:
            L.append(t)
        v = ({(1 << (8 * L.index(t)), 0): 1}, 1)
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return mul(v, ({(0, 0): -1}, 1)), i
    else:
        raise ValueError('bad ' + t)
    # power: whole, or a half (1/2, 0.5, 3/2) for a square root, and
    # below 0 for 1 over it. x2 means x^2: the power can follow a
    # letter with no ^ between
    if i < len(ts) and (ts[i] == '^' or (t in LET and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        n = e[0].get((0, 0), 0)
        if len(e[0]) != (n != 0) or e[1] > 2 or abs(n) > 24 * e[1]:
            raise ValueError('bad power')
        if e[1] == 2:
            v = mkrad(v)
        r = ({(0, 0): 1}, 1)
        for _ in range(abs(n)):
            r = mul(r, v)
        v = r
        if n < 0:
            # below 0: 1 over it
            w, v = rat(v, ({(0, 0): 1}, 1))
            v = mul(v, w)
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
