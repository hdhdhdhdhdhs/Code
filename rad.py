# RAD - solve square root equations for the Casio fx-9750GIII
#
# Type it the way it is written. The root key types sqrt( :
#   sqrt(5+x)-sqrt(4x+9)=-2
# Close each root's bracket. Brackets still open at the = or at the
# end are closed for you. ^(1/2) and ^0.5 also mean a square root.
# Roots inside roots work too: sqrt(x+sqrt(x+8))=4
#
# How it works, the same as by hand: get a root alone, square both
# sides, and repeat until no roots are left. That leaves a polynomial.
# Its zeros are the only possible answers, but squaring can add fake
# ones, so each is put back into the question. Each zero is pinned
# between two fractions (whole-number maths, no decimal rounding)
# and checked with interval sums to 60+ digits, which can never
# wrongly throw out a real answer.
W = 21
DIG = '0123456789.'
R = []   # radicands: R[i] is what is under root number i


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def isq(n):
    # whole-number square root, rounded down
    if n < 2:
        return n
    if n < 10 ** 30:
        r = int(n ** 0.5) + 1
    else:
        # start above the root, so Newton's steps come down onto it
        r = 1 << (len(str(n)) * 5 // 3 + 2)
    while True:
        s = (r + n // r) // 2
        if s >= r:
            break
        r = s
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r


# ---- expressions: ({(x power, roots mask): number}, divisor)
# A mask bit i means root number i is a factor of that term.
def tidy(c, d):
    for k in list(c):
        if c[k] == 0:
            del c[k]
        elif k[0] > 40:
            raise ValueError('too big')
    g = d
    for k in c:
        g = gcd(g, c[k])
    if d < 0:
        g = -g
    for k in c:
        c[k] //= g
    return (c, d // g)


def pm(a, b):
    # multiply; root i times root i is put back as what is under it
    c = {}
    for i in a:
        for j in b:
            k = (i[0] + j[0], i[1] ^ j[1])
            v = a[i] * b[j]
            m = i[1] & j[1]
            if m:
                t = {k: v}
                n = 0
                while m:
                    if m & 1:
                        t = pm(t, R[n])
                    m >>= 1
                    n += 1
                for q in t:
                    c[q] = c.get(q, 0) + t[q]
            else:
                c[k] = c.get(k, 0) + v
    return c


def mul(a, b):
    return tidy(pm(a[0], b[0]), a[1] * b[1])


def add(a, b, s):
    c = {}
    for k in a[0]:
        c[k] = a[0][k] * b[1]
    for k in b[0]:
        c[k] = c.get(k, 0) + s * b[0][k] * a[1]
    return tidy(c, a[1] * b[1])


def num(t):
    i = t.find('.')
    if t == '.' or (i >= 0 and t.find('.', i + 1) >= 0):
        raise ValueError('bad number')
    if i < 0:
        return tidy({(0, 0): int(t)}, 1)
    f = t[i + 1:]
    return tidy({(0, 0): int(t[:i] + f)}, 10 ** len(f))


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
    if len(Q) == 1 and (0, 0) in Q:
        c = Q[(0, 0)]
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
    i = 0
    while i < len(R) and R[i] != Q:
        i += 1
    if i == len(R):
        if i == 4:
            raise ValueError('over 4 roots')
        R.append(Q)
    return tidy({(0, 1 << i): k}, d)


def tok(s):
    o = []
    i = 0
    while i < len(s):
        j = i + 1
        if s[i] in DIG:
            while j < len(s) and s[j] in DIG:
                j += 1
        elif s[i:i + 4] == 'sqrt':
            j = i + 4
        elif s[i] not in 'x+-*/^()':
            raise ValueError('bad sign ' + s[i])
        o.append(s[i:j])
        i = j
    return o


def need(ts, i, t):
    if i >= len(ts) or ts[i] != t:
        raise ValueError('missing ' + t)
    return i + 1


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
            if not w[0]:
                raise ValueError('divide by 0')
            if len(w[0]) != 1 or (0, 0) not in w[0]:
                raise ValueError('only / by a number')
            w = tidy({(0, 0): w[1]}, w[0][(0, 0)])
        v = mul(v, w)
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
        v = mkrad(v)
    elif t == 'x':
        v = ({(1, 0): 1}, 1)
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return mul(v, ({(0, 0): -1}, 1)), i
    else:
        raise ValueError('bad ' + t)
    # power: whole, or a half (1/2, 0.5, 3/2) for a square root.
    # x2 means x^2: the power can follow x with no ^ in between
    if i < len(ts) and (ts[i] == '^' or (t == 'x' and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        n = e[0].get((0, 0), 0)
        if len(e[0]) != (n != 0) or n < 0 or e[1] > 2 or n > 24 * e[1]:
            raise ValueError('bad power')
        if e[1] == 2:
            v = mkrad(v)
        r = ({(0, 0): 1}, 1)
        for _ in range(n):
            r = mul(r, v)
        v = r
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


# ---- whole-number polynomials, low power first
def prim(c):
    g = 0
    for x in c:
        g = gcd(g, x)
    if c[-1] < 0:
        g = -g
    return [x // g for x in c]


def pdiv(c, d):
    c = c[:]
    n = len(d) - 1
    q = [0] * (len(c) - n)
    for k in range(len(q) - 1, -1, -1):
        t = c[k + n]
        if t % d[n]:
            return None
        t //= d[n]
        q[k] = t
        for j in range(n + 1):
            c[k + j] -= t * d[j]
    for x in c[:n]:
        if x:
            return None
    return q


def sqf(c):
    # c with every repeated factor cut down to one copy
    a = c
    b = prim([i * c[i] for i in range(1, len(c))])
    while b != [0]:
        r = a[:]
        while len(r) >= len(b):
            t = r[-1]
            r = [x * b[-1] for x in r]
            for j in range(len(b)):
                r[len(r) - len(b) + j] -= t * b[j]
            r.pop()
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        a, b = b, (prim(r) if r and r != [0] else [0])
    return pdiv(c, prim(a))


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


def pg(c):
    g = 0
    for x in c:
        g = gcd(g, x)
    return [x // g for x in c]


def sturm(c):
    # Sturm's chain: counts the real zeros between any two points
    S = [c, pg([i * c[i] for i in range(1, len(c))])]
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
        S.append(pg([-x for x in r]))
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


def refine(c, t, bits):
    # halve until the width is 2^-bits of the size; [m, m, k] if exact
    lo, hi, k = t
    if lo == hi:
        return t
    sh = sgn(hz(c, hi, 1 << k))
    if sh == 0:
        return [hi, hi, k]
    while (hi - lo) << bits > max(abs(hi), 1 << k):
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
    # the fraction in (lo, hi] that is a zero, if there is one
    lo, hi, k = t
    if lo == hi:
        g = gcd(hi, 1 << k)
        return (hi // g, (1 << k) // g)
    a = lo + hi
    b = 1 << (k + 1)
    p0, q0, p1, q1 = 0, 1, 1, 0
    while b:
        h = a // b
        a, b = b, a - h * b
        p0, q0, p1, q1 = p1, q1, h * p1 + p0, h * q1 + q0
        if q1 * q1 > (1 << k):
            break
        if lo * q1 < p1 << k <= hi * q1 and hz(c, p1, q1) == 0:
            return (p1, q1)
    return None


def fr(p, q):
    g = gcd(p, q)
    if q < 0:
        g = -g
    p //= g
    q //= g
    return str(p) if q == 1 else str(p) + '/' + str(q)


def mid(t):
    return (t[0] + t[1]) / (1 << (t[2] + 1))


def dec(x):
    t = '%.6g' % x
    if t.find('e') < 0 and t.find('.') >= 0:
        t = t.rstrip('0').rstrip('.')
    return '~' + t


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


def zeros(c):
    # every real zero: [label, (p, q) if a fraction, decimal, interval]
    z = []
    while c[0] == 0:
        c = c[1:]
        if not z:
            z.append(['0', (0, 1), 0.0, None])
    if len(c) < 2:
        return z
    c = prim(sqf(c))
    left = []
    d = c
    for t in isolate(c):
        t = refine(c, t, 64)
        r = ratin(c, t)
        if r:
            z.append([fr(r[0], r[1]), r, r[0] / r[1], None])
            d = pdiv(d, [-r[0], r[1]])
        else:
            left.append(t)
    # what is left after the fractions: one zero is a fraction too,
    # two zeros of a quadratic are written exactly
    if len(d) == 2 and len(left) == 1:
        r = (-d[0], d[1])
        z.append([fr(r[0], r[1]), r, r[0] / r[1], None])
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


def ichk(F, X, sh):
    # 0 if F cannot be 0 anywhere in X (or a root is undefined there)
    V = []
    for P in R:
        a, b = ival(P, X, V, sh)
        if b < 0:
            return 0
        V.append((isq(max(a, 0) << sh), isq(b << sh) + 1))
    a, b = ival(F, X, V, sh)
    return 1 if a <= 0 <= b else 0


def near(F, c, t):
    # check on the interval, then on a far smaller one
    if t[1] is not None:
        p, q = t[1]
        return ichk(F, ((p << 256) // q, -(-(p << 256) // q)), 256)
    u = t[3]
    for b in (64, 200):
        u = refine(c, u, b)
        if not ichk(F, (u[0] << 64, u[1] << 64), u[2] + 64):
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
            t += 'x'
        if i > 1:
            t += '^' + str(i)
        s += ('-' if a < 0 else '+') + t
    if s == '':
        return '0'
    return s[1:] if s[0] == '+' else s


def span(a, b):
    if b is None:
        return 'x>=' + a if a else 'every x'
    if not a:
        return 'x<=' + b
    return 'x=' + a if a == b else a + '<=x<=' + b


def rng(F):
    # F = A + B*root, and A^2 = B^2*(under the root) for every x: then
    # F = 0 exactly where A*B <= 0. Walk its zeros left to right.
    q = [0] * 81
    for i in F:
        for j in F:
            if i[1] < j[1]:
                q[i[0] + j[0]] += F[i] * F[j]
    while q[-1] == 0:
        q.pop()
    z = zeros(q)
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
    return ['Ans: ' + (', '.join(o) if o else 'no solution')]


def solve(s):
    s = s.lower().replace(' ', '').replace('math.', '').replace('**', '^')
    while R:
        R.pop()
    j = s.find('=')
    if j < 0:
        s += '=0'
        j = s.find('=')
    F0 = add(side(s[:j]), side(s[j + 1:]), -1)[0]
    if not F0:
        return ['Both sides match:', 'every x works where', 'the roots are defined']
    F = F0
    n = 0
    while True:
        m = 0
        for k in F:
            m |= k[1]
        if not m:
            break
        # take the last root made (an outer one before what is inside
        # it): F = A + B*root, so A = -B*root, and squaring gives
        # A^2 = B^2*(what is under the root)
        i = 0
        while m >> (i + 1):
            i += 1
        b = 1 << i
        A = {}
        Bp = {}
        for k in F:
            if k[1] & b:
                Bp[(k[0], k[1] ^ b)] = F[k]
            else:
                A[k] = F[k]
        F = add((pm(A, A), 1), (pm(pm(Bp, Bp), R[i]), 1), -1)[0]
        n += 1
        if F:
            F = tidy(F, 0)[0]
    o = ['Squared %d time%s:' % (n, 's' * (n > 1))] if n else []
    if not F:
        if n == 1 and len(R) == 1 and not [k for k in R[0] if k[1]]:
            return o + ['Gives 0=0: a range'] + rng(F0)
        return o + ['0=0: a whole range', 'of x may work,', 'check by hand']
    d = 0
    for k in F:
        d = max(d, k[0])
    c = prim([F.get((i, 0), 0) for i in range(d + 1)])
    t = pstr(c) + '=0'
    # more than 3 lines of numbers helps no one: just say how big
    if d:
        o.append(t if len(t) <= 3 * W else 'Degree ' + str(d) + ' polynomial')
    z = zeros(c) if d else []
    cz = prim(sqf(c)) if d else c
    a = []
    for t in z:
        k = near(F0, cz, t)
        x = 'x' + ('' if t[0][0] == '~' else '=') + t[0]
        o.append(x + (' works' if k else ' fails'))
        if k:
            a.append(x)
    o.append('Ans: ' + (', '.join(a) if a else 'no solution'))
    return o


def cut(t):
    for i in range(W, 0, -1):
        if t[i] == ' ':
            return i
    for i in range(W, 0, -1):
        if t[i - 1] in '),:' and t[i] != ')':
            return i
    for i in range(W, 0, -1):
        if t[i] in '+-':
            return i
    return W


def wrap(t):
    o = []
    while len(t) > W:
        j = cut(t)
        o.append(t[:j].rstrip())
        t = t[j:].lstrip()
    o.append(t)
    return o


print('Root equations. Like')
print('sqrt(5+x)-sqrt(4x+9)')
print('=-2')
s = ''
while True:
    if s == '':
        try:
            s = input('Eqn:').strip()
        except (KeyboardInterrupt, EOFError):
            break
        if s == '':
            continue
    try:
        out = solve(s)
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    s = ''
    ls = []
    for ln in out:
        ls += wrap(ln)
    try:
        for i in range(len(ls)):
            # typing a new one at more.. skips the rest and solves it
            if i and i % 6 == 0:
                s = input('more..').strip()
                if s:
                    break
            print(ls[i])
    except (KeyboardInterrupt, EOFError):
        break
