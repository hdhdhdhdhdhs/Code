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
# Under a root, what every term shares comes out (sqrt(x^3+x^2) =
# xsqrt(x+1)), a square of a sum comes out (sqrt(x^2+6x+9) = x+3, or
# |x-3| for sqrt(x^2-6x+9)), and sqrt(4+2sqrt(3)) = 1+sqrt(3).
# Letters are taken as >= 0, as in textbooks; a bottom like x-4 is
# left as it is.
#
# rad.py lends this file the helpers both need (gcd, mul, add ...), so
# they are only compiled once.
W = 21
DIG = '0123456789.'
LET = 'abcdefghijklmnopqrstuvwxyz'
R = []   # roots: R[i] is what is under root number i (each prime and
         # each letter left inside gets its own, so they combine)
L = []   # letters, in the order they first appear
U = []   # letters taken >= 0
ST = []  # what the bottom was multiplied by, top and bottom


# ---- expressions: ({(letter powers, roots mask): number}, divisor)
# Letter number i has its power in 8 bits at 256^i (it can be below 0
# when simplifying), so multiplying adds them. When solving there is
# one letter, so that is just its power. A mask bit i means root
# number i is a factor of that term.


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


def sq(P):
    # p with p*p = P, or None: P a sum of whole numbers times letters
    # (no roots, no bottoms), p found biggest power first
    for k in P:
        if k[1]:
            return None
        e = dg(k[0])
        for i in range(len(e)):
            if e[i] < 0 or (e[i] and L[i][0] == '('):
                return None
    K = max(P)
    c = P[K]
    r = isq(c) if c > 0 else 0
    for e in dg(K[0]):
        if e & 1:
            r = 0
    if len(P) < 2 or r * r != c:
        return None
    h = K[0] // 2
    p = {(h, 0): r}
    for _ in range(2 * len(P)):
        D = dict(P)
        X = pm(p, p)
        for k in X:
            D[k] = D.get(k, 0) - X[k]
            if not D[k]:
                del D[k]
        if not D:
            return p
        K = max(D)
        n = K[0] - h
        q, w = divmod(D[K], 2 * r)
        if w or (n, 0) in p:
            return None
        for e in dg(n):
            if e < 0 or e > 40:
                return None
        p[(n, 0)] = q
    return None


def pm2(a, e, n):
    # a^e mod n (pow with three numbers may be missing)
    r = 1
    a %= n
    while e:
        if e & 1:
            r = r * a % n
        a = a * a % n
        e >>= 1
    return r


def pr(n):
    # n is prime (Miller-Rabin, exact below 3*10^24)
    d = n - 1
    k = 0
    while d % 2 == 0:
        d //= 2
        k += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pm2(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(k - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rho(n):
    # a factor of n (n is not prime), Pollard's rho; 0 if it takes long
    c = 1
    while c < 4:
        x = 2
        y = 2
        g = 1
        k = 0
        while g == 1 and k < 3000:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            g = gcd(x - y, n)
            k += 1
        if 1 < g < n:
            return g
        c += 1
    return 0


def pf(c):
    # the primes of c, each as often as it divides c. Small ones by
    # trying them; big ones (up to 10^30) split by Pollard's rho, so
    # roots of numbers like 1009*1013 still combine with sqrt(1009)
    o = []
    f = 2
    while f < 1000 and f * f <= c:
        while c % f == 0:
            o.append(f)
            c //= f
        f += 1
    st = [c] if c > 1 else []
    while st:
        n = st.pop()
        h = isq(n)
        if h * h == n:
            st += [h, h]
        elif n < 1000000 or n > 10 ** 30 or pr(n):
            o.append(n)
        else:
            g = rho(n)
            if g:
                st += [g, n // g]
            else:
                o.append(n)
    return o


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


# ---- simplifying: writing it out
def ab():
    # letter numbers in a-z order, bottoms like (x-4) last
    return sorted(range(len(L)), key=lambda i: (L[i][0] == '(', L[i]))


def ak(m):
    # powers in a-z order, for sorting: x^2 before xy before y^2
    e = dg(m)
    return tuple([-(e[i] if i < len(e) else 0) for i in ab()])


def mo(e, g):
    # the letters with power above 0 (g=1) or below 0 (g=-1), a-z
    s = ''
    e = dg(e)
    for i in ab():
        if i < len(e) and e[i] * g > 0:
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


def rp(m):
    # the roots in mask m: the number under them, the letters under
    # them, and the roots of sums
    s = 1
    i = 0
    o = []
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
                o.append(P)
        m >>= 1
        j += 1
    return s, i, o


def rt(o):
    # roots of sums as text; one that is a square is written |x-3|
    t = ''
    for P in o:
        p = sq(P)
        t += '|' + es(p, 1) + '|' if p else 'sqrt(' + es(P, 1) + ')'
    return t


def tm(k, n, q):
    # one term, n/q times the letters and roots in k, with its sign
    s, i, o = rp(k[1])
    t = mo(k[0], 1)
    if (s > 1 or i) and len(o) == 1 and not sq(o[0]):
        # sqrt(2)sqrt(x+1) is written sqrt(2x+2)
        P = pm(o[0], {(i, 0): s})
        for x in P:
            if x[1] or mo(x[0], 1).find('(') >= 0:
                P = 0
        if P:
            o = [P]
            s = 1
            i = 0
    if s > 1 or i:
        x = (str(s) if s > 1 else '') + mo(i, 1)
        t += 'sqrt(' + (x[1:-1] if x[0] == '(' and x in L else x) + ')'
    t += rt(o)
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
    # highest power first (a letter under a root counts a half), then
    # the smallest number under the root: 2+sqrt(2)+sqrt(3)+sqrt(10)
    t = []
    for k in c:
        h = 0
        for e in dg(k[0]):
            h += e
        s, i, o = rp(k[1])
        for e in dg(i):
            h += e / 2
        t.append((-h, s, ak(i), rt(o), ak(k[0]), k))
    t.sort()
    # start with a + term when there is one: 1-x, not -x+1
    for x in t:
        if c[x[5]] > 0:
            t.remove(x)
            t.insert(0, x)
            break
    if len(c) == 1:
        k = t[0][5]
        g = gcd(c[k], d)
        s = tm(k, c[k] // g, d // g)
    else:
        z = ng(t[0][5][0])
        for x in t:
            if ng(x[5][0]) != z:
                z = 0
        s = ''
        for x in t:
            k = x[5]
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
    o = ['Restr: ' + ', '.join([x[1:-1] + '>0' if x[0] == '(' else x + '>=0' for x in sorted(U)])] if U else []
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

def go(s, G):
    # rad.py lends this half its tools (the same code would be in both
    # files) and its list of roots, so the calculator compiles them once
    g = globals()
    for k in ('gcd', 'isq', 'dg', 'tidy', 'pm', 'mul', 'add', 'num', 'tok', 'need', 'dec', 'R'):
        g[k] = G[k]
    s = s.lower().replace(' ', '').replace('math.', '').replace('**', '^')
    for t in (R, L, U, ST):
        while t:
            t.pop()
    if s.find('=') >= 0:
        raise ValueError('=: rad.py solves')
    return simp(side(s))

