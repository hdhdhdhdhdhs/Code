# ALGCORE - what every part of ALGEBRA shares (see algebra.py)
#
# Numbers with roots in them: an expression is ({(letter powers, roots
# mask): whole number}, divisor). Letter i's power is 8 bits at 256^i
# (below 0 too). Bit j of the mask is the square root of R[j]; a root
# squared is what is under it, so no root appears twice in a term.
W = 21
DIG = '0123456789.'
LET = 'abcdefghijklmnopqrstuvwxyz'
R = []   # radicands: R[i] is what is under root number i
L = []   # letters, in the order typed


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


# ---- one-letter polynomials: whole numbers, low power first
def prim(c, s=1):
    # c over what its numbers share; s=1: top power's number > 0
    g = 0
    for x in c:
        g = gcd(g, x)
    if s and c[-1] < 0:
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


def pg(a, b):
    # what a and b share (low power first), its top number > 0
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
    return prim(a)


def sqf(c):
    # c with every repeated factor cut down to one copy
    return pdiv(c, pg(c, prim([i * c[i] for i in range(1, len(c))])))


# ---- the screen is 21 wide
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
        if t[i - 1] in '),:;' and t[i] != ')':
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


def st(t):
    # x^2y could be read as x^(2y): x^2*y, and the same before sqrt( or (
    o = ''
    p = 0
    for c in t:
        if p == 2 and (c in LET or c == '('):
            o += '*'
        p = 1 if c == '^' else 2 if p and c in DIG else 0
        o += c
    return o


def free(k):
    # put away the parts whose names start with one of k (each is loaded
    # again when it is needed)
    try:
        import sys
        for m in list(sys.modules):
            if m[:5] in k:
                del sys.modules[m]
        import gc
        gc.collect()
    except Exception:
        pass


def go(s):
    # which part answers it: = solves; roots simplify one way, and
    # everything else (numbers, letters, fractions) the other
    s = s.lower().replace(' ', '').replace('math.', '').replace('**', '^')
    try:
        return go1(s)
    except MemoryError:
        # out of memory: put every part away (each is loaded again when
        # needed) and try once more
        free(('algeq', 'algfr', 'algrt', 'algfc'))
        return go1(s)


def go1(s):
    if '=' in s:
        from algeq3 import solve
        return solve(s)
    if 'sqrt' not in s:
        from algfr3 import go as g
        try:
            return g(s)
        except ValueError as e:
            # a power like ^(1/2) or ^0.5 is a root
            if str(e) != 'bad power':
                raise
    from algrt3 import go as g
    return g(s)
