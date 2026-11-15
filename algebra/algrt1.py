# ALGRT1 - simplifying with roots, part 1: reading it in, making roots
# and clearing them out of bottoms (see algebra.py; algrt4 has what
# clearing a bottom uses)
from algcore import *
U = []   # letters taken as >= 0 (each shown in Restr)
ST = []  # what tops and bottoms were multiplied by (shown as Times)
BX = []  # every bottom met, and every root's inside (RX), for the NPVs
RX = []  # and Restr when there are many letters
PS = {}  # what each bottom written like a letter, (x-4), stands for


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
    RX.append(v)
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
    from algrt4 import clr, dv, cn, fb
    w, v = clr(w, v)
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
        # number and the letters all its terms share come out (and
        # cancel with the top's when they can)
        g = 0
        for k in w[0]:
            g = gcd(g, w[0][k])
        # all - : the - comes out too, so it is 3x+5, not -3x-5
        if not [k for k in w[0] if w[0][k] > 0]:
            g = -g
        z = 0
        for j in range(len(L)):
            t = 99
            for k in w[0]:
                e = dg(k[0])
                t = min(t, e[j] if j < len(e) else 0)
            if t > 0:
                z += t << (8 * j)
        P = {}
        for k in w[0]:
            P[(k[0] - z, 0)] = w[0][k] // g
        # what it shares with the top (one letter) is divided out of both
        from algrt2 import es
        P, c = cn(P, v[0])
        v = (c, v[1])
        if len(P) == 1:
            for k in P:
                pass
            return ({(-z - k[0], 0): w[1]}, g * P[k]), v
        # when the bottom goes into the top exactly, it cancels
        q = dv(v[0], P)
        if q is not None:
            return ({(-z, 0): w[1]}, 1), (q, v[1] * g)
        # (only one of power 2 or more could factor)
        t = '(' + es(P, 1) + ')'
        if max([sum(dg(k[0])) for k in P]) > 1:
            t, n = fb(P)
            if n < 0:
                g = -g
                for k in P:
                    P[k] = -P[k]
        if t not in L:
            L.append(t)
            PS[t] = P
        return ({(-z - (1 << (8 * L.index(t))), 0): w[1]}, g), v
    for k in w[0]:
        c = w[0][k]
    return ({(-k[0], 0): w[1]}, c), v


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
