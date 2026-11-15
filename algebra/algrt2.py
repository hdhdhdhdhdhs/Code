# ALGRT2 - simplifying with roots, part 2: factoring whole numbers,
# squares of sums, and writing the answer (see algebra.py)
from algrt1 import *


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
    return '(' + b + ')' if h > 1 or d0(b) else b


def d0(t):
    # a power not inside brackets: x^3, (x-4)^2, but not sqrt(x^2-4x)
    d = 0
    for c in t:
        d += (c == '(') - (c == ')')
        if c == '^' and d == 0:
            return 1
    return 0


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
    if b and d0(t):
        # x^3/2 could be read as x^(3/2): (x^3)/2
        t = '(' + t + ')'
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
        # what comes out as one bottom: the lowest power of each letter
        # below 0, and a bottom like (x-4) when every term has it
        e = [0] * len(L)
        h = [-99] * len(L)
        for x in t:
            f = dg(x[5][0]) + [0] * len(L)
            for i in range(len(L)):
                e[i] = min(e[i], f[i])
                h[i] = max(h[i], f[i])
        z = 0
        for i in range(len(L)):
            if L[i][0] == '(' and e[i] < h[i]:
                # not in every term the same: each term on its own
                z = 0
                break
            z += e[i] << (8 * i)
        # a term left with a bottom like (x-4) of its own: each term
        # over its own number too, x/2+sqrt(x)/(x-4)
        n = 0
        for x in t:
            f = dg(x[5][0] - z)
            for i in range(len(f)):
                n |= f[i] < 0 and L[i][0] == '('
        s = ''
        for x in t:
            k = x[5]
            g = gcd(c[k], d) if n else 1
            s += tm((k[0] - z, k[1]), c[k] // g, d // g if n else 1)
        b = '' if n else bt(d, z)
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
