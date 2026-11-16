# ALGFC - the steps for factoring a polynomial typed alone, from fac.py
# (see algebra.py): GCF, take out -1, ax^2+bx+c the slide-and-divide way
# (Multiply, Add, the pair, Slide, divide by a), whole-number zeros
# divided out of bigger ones, the rest split into the factors the
# fraction part found; then the factors and the zeros. Its letters are
# x (and y), and written back after. Polynomials: numbers, low power
# first (with y: by the power of x, every term the same total power)
from algcore import gcd, pdiv, isq


def dvs(n):
    n = abs(n)
    o = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            o.append(d)
            if d * d != n:
                o.append(n // d)
        d += 1
    return o

def ev(c, x):
    # the calculator has no reversed(), so count down by index
    s = 0
    for i in range(len(c) - 1, -1, -1):
        s = s * x + c[i]
    return s

def root(c):
    # a zero p/q needs q-p to divide c(1) and q+p to divide c(-1):
    # a quick way past most of the candidates before dividing
    a = ev(c, 1)
    b = ev(c, -1)
    r = []
    for q in dvs(c[-1]):
        for p in dvs(c[0]):
            for p in (p, -p):
                if ((q == p or a % (q - p) == 0) and
                        (q == -p or b % (q + p) == 0) and gcd(p, q) == 1):
                    r.append((p, q))
    r.sort(key=lambda t: (abs(t[0]) / t[1], t[0] < 0))
    for p, q in r:
        if pdiv(c, [-p, q]) is not None:
            return [-p, q]
    return None

def pstr(c, Y=0):
    # Y: write it with y, every term the same total power
    s = ''
    n = len(c) - 1
    for i in range(n, -1, -1):
        a = c[i]
        if a == 0:
            continue
        e = n - i if Y else 0
        t = str(abs(a))
        if (i or e) and abs(a) == 1:
            t = ''
        if i:
            t += 'x' + ('^' + str(i) if i > 1 else '')
        if e:
            t += 'y' + ('^' + str(e) if e > 1 else '')
        s += ('-' if a < 0 else '+') + t
    if s == '':
        return '0'
    return s[1:] if s[0] == '+' else s

def fr(n, d):
    g = gcd(n, d)
    if d < 0:
        g = -g
    n //= g
    d //= g
    return str(n) if d == 1 else str(n) + '/' + str(d)

def lin(p, a, Y):
    t = str(abs(p))
    if Y:
        t = ('' if t == '1' else t) + 'y'
    return ('(x' + ('+' if p > 0 else '-') + t +
            ('/' + str(a) if a != 1 else '') + ')')

def surd(c, z):
    # zeros of a quadratic with no whole-number pair
    C, B, A = c
    D = B * B - 4 * A * C
    if D < 0:
        return
    s = 1
    i = 2
    while i < 1000 and i * i <= D:
        while D % (i * i) == 0:
            D //= i * i
            s *= i
        i += 1
    g = gcd(gcd(B, s), 2 * A)
    b = -B // g
    s //= g
    a = 2 * A // g
    r = (str(s) if s > 1 else '') + 'sqrt(' + str(D) + ')'
    for k in ('+', '-'):
        t = (str(b) + k if b else ('-' if k == '-' else '')) + r
        if a != 1:
            t = ('(' + t + ')' if b else t) + '/' + str(a)
        z.append(t)

def slide(c, o, F, Y):
    C, B, A = c
    N = A * C
    o.append('Multiply:' + ('ac=' if A != 1 else '') + str(N) +
             ' Add:' + str(B))
    # the pair is (B -+ r)/2 with r*r = B*B-4N, so there is no search
    D = B * B - 4 * N
    r = isq(D) if D >= 0 else -1
    if r < 0 or r * r != D:
        o.append('No pair works')
        F.append(c)
        return
    p = (B - r) // 2
    q = (B + r) // 2
    o.append(str(p) + ' and ' + str(q))
    if A != 1:
        o.append('Slide:' + lin(p, 1, Y) + lin(q, 1, Y))
        o.append('/' + str(A) + ':' + lin(p, A, Y) + lin(q, A, Y))
    for t in (p, q):
        g = gcd(t, A)
        F.append([t // g, A // g])


def fac2(P, d, Q):
    j = 99
    n = 0
    for k in P:
        j = min(j, k[1])
        n = max(n, k[0])
    # with y: take out the y every term shares; what is left must have the
    # same total power in every term, and is factored as if y were 1
    Y = 0
    t = -1
    for k in P:
        if k[1] > j:
            Y = 1
        if t == -1:
            t = k[0] + k[1]
        elif k[0] + k[1] != t:
            t = -2
    if Y and t < 0:
        raise ValueError('x,y powers mixed')
    c = [0] * (n + 1)
    for k in P:
        c[k[0]] = P[k]
    yk = (t - n if Y else j) if P else 0
    if len(c) < 2 and not yk:
        return ['No x to factor']
    g = 0
    for x in c:
        g = gcd(g, x)
    if c[-1] < 0:
        g = -g
    c = [x // g for x in c]
    for x in c:
        if abs(x) > 10 ** 9:
            raise ValueError('numbers too big')
    if len(c) > 13:
        raise ValueError('power over 12')
    m = 0
    while c[0] == 0:
        c.pop(0)
        m += 1
    h = fr(g, d)
    if h == '1':
        h = ''
    elif h == '-1':
        h = '-'
    elif '/' in h:
        h = '(' + h + ')'
    if m:
        h += 'x' + ('^' + str(m) if m > 1 else '')
    if yk:
        h += 'y' + ('^' + str(yk) if yk > 1 else '')
    o = []
    if h == '-':
        o.append('Take out -1')
    elif h:
        o.append('GCF: ' + h.replace('(', '').replace(')', ''))
    if h and len(c) > 1:
        o.append(h + '(' + pstr(c, Y) + ')')
    F = []
    while len(c) > 3:
        f = root(c)
        if f is None:
            break
        k = 0
        while len(c) > 3 and pdiv(c, f) is not None:
            c = pdiv(c, f)
            F.append(f)
            k += 1
        if not Y:
            o.append('x=' + fr(-f[0], f[1]) + ' gives 0')
        o.append('/(' + pstr(f, Y) + ')' + ('^' + str(k) if k > 1 else '') +
                 '=' + pstr(c, Y))
    # no whole-number zeros left: it splits into the fraction part's
    # factors (each a power 2 or more)
    sp = 0
    for f in Q:
        while len(c) > 4 and len(c) > len(f) > 2 and pdiv(c, f) is not None:
            o.append('Splits:(' + pstr(f, Y) + ')(' + pstr(pdiv(c, f), Y) + ')')
            c = pdiv(c, f)
            F.append(f)
            sp = 1
    if len(c) == 3 and not sp:
        slide(c, o, F, Y)
    elif len(c) > 1:
        F.append(c)
    # answer: the same factor twice is written as a square
    u = []
    for f in F:
        for e in u:
            if e[0] == f:
                e[1] += 1
                break
        else:
            u.append([f, 1])
    a = h
    for f, k in u:
        t = pstr(f, Y)
        if h or len(u) > 1 or k > 1:
            t = '(' + t + ')'
        a += t + ('^' + str(k) if k > 1 else '')
    if len(u) == 1 and u[0][1] == 1 and not h and len(u[0][0]) > 2:
        o.append('Prime: no factors')
    else:
        o.append('Ans:' + a)
    if Y or yk:
        return o
    z = ['0'] if m else []
    for f, k in u:
        if len(f) == 2:
            z.append(fr(-f[0], f[1]))
        elif len(f) == 3:
            surd(f, z)
        else:
            from algfc2 import units
            for e in units(f):
                if e[0] == 1:
                    t = '%.4f' % -e[1][0]
                    z.append('~' + (t.rstrip('0').rstrip('.') or '0'))
    o.append('Zeros: ' + ', '.join(z) if z else 'No real zeros')
    return o


def steps(P, d, Q, v):
    # P: {(x power, y power): number}, all over d; Q: its factors as
    # numbers by the power of x; v: the letters that are x and y
    b = {'x': v[0], 'y': v[-1]}
    o = []
    for l in fac2(P, d, Q):
        l = l.replace('Multiply', '#')
        t = ''
        for c in l:
            t += b.get(c, c)
        t = t.replace('#', 'Multiply')
        o.append('Fac: ' + t[4:] if t[:4] == 'Ans:' else t)
    return o
