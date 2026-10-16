# FAC - factor polynomials for the Casio fx-9750GIII
#
# Type it the way it is written:  2x^2+5x-3
# Brackets and * are fine:        3(x^2-4)   x(x+1)^2
# Or only the numbers, highest power first:  2,5,-3
# Two letters work when every term has the same total power:
#   x^2+5xy+6y^2   4x^2-9y^2   and a shared y comes out first: x^2y-4y
#
# For ax^2+bx+c it works the slide-and-divide way and shows both sets:
#   Slide: the factors of x^2+bx+ac  (a working step, not the answer)
#   Ans:   the real factors, after dividing by a
# Bigger polynomials: takes out the GCF, finds the zeros that make it 0,
# divides each one out, and finishes on the quadratic that is left.
# Pieces with no nice zeros are found from the zeros worked out as
# decimals, and every piece is checked by exact division before it is
# printed, so a rounding slip can never put a wrong factor on screen.
import math
W = 21
DIG = '0123456789.'


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


# ---- polynomials while reading: ({(x power, y power): number}, divisor)
def tidy(c, d):
    for k in list(c):
        if c[k] == 0:
            del c[k]
        elif k[0] + k[1] > 12:
            raise ValueError('power over 12')
    g = d
    for v in c.values():
        g = gcd(g, v)
    if d < 0:
        g = -g
    for k in c:
        c[k] //= g
    return (c, d // g)


def mul(a, b):
    c = {}
    for i, u in a[0].items():
        for j, v in b[0].items():
            k = (i[0] + j[0], i[1] + j[1])
            c[k] = c.get(k, 0) + u * v
    return tidy(c, a[1] * b[1])


def add(a, b, s):
    c = {}
    for k, v in a[0].items():
        c[k] = v * b[1]
    for k, v in b[0].items():
        c[k] = c.get(k, 0) + s * v * a[1]
    return tidy(c, a[1] * b[1])


def num(t):
    i = t.find('.')
    if t == '.' or (i >= 0 and t.find('.', i + 1) >= 0):
        raise ValueError('bad number')
    if i < 0:
        return ({(0, 0): int(t)}, 1)
    f = t[i + 1:]
    return tidy({(0, 0): int(t[:i] + f)}, 10 ** len(f))


def tok(s):
    s = s.replace('**', '^').replace('[', '(').replace(']', ')')
    o = []
    i = 0
    while i < len(s):
        j = i + 1
        if s[i] in DIG:
            while j < len(s) and s[j] in DIG:
                j += 1
        elif s[i] not in 'xy+-*/^()':
            raise ValueError('bad sign ' + s[i])
        o.append(s[i:j])
        i = j
    return o


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
            for k in w[0]:
                if k != (0, 0):
                    raise ValueError('no dividing by x')
            if not w[0].get((0, 0)):
                raise ValueError('divide by 0')
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
        if i >= len(ts) or ts[i] != ')':
            raise ValueError('missing )')
        i += 1
    elif t == 'x' or t == 'y':
        v = ({(int(t == 'x'), int(t == 'y')): 1}, 1)
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return mul(v, ({(0, 0): -1}, 1)), i
    else:
        raise ValueError('bad ' + t)
    # x2 means x^2: the power can follow x with no ^ in between
    if i < len(ts) and (ts[i] == '^' or (t in 'xy' and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        b = i < len(ts) and ts[i] == '('
        if b:
            i += 1
        if i >= len(ts) or not ts[i].isdigit():
            raise ValueError('power not whole')
        e = int(ts[i])
        i += 1
        if b:
            if i >= len(ts) or ts[i] != ')':
                raise ValueError('missing )')
            i += 1
        if e > 12:
            raise ValueError('power over 12')
        r = ({(0, 0): 1}, 1)
        for _ in range(e):
            r = mul(r, v)
        v = r
    return v, i


def expr(s):
    ts = tok(s)
    if not ts:
        raise ValueError('nothing typed')
    v, i = pexpr(ts, 0)
    if i != len(ts):
        raise ValueError('bad ' + ts[i])
    return v


def parse(s):
    s = s.lower().replace(' ', '').replace('math.', '')
    if s[-2:] == '=0':
        s = s[:-2]
    if 'x' in s or ',' not in s:
        return expr(s)
    v = ({}, 1)
    for t in s.split(','):
        v = add(mul(v, ({(1, 0): 1}, 1)), expr(t), 1)
    return v


# ---- whole-number polynomials, coefficients low to high
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


def split(c):
    # a quadratic factor through the values at -1, 0 and 1
    v0 = dvs(ev(c, 0))
    v1 = dvs(ev(c, 1))
    vm = dvs(ev(c, -1))
    if len(v0) * len(v1) * len(vm) > 4000:
        return None
    for a in v0 + [-x for x in v0]:
        for b in v1 + [-x for x in v1]:
            for d in vm + [-x for x in vm]:
                t = b + d - 2 * a
                if t > 0 and t % 2 == 0 and (b - d) % 2 == 0:
                    g = [a, (b - d) // 2, t // 2]
                    q = pdiv(c, g)
                    if q is not None:
                        return g
    return None


def prim(c):
    g = 0
    for x in c:
        g = gcd(g, x)
    if c[-1] < 0:
        g = -g
    return [x // g for x in c]


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


def units(c):
    # every zero found numerically, real ones alone and the rest in
    # conjugate pairs, each as a small real polynomial
    n = len(c) - 1
    # scale x = S*t so every zero has |t| <= 2: keeps the numbers small
    # enough for a calculator that works in single precision
    S = 0.0
    for k in range(n):
        S = max(S, (abs(c[k]) / abs(c[-1])) ** (1.0 / (n - k)))
    S = S or 1.0
    a = [c[k] / c[-1] / S ** (n - k) for k in range(n + 1)]
    z = []
    for k in range(n):
        t = 6.2832 * k / n + 0.4
        z.append([math.cos(t), math.sin(t)])
    w = 0
    for it in range(500):
        mv = 0
        for i in range(n):
            zr, zi = z[i]
            pr, pi = 1.0, 0.0
            for k in range(n - 1, -1, -1):
                pr, pi = pr * zr - pi * zi + a[k], pr * zi + pi * zr
            dr, di = 1.0, 0.0
            for j in range(n):
                if j != i:
                    er = zr - z[j][0]
                    ei = zi - z[j][1]
                    dr, di = dr * er - di * ei, dr * ei + di * er
            m = dr * dr + di * di or 1e-30
            qr = (pr * dr + pi * di) / m
            qi = (pi * dr - pr * di) / m
            z[i] = [zr - qr, zi - qi]
            mv = max(mv, abs(qr) + abs(qi))
        # it closes in fast once near: a few more passes reach full precision
        if mv < 1e-5:
            w += 1
        if mv < 1e-14 or w > 4:
            break
    for p in z:
        if not abs(p[0]) + abs(p[1]) < 10:
            return []
        p[0] *= S
        p[1] *= S
    u = []
    ok = [1] * n
    for i in range(n):
        if not ok[i]:
            continue
        ok[i] = 0
        zr, zi = z[i]
        if abs(zi) < 1e-6 * (1 + abs(zr)):
            u.append((1, [-zr, 1.0]))
            continue
        b = i
        bd = 1e300
        for j in range(n):
            d = abs(z[j][0] - zr) + abs(z[j][1] + zi)
            if ok[j] and d < bd:
                b = j
                bd = d
        ok[b] = 0
        zr = (zr + z[b][0]) / 2
        zi = (abs(zi) + abs(z[b][1])) / 2
        u.append((2, [zr * zr + zi * zi, -2 * zr, 1.0]))
    return u


def nsplit(c):
    # the smallest factor: try groups of zeros, then check exactly
    u = units(c)
    k = len(u)
    L = dvs(c[-1])
    for d in range(2, (len(c) - 1) // 2 + 1):
        for m in range(1, 1 << k):
            s = 0
            for i in range(k):
                if m >> i & 1:
                    s += u[i][0]
            if s != d:
                continue
            p = [1.0]
            for i in range(k):
                if m >> i & 1:
                    q = u[i][1]
                    r = [0.0] * (len(p) + len(q) - 1)
                    for x in range(len(p)):
                        for y in range(len(q)):
                            r[x + y] += p[x] * q[y]
                    p = r
            for l in L:
                # cheap test first: the constant must be a whole number
                # that divides c's constant
                t = l * p[0]
                g = int(round(t))
                if g and abs(t - g) < 0.01 and c[0] % g == 0:
                    g = [int(round(l * x)) for x in p]
                    if pdiv(c, g) is not None:
                        return g
    return None


# ---- writing it out
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


def isq(n):
    r = int(n ** 0.5)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r


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


def fac(s):
    P, d = parse(s)
    w = 0
    for k in P:
        if k[0]:
            w = -1
        elif k[1] and not w:
            w = 1
    if w > 0:
        # only y: factor it as x, then write y back in
        P = dict(((k[1], 0), P[k]) for k in P)
        return [l.replace('x', 'y') for l in fac2(P, d)]
    return fac2(P, d)


def fac2(P, d):
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
    sp = 0
    while len(c) > 4:
        f = sqf(c)
        if len(f) == len(c):
            f = nsplit(c) or split(c)
        elif len(f) > 4:
            f = nsplit(f) or f
        if f is None:
            break
        o.append('Splits:(' + pstr(f, Y) + ')(' + pstr(pdiv(c, f), Y) + ')')
        while len(c) > len(f) and pdiv(c, f) is not None:
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
            for e in units(sqf(f)):
                if e[0] == 1:
                    t = '%.4f' % -e[1][0]
                    z.append('~' + (t.rstrip('0').rstrip('.') or '0'))
    o.append('Zeros: ' + ', '.join(z) if z else 'No real zeros')
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


print('Factor. Type like')
print('2x^2+5x-3 or 2,5,-3')
s = ''
while True:
    if s == '':
        try:
            s = input('Poly:').strip()
        except (KeyboardInterrupt, EOFError):
            break
        if s == '':
            continue
    try:
        out = fac(s)
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    s = ''
    ls = []
    for ln in out:
        ls += wrap(ln)
    try:
        for i in range(len(ls)):
            # typing a new one at more.. skips the rest and factors it
            if i and i % 6 == 0:
                s = input('more..').strip()
                if s:
                    break
            print(ls[i])
    except (KeyboardInterrupt, EOFError):
        break
