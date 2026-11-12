# RADSIMP - the simplifying half of rad.py, for the Casio fx-9750GIII
#
# Keep this file on the calculator next to rad.py, and run rad.py: when
# what is typed has no =, rad.py loads this file and calls go(). It is
# its own file because the calculator's compiler holds the parse tree of
# a whole file at once, and both halves together are too big for it;
# loaded one after the other they fit. In rad.py the root key types
# sqrt( :
#   25/sqrt(2)                  gives 25sqrt(2)/2
#   sqrt(15)(3sqrt(5)-sqrt(3))  gives 15sqrt(3)-3sqrt(5)
#   6/(2+sqrt(3))               gives 12-6sqrt(3)
#   sqrt(12a^2b^3)              gives 2absqrt(3b)
# It takes squares out (sqrt(72) = 6sqrt(2)), puts roots together
# (sqrt(15)sqrt(5) = 5sqrt(3)), adds like roots, and clears roots out
# of the bottom: times the root when the bottom is one term, times the
# conjugate when it has a + or -, and it shows what it multiplied by.
# Letters are taken as >= 0, as in textbooks; a bottom like x-4 is
# left as it is.
W = 21
DIG = '0123456789.'
LET = 'abcdefghijklmnopqrstuvwxyz'
R = []   # roots: R[i] is what is under root number i (each prime and
         # each letter left inside gets its own, so they combine)
L = []   # letters, in the order they first appear
U = []   # letters taken >= 0
ST = []  # what the bottom was multiplied by, top and bottom


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


# ---- expressions: ({(letter powers, roots mask): number}, divisor)
# Letter number i has its power in 8 bits at 256^i (it can be below 0
# when simplifying), so multiplying adds them. When solving there is
# one letter, so that is just its power. A mask bit i means root
# number i is a factor of that term.
def dg(m):
    # the powers of each letter, in order
    o = []
    while m:
        e = (m + 128) % 256 - 128
        o.append(e)
        m = (m - e) >> 8
    return o


def tidy(c, d):
    for k in list(c):
        if c[k] == 0:
            del c[k]
        else:
            for e in dg(k[0]):
                if e > 40 or e < -40:
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
    for k in Q:
        c = Q[k]
    if len(Q) == 1 and not k[1] and c > 0:
        # one term: squares come out, and each prime and each letter
        # left inside gets a root of its own, so they always combine
        r = 1
        m = 0
        f = 2
        while f < 1000 and f * f <= c:
            while c % (f * f) == 0:
                c //= f * f
                r *= f
            if c % f == 0:
                c //= f
                m |= sym({(0, 0): f})
            f += 1
        if c > 1:
            h = isq(c)
            if h * h == c:
                r *= h
            else:
                m |= sym({(0, 0): c})
        o = 0
        e = dg(k[0])
        for i in range(len(e)):
            if e[i]:
                if L[i] not in U:
                    U.append(L[i])
                o += (e[i] >> 1) << (8 * i)
                if e[i] & 1:
                    m |= sym({(1 << (8 * i), 0): 1})
        return tidy({(o, m): r}, d)
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
        elif s[i] not in LET and s[i] not in '+-*/^()':
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
            w, v = rat(w, v)
        v = mul(v, w)
    return v, i


def rat(w, v):
    # 1/w, after clearing the roots out of w: top and bottom times
    # its conjugate (or just the root, when w is one term)
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
    for k in a:
        for e in dg(k[0]):
            if e < 0:
                return None
    p = 0
    for k in P:
        p = max(p, k[0])
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
    # power: whole, or a half (1/2, 0.5, 3/2) for a square root.
    # x2 means x^2: the power can follow a letter with no ^ between
    if i < len(ts) and (ts[i] == '^' or (t in LET and ts[i][0] in DIG)):
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


def dec(x):
    t = '%.6g' % x
    if t.find('e') < 0 and t.find('.') >= 0:
        t = t.rstrip('0').rstrip('.')
    return '~' + t


def cut(t):
    for i in range(W, 8, -1):
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


# ---- simplifying: writing it out
def mo(e, g):
    # the letters with power above 0 (g=1) or below 0 (g=-1)
    s = ''
    e = dg(e)
    for i in range(len(e)):
        if e[i] * g > 0:
            s += L[i] + ('^' + str(e[i] * g) if e[i] * g > 1 else '')
    return s


def bt(q, m):
    # a bottom: q times the letters with power below 0, in brackets
    # when it is more than one thing
    b = (str(q) if q > 1 else '') + mo(m, -1)
    h = q > 1
    for e in dg(m):
        h += e < 0
    return '(' + b + ')' if h > 1 else b


def tm(k, n, q):
    # one term, n/q times the letters and roots in k, with its sign
    s = 1
    i = 0
    o = ''
    m = k[1]
    j = 0
    while m:
        if m & 1:
            P = R[j]
            for t in P:
                pass
            if len(P) == 1 and t == (0, 0):
                s *= P[t]
            elif len(P) == 1 and not t[1] and P[t] == 1:
                i += t[0]
            else:
                o += 'sqrt(' + es(P, 1) + ')'
        m >>= 1
        j += 1
    t = mo(k[0], 1)
    if s > 1 or i:
        t += 'sqrt(' + (str(s) if s > 1 else '') + mo(i, 1) + ')'
    t += o
    t = (str(abs(n)) if abs(n) != 1 or not t else '') + t
    b = bt(q, k[0])
    return ('-' if n < 0 else '+') + t + ('/' + b if b else '')


def ng(m):
    # just the letters with power below 0
    o = 0
    e = dg(m)
    for i in range(len(e)):
        if e[i] < 0:
            o += e[i] << (8 * i)
    return o


def es(c, d):
    # an expression as text: highest power first, roots of numbers
    # and letters written as one root, a shared bottom taken out
    if not c:
        return '0'
    t = []
    for k in c:
        h = 0
        for e in dg(k[0]):
            h += e
        m = k[1]
        j = 0
        while m:
            if m & 1:
                for x in R[j]:
                    if len(R[j]) == 1 and x[0] and not x[1]:
                        h += 0.5
            m >>= 1
            j += 1
        t.append((-h, k[1] != 0, k[1], k[0], k))
    t.sort()
    # start with a + term when there is one: 1-x, not -x+1
    for x in t:
        if c[x[4]] > 0:
            t.remove(x)
            t.insert(0, x)
            break
    if len(c) == 1:
        k = t[0][4]
        g = gcd(c[k], d)
        s = tm(k, c[k] // g, d // g)
    else:
        z = ng(t[0][4][0])
        for x in t:
            if ng(x[4][0]) != z:
                z = 0
        s = ''
        for x in t:
            k = x[4]
            s += tm((k[0] - z, k[1]), c[k], 1)
        b = bt(d, z)
        if b:
            s = '(' + (s[1:] if s[0] == '+' else s) + ')/' + b
    return s[1:] if s[0] == '+' else s


def fv(c):
    # the value in decimals, None if a root is of something below 0
    s = 0.0
    for k in c:
        t = float(c[k])
        m = k[1]
        j = 0
        while m:
            if m & 1:
                x = fv(R[j])
                if x is None or x < 0:
                    return None
                t *= x ** 0.5
            m >>= 1
            j += 1
        s += t
    return s


def simp(v):
    c, d = v
    o = ['Restr: ' + ', '.join([x + '>=0' for x in U])] if U else []
    o.append('Ans: ' + es(c, d))
    m = 0
    for k in c:
        m |= k[1]
    if not L and (m or d > 1):
        x = fv(c)
        if x is not None:
            o.append(dec(x / d))
    for c in ST:
        t = es(c, 1)
        if len(c) > 1:
            t = '(' + t + ')'
        o.append('Times ' + t + '/' + t)
    return o

def go(s):
    s = s.lower().replace(' ', '').replace('math.', '').replace('**', '^')
    for t in (R, L, U, ST):
        while t:
            t.pop()
    if s.find('=') >= 0:
        raise ValueError('=: rad.py solves')
    return simp(side(s))

