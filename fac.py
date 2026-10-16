# FAC - factor polynomials for the Casio fx-9750GIII
#
# Type it the way it is written:  2x^2+5x-3
# Brackets and * are fine:        3(x^2-4)   x(x+1)^2
# Or only the numbers, highest power first:  2,5,-3
#
# For ax^2+bx+c it works the slide-and-divide way and shows both sets:
#   Slide: the factors of x^2+bx+ac  (a working step, not the answer)
#   Ans:   the real factors, after dividing by a
# Bigger polynomials: takes out the GCF, finds the zeros that make it 0,
# divides each one out, and finishes on the quadratic that is left.
W = 21
DIG = '0123456789.'


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


# ---- polynomials while reading: (coefficients low to high, denominator)
def tidy(c, d):
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    if len(c) > 13:
        raise ValueError('power over 12')
    g = d
    for x in c:
        g = gcd(g, x)
    if d < 0:
        g = -g
    return ([x // g for x in c], d // g)


def mul(a, b):
    c = [0] * (len(a[0]) + len(b[0]) - 1)
    for i in range(len(a[0])):
        for j in range(len(b[0])):
            c[i + j] += a[0][i] * b[0][j]
    return tidy(c, a[1] * b[1])


def add(a, b, s):
    c = [0] * max(len(a[0]), len(b[0]))
    for i in range(len(a[0])):
        c[i] += a[0][i] * b[1]
    for i in range(len(b[0])):
        c[i] += s * b[0][i] * a[1]
    return tidy(c, a[1] * b[1])


def num(t):
    i = t.find('.')
    if t.count('.') > 1 or t == '.':
        raise ValueError('bad number')
    if i < 0:
        return ([int(t)], 1)
    f = t[i + 1:]
    return tidy([int(t[:i] + f)], 10 ** len(f))


def tok(s):
    s = s.replace('**', '^').replace('[', '(').replace(']', ')')
    o = []
    i = 0
    while i < len(s):
        j = i + 1
        if s[i] in DIG:
            while j < len(s) and s[j] in DIG:
                j += 1
        elif s[i] not in 'x+-*/^()':
            raise ValueError('bad sign ' + s[i])
        o.append(s[i:j])
        i = j
    return o


def pexpr(ts, i):
    v = ([0], 1)
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
            if len(w[0]) > 1:
                raise ValueError('no dividing by x')
            if w[0][0] == 0:
                raise ValueError('divide by 0')
            w = tidy([w[1]], w[0][0])
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
    elif t == 'x':
        v = ([0, 1], 1)
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return mul(v, ([-1], 1)), i
    else:
        raise ValueError('bad ' + t)
    # x2 means x^2: the power can follow x with no ^ in between
    if i < len(ts) and (ts[i] == '^' or (t == 'x' and ts[i][0] in DIG)):
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
        r = ([1], 1)
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
    v = ([0], 1)
    for t in s.split(','):
        v = add(mul(v, ([0, 1], 1)), expr(t), 1)
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
    s = 0
    for a in reversed(c):
        s = s * x + a
    return s


def root(c):
    r = []
    for q in dvs(c[-1]):
        for p in dvs(c[0]):
            if gcd(p, q) == 1:
                r.append((p, q))
                r.append((-p, q))
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


# ---- writing it out
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


def fr(n, d):
    g = gcd(n, d)
    if d < 0:
        g = -g
    n //= g
    d //= g
    return str(n) if d == 1 else str(n) + '/' + str(d)


def lin(p, a):
    s = '(x' + ('+' if p > 0 else '-') + str(abs(p))
    return s + ('/' + str(a) if a != 1 else '') + ')'


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


def slide(c, o, F):
    C, B, A = c
    N = A * C
    o.append('Multiply:' + ('ac=' if A != 1 else '') + str(N) +
             ' Add:' + str(B))
    p = None
    for t in dvs(N):
        for u in (t, -t):
            if p is None and u + N // u == B:
                p = u
    if p is None:
        o.append('No pair works')
        F.append(c)
        return
    q = max(p, N // p)
    p = min(p, N // p)
    o.append(str(p) + ' and ' + str(q))
    if A != 1:
        o.append('Slide:' + lin(p, 1) + lin(q, 1))
        o.append('/' + str(A) + ':' + lin(p, A) + lin(q, A))
    for t in (p, q):
        g = gcd(t, A)
        F.append([t // g, A // g])


def fac(s):
    c, d = parse(s)
    if len(c) < 2:
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
    o = []
    if h == '-':
        o.append('Take out -1')
    elif h:
        o.append('GCF: ' + h.replace('(', '').replace(')', ''))
    if h and len(c) > 1:
        o.append(h + '(' + pstr(c) + ')')
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
        o.append('x=' + fr(-f[0], f[1]) + ' gives 0')
        o.append('/(' + pstr(f) + ')' + ('^' + str(k) if k > 1 else '') +
                 '=' + pstr(c))
    sp = 0
    while len(c) > 4:
        f = split(c)
        if f is None:
            break
        c = pdiv(c, f)
        F.append(f)
        sp = 1
        o.append('Splits:(' + pstr(f) + ')(' + pstr(c) + ')')
    if len(c) == 3 and not sp:
        slide(c, o, F)
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
        t = pstr(f)
        if h or len(u) > 1 or k > 1:
            t = '(' + t + ')'
        a += t + ('^' + str(k) if k > 1 else '')
    if len(u) == 1 and u[0][1] == 1 and not h and len(u[0][0]) > 2:
        o.append('Prime: no factors')
    else:
        o.append('Ans:' + a)
    z = ['0'] if m else []
    for f, k in u:
        if len(f) == 2:
            z.append(fr(-f[0], f[1]))
        elif len(f) == 3:
            surd(f, z)
    if z:
        o.append('Zeros: ' + ', '.join(z))
    if len(c) > 3:
        o.append(('Others' if z else 'Zeros') + ': not exact')
    elif not z:
        o.append('No real zeros')
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
