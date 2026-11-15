# ALGEQ3 - equations, part 3: putting the zeros back in, restrictions,
# NPVs and the answer lines (see algebra.py)
from algeq1 import *
from algeq2 import *
V = 'x'  # the letter being solved for


# ---- putting an answer back in
def imul(A, Bv, sh):
    t = (A[0] * Bv[0], A[0] * Bv[1], A[1] * Bv[0], A[1] * Bv[1])
    return (min(t) >> sh, -(-max(t) >> sh))


def ival(P, X, V, sh):
    # the range of P for x in X, as whole numbers over 2^sh
    s0 = 0
    s1 = 0
    for k in P:
        a = (P[k] << sh, P[k] << sh)
        for _ in range(k[0]):
            a = imul(a, X, sh)
        m = k[1]
        n = 0
        while m:
            if m & 1:
                a = imul(a, V[n], sh)
            m >>= 1
            n += 1
        s0 += a[0]
        s1 += a[1]
    return s0, s1


def ichk(F, X, sh, m=-1):
    # 0 if F cannot be 0 anywhere in X (or a root in mask m is undefined
    # there)
    V = []
    for P in R:
        a, b = ival(P, X, V, sh)
        if b < 0:
            if m >> len(V) & 1:
                return 0
            a = b = 0
        V.append((isq(max(a, 0) << sh), isq(b << sh) + 1))
    a, b = ival(F, X, V, sh)
    return 1 if a <= 0 <= b else 0


def near(F, c, t, m=-1):
    # check on the interval, then on a far smaller one
    if t[1] is not None:
        p, q = t[1]
        return ichk(F, ((p << 256) // q, -(-(p << 256) // q)), 256, m)
    u = t[3]
    for b in (64, 200):
        u = refine(c, u, b)
        if not ichk(F, (u[0] << 64, u[1] << 64), u[2] + 64, m):
            return 0
    return 1


def pstr(c):
    s = ''
    for i in range(len(c) - 1, -1, -1):
        a = c[i]
        if a == 0:
            continue
        t = str(abs(a))
        if i and abs(a) == 1:
            t = ''
        if i:
            t += V
        if i > 1:
            t += '^' + str(i)
        s += ('-' if a < 0 else '+') + t
    if s == '':
        return '0'
    return s[1:] if s[0] == '+' else s


def span(a, b):
    if b is None:
        return V + '>=' + a if a else 'every ' + V
    if not a:
        return V + '<=' + b
    return V + '=' + a if a == b else a + '<=' + V + '<=' + b


def le0(q):
    # where q <= 0, as pieces: walk its zeros left to right
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    z = zeros(q) if len(q) > 1 else []
    k = len(z)
    v = []
    for j in range(k + 1):
        x = 0.0
        if k:
            x = z[0][2] - 1 if j == 0 else z[j - 1][2] + 1
        if 0 < j < k:
            x = (z[j - 1][2] + z[j][2]) / 2
        v.append(sgn(hz(q, int(x * (1 << 40)), 1 << 40)) < 0)
    o = []
    a = '' if v[0] else None
    for j in range(k):
        if a is None:
            a = z[j][0]
        if not v[j + 1]:
            o.append(span(a, z[j][0]))
            a = None
    if a is not None:
        o.append(span(a, None))
    return o


def rng(F):
    # F = A + B*root, and A^2 = B^2*(under the root) for every x: then
    # F = 0 exactly where A*B <= 0
    q = [0] * 81
    for i in F:
        for j in F:
            if i[1] < j[1]:
                q[i[0] + j[0]] += F[i] * F[j]
    return le0(q)


def restr():
    # what under each root needs: >= 0 (roots inside roots are left out)
    o = []
    for P in R:
        d = 0
        for k in P:
            if k[1]:
                d = -1
                break
            d = max(d, k[0])
        if d > 0:
            t = ' or '.join(le0([-P.get((i, 0), 0) for i in range(d + 1)]))
            if t != 'every ' + V and t not in o:
                o.append(t or 'no ' + V)
    return ['Restr: ' + ', '.join(o)] if o else []

def pz(F):
    # F (no roots left) as a polynomial, and its zeros
    d = 0
    for k in F:
        d = max(d, k[0])
    c = prim([F.get((i, 0), 0) for i in range(d + 1)])
    cz = prim(sqf(c)) if d else c
    return c, cz, zeros(cz, 0) if d else []


def npv():
    # the NPVs: where a bottom is 0 (and its roots are all there),
    # found the same way as the answers
    o = []
    for P in B:
        F, n = elim(P)
        if not F:
            return ['NPV: a range, check by hand']
        c, cz, z = pz(F)
        # only the roots in this bottom need to be there
        m = 0
        for k in P:
            m |= k[1]
        for j in range(len(R) - 1, -1, -1):
            if m >> j & 1:
                for k in R[j]:
                    m |= k[1]
        for t in z:
            if near(P, cz, t, m) and t not in o:
                o.append(t)
    o.sort(key=lambda t: t[2])
    z = []
    for t in o:
        if t[0] not in z:
            z.append(t[0])
    return ['NPV: ' + V + '!=' + ','.join(z)] if z else []


def solve(s):
    global V
    for t in (R, L, B):
        while t:
            t.pop()
    j = s.find('=')
    a = side(s[:j])
    b = side(s[j + 1:])
    # top/bottom = top/bottom, multiplied through by the lowest common
    # bottom
    F0 = ad(a, b, -1)[0][0]
    if len(L) > 1:
        raise ValueError('one letter only')
    V = L[0] if L else 'x'
    r = restr()
    h = r + npv()
    if not F0:
        return h + ['Ans: every ' + V + (' in Restr' if r else '') + (' but NPV' if len(h) > len(r) else '')]
    F, n = elim(F0)
    o = ['Squared %d time%s:' % (n, 's' * (n > 1))] if n else []
    if not F:
        if n == 1 and len(R) == 1 and not [k for k in R[0] if k[1]]:
            a = rng(F0)
            return h + ['Ans: ' + (', '.join(a) if a else 'no solution')] + o + ['Gives 0=0: a range']
        return h + o + ['0=0: a whole range', 'of ' + V + ' may work,', 'check by hand']
    c, cz, z = pz(F)
    d = len(c) - 1
    t = pstr(c) + '=0'
    # more than 3 lines of numbers helps no one: just say how big
    o.append(t if len(t) <= 3 * W else 'Degree ' + str(d) + ' polynomial'
             if d else 'Never equal')
    # answers first, then the ones that fail, then the working
    a = []
    f = []
    for t in z:
        u = near(F0, cz, t)
        for P in B:
            u = u and not near(P, cz, t)
        t = (a if u else f, V + ('' if t[0][0] == '~' else '=') + t[0])
        if t[1] not in t[0]:  # two zeros too close to tell apart: once
            t[0].append(t[1])
    h.append('Ans: ' + (', '.join(a) if a else 'no solution'))
    if f:
        h.append('Fails: ' + ', '.join(f))
    return h + o


def rn(s, a):
    # for simplifying with roots, one letter: what each root needs
    # (>= 0) and the NPVs, from reading it in as one side of an equation;
    # then the values that make one of the answer's bottoms (list a) 0
    global V
    for t in (R, L, B):
        while t:
            t.pop()
    side(s)
    if len(L) != 1:
        return [], []
    V = L[0]
    r = restr()
    n = npv()
    k = len(B)
    for t in a:
        try:
            side('1/(' + t + ')')
        except ValueError:
            pass
    del B[:k]
    return r[0][7:].split(', ') if r else [], n, npv() if B else []
