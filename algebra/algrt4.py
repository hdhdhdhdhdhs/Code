# ALGRT4 - simplifying with roots, part 4: what clearing a bottom uses:
# fractions inside it, dividing, cancelling, and naming what is left
# (see algebra.py)
from algrt2 import *


def clr(w, v):
    # fractions in the bottom w: w and the top v times what clears them,
    # with (x-5) put back as x-5, so 1+sqrt(x-5)/(x-5) is x-5+sqrt(x-5)
    M = 0
    for j in range(len(L)):
        t = 0
        for k in w[0]:
            e = dg(k[0])
            if j < len(e) and e[j] < t:
                t = e[j]
        M -= t << (8 * j)
    if not M:
        return w, v
    ST.append(ex({(M, 0): 1}))
    return tidy(ex(pm(w[0], {(M, 0): 1})), w[1]), tidy(ex(pm(v[0], {(M, 0): 1})), v[1])


def ex(c):
    # each bottom written like a letter, above the line, multiplied out
    o = {}
    for k in c:
        e = dg(k[0])
        t = {k: c[k]}
        for j in range(len(e)):
            if e[j] > 0 and L[j][0] == '(':
                t = {(k[0] - (e[j] << (8 * j)), k[1]): c[k]}
                for _ in range(e[j]):
                    t = pm(t, PS[L[j]])
                t = ex(t)
                break
        for q in t:
            o[q] = o.get(q, 0) + t[q]
    return o


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


def cn(P, v):
    # P (no roots) in one letter, and v: each part of v with the same
    # roots and other letters is a polynomial in that letter too; what P
    # and all of them share is divided out. Returns P, v
    i = -1
    for k in P:
        e = dg(k[0])
        for j in range(len(e)):
            if e[j] < 0 or e[j] and (j != i > -1 or L[j][0] == '('):
                return P, v
            if e[j]:
                i = j
    if i < 0:
        return P, v
    m = []
    for k in v:
        e = dg(k[0])
        if i < len(e) and e[i] < 0:
            return P, v
        g = (k[0] - (pw(k, i) << (8 * i)), k[1])
        if g not in m:
            m.append(g)
    h = cl(P, (0, 0), i)
    for g in m:
        h = pg(h, cl(v, g, i))
        if len(h) < 2:
            return P, v
    o = [bk(pdiv(cl(P, (0, 0), i), h), (0, 0), i), {}]
    for g in m:
        o[1].update(bk(pdiv(cl(v, g, i), h), g, i))
    return o


def pw(k, i):
    # the power of letter i in term k
    e = dg(k[0])
    return e[i] if i < len(e) else 0


def cl(c, g, i):
    # the part of c that is g times powers of letter i, as numbers, low
    # power first
    o = [0]
    for k in c:
        e = pw(k, i)
        if (k[0] - (e << (8 * i)), k[1]) == g:
            while len(o) <= e:
                o.append(0)
            o[e] = c[k]
    return o


def bk(o, g, i):
    c = {}
    for e in range(len(o)):
        if o[e]:
            c[(g[0] + (e << (8 * i)), g[1])] = o[e]
    return c


def fb(P):
    # a bottom's name, factored as for a fraction: ((x+1)(x-1)),
    # ((x-4)^2); and -1 when that is of minus it (1-x^2). One letter:
    # its whole-number roots come out here; more: as for a fraction
    i = -1
    for k in P:
        e = dg(k[0])
        for j in range(len(e)):
            if e[j] and (j != i > -1 or L[j][0] == '('):
                i = -2
            elif e[j] and i == -1:
                i = j
    if i >= 0:
        return fu(P, i)
    t = es(P, 1)
    from algfr3 import go as g
    try:
        f = g('1/(' + t + ')')[0]
    except ValueError:
        f = ''
    n = 1
    if f[:6] == 'Ans: -':
        n = -1
        f = f[:5] + f[6:]
    if f[:7] != 'Ans: 1/' or f.find('~') >= 0:
        return '(' + t + ')', 1
    t = f[7:]
    d = 0
    for i in range(len(t)):
        d += (t[i] == '(') - (t[i] == ')')
        if d == 0 and i < len(t) - 1:
            return '(' + t + ')', n
    return (t if t[0] == '(' else '(' + t + ')'), n


def fu(P, i):
    # P in letter i: each (qx-p) for a root p/q comes out
    c = cl(P, (0, 0), i)
    F = []
    while len(c) > 2:
        r = 0
        for q in ds(c[-1]):
            for p in ds(c[0]):
                for s in (p, -p):
                    if not r and gcd(s, q) == 1:
                        r = pdiv(c, [-s, q])
                        if r:
                            F.append([-s, q])
                            c = r
            if r:
                break
        if not r:
            break
    n = 1
    if c[-1] < 0:
        n = -1
        c = [-x for x in c]
    F.append(c)
    o = []
    for f in F:
        t = '(' + es(bk(f, (0, 0), i), 1) + ')'
        for x in o:
            if x[0] == t:
                x[1] += 1
                t = ''
        if t:
            o.append([t, 1])
    o.sort()
    t = ''
    for x in o:
        t += x[0] + ('^' + str(x[1]) if x[1] > 1 else '')
    return (t if len(o) == 1 and o[0][1] == 1 else '(' + t + ')'), n


def ds(n):
    # the numbers that divide n (the first 40)
    o = [1]
    for p in pf(abs(n)):
        for x in o[:]:
            if x * p not in o and len(o) < 40:
                o.append(x * p)
    return o
