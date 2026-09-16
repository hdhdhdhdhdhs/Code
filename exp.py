# EXP - exponent and radical helper for the Casio fx-9750GIII
# Powers stay as powers: 2^2 is printed as 2^2, never as 4.
W = 21


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


# ---- rationals, kept as (numerator, denominator) with denominator > 0 ----
def rn(n, d=1):
    if d == 0:
        raise ValueError('div by 0')
    if d < 0:
        n = -n
        d = -d
    g = gcd(n, d) or 1
    return (n // g, d // g)


def rml(a, b):
    return rn(a[0] * b[0], a[1] * b[1])


def rdv(a, b):
    return rn(a[0] * b[1], a[1] * b[0])


def rad(a, b):
    return rn(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def rpw(c, k):
    if k < 0:
        return rn(c[1] ** (-k), c[0] ** (-k))
    return rn(c[0] ** k, c[1] ** k)


def pnum(t):
    if '.' in t:
        i = t.index('.')
        w = t[:i] + t[i + 1:]
        if w == '' or '.' in w:
            raise ValueError('bad number')
        return rn(int(w), 10 ** (len(t) - i - 1))
    return (int(t), 1)


def irt(n, q):
    """Exact integer q-th root of n, or None."""
    if q > 20 and abs(n) > 1:
        return None
    if n < 0:
        if q % 2 == 0:
            return None
        r = irt(-n, q)
        return None if r is None else -r
    if n < 2:
        return n
    hi = 1
    while hi ** q < n:
        hi *= 2
    lo = 1
    while lo <= hi:
        m = (lo + hi) // 2
        p = m ** q
        if p == n:
            return m
        if p < n:
            lo = m + 1
        else:
            hi = m - 1
    return None


def rrt(c, q):
    a = irt(c[0], q)
    b = irt(c[1], q)
    if a is None or b is None:
        return None
    return (a, b)


def mix(n, q):
    """Split n into (outside ** q) * inside, outside as large as possible."""
    if q > 20 or n > 40000000:
        return 1, n
    o = 1
    d = 2
    while 1:
        p = d ** q
        if p > n:
            break
        while n % p == 0:
            n //= p
            o *= d
        d += 1
    return o, n


# ---- a monomial is [coefficient, numeric powers, variable powers] ----
def one():
    return [(1, 1), [], []]


def put(l, k, e):
    for p in l:
        if p[0] == k:
            p[1] = rad(p[1], e)
            return
    l.append([k, e])


def mmul(a, b):
    a[0] = rml(a[0], b[0])
    for p in b[1]:
        put(a[1], p[0], p[1])
    for p in b[2]:
        put(a[2], p[0], p[1])
    return a


def minv(m):
    o = one()
    o[0] = rdv((1, 1), m[0])
    for p in m[1]:
        o[1].append([p[0], rn(-p[1][0], p[1][1])])
    for p in m[2]:
        o[2].append([p[0], rn(-p[1][0], p[1][1])])
    return o


def mpow(m, e):
    o = one()
    for p in m[1]:
        o[1].append([p[0], rml(p[1], e)])
    for p in m[2]:
        o[2].append([p[0], rml(p[1], e)])
    c = m[0]
    if c[0] == 0:
        if e[0] <= 0:
            raise ValueError('0 to a bad power')
        return o if o[0] == (0, 1) else [(0, 1), o[1], o[2]]
    if e[1] == 1:
        # whole-number power: keep the numbers as powers, do not work them out
        k = e[0]
        if c[0] < 0 and k % 2:
            o[0] = (-1, 1)
        n = abs(c[0])
        if n != 1:
            put(o[1], n, (k, 1))
        if c[1] != 1:
            put(o[1], c[1], (-k, 1))
    else:
        r = rrt(c, e[1])
        if r is not None:
            o[0] = rpw(r, e[0])
        else:
            if c[0] < 0:
                if e[1] % 2 == 0:
                    raise ValueError('not a real answer')
                if e[0] % 2:
                    o[0] = (-1, 1)
            n = abs(c[0])
            if n != 1:
                put(o[1], n, e)
            if c[1] != 1:
                put(o[1], c[1], rn(-e[0], e[1]))
    return o


def norm(m):
    """Tidy a monomial: pull exact roots out, merge, make it printable."""
    co = m[0]
    src = []
    for p in m[1]:
        put(src, p[0], p[1])
    for _ in range(6):
        out = []
        ch = 0
        for p in src:
            b = p[0]
            e = p[1]
            if e[0] == 0:
                ch = 1
                continue
            if e[1] == 1:
                put(out, b, e)
                continue
            q = e[1]
            k = e[0] // q
            j = e[0] - k * q
            if k:
                if abs(k) * len(str(b)) > 30:
                    put(out, b, e)
                    continue
                co = rml(co, rpw((b, 1), k))
                ch = 1
            if j == 0:
                ch = 1
                continue
            if j > 1:
                if len(str(b)) * j > 24:
                    put(out, b, (j, q))
                    continue
                b = b ** j
                ch = 1
            r = irt(b, q)
            if r is not None:
                co = rml(co, (r, 1))
                ch = 1
                continue
            r, b2 = mix(b, q)
            if r > 1:
                co = rml(co, (r, 1))
                b = b2
                ch = 1
                if b == 1:
                    continue
            put(out, b, (1, q))
        mg = []
        for p in out:
            hit = 0
            if p[1][1] != 1:
                for r in mg:
                    if r[1] == p[1] and \
                       len(str(r[0])) + len(str(p[0])) <= 18:
                        r[0] = r[0] * p[0]
                        hit = 1
                        ch = 1
                        break
            if not hit:
                mg.append(p)
        src = mg
        if not ch:
            break
    keep = []
    for p in src:
        if p[1] == (1, 1):
            co = rml(co, (p[0], 1))
        elif p[1] == (-1, 1):
            co = rdv(co, (p[0], 1))
        elif p[1][0] != 0:
            keep.append(p)
    for p in keep:
        b = p[0]
        if p[1][1] != 1 or b < 2:
            continue
        while co[0] % b == 0 and abs(co[0]) >= b:
            co = rn(co[0] // b, co[1])
            p[1] = rad(p[1], (1, 1))
        while co[1] % b == 0 and co[1] >= b:
            co = rn(co[0], co[1] // b)
            p[1] = rad(p[1], (-1, 1))
    nb = []
    for p in keep:
        if p[1] == (1, 1):
            co = rml(co, (p[0], 1))
        elif p[1] == (-1, 1):
            co = rdv(co, (p[0], 1))
        elif p[1][0] != 0:
            nb.append(p)
    vr = []
    for p in m[2]:
        if p[1][0] != 0:
            vr.append([p[0], p[1]])
    return [co, nb, vr]


# ---- reading what the user typed ----
def tok(s):
    s = s.lower().replace('[', '(').replace(']', ')')
    o = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == ' ':
            i += 1
        elif c.isdigit() or c == '.':
            j = i
            while j < n and (s[j].isdigit() or s[j] == '.'):
                j += 1
            o.append(s[i:j])
            i = j
        elif c.isalpha():
            j = i
            while j < n and s[j].isalpha():
                j += 1
            w = s[i:j]
            if (w == 'sqrt' or w == 'rt') and j < n and s[j] == '(':
                o.append(w)
                i = j
            else:
                o.append(c)
                i += 1
        elif c in '()^*/+-,':
            o.append(c)
            i += 1
        else:
            raise ValueError('bad sign ' + c)
    return o


def idx(q):
    if q[1] != 1 or q[0] < 2 or q[0] > 20:
        raise ValueError('index 2 to 20')
    return q[0]


def isnum(t):
    return t[0].isdigit() or t[0] == '.'


def prat(ts, i, frac):
    s = 1
    while i < len(ts) and (ts[i] == '-' or ts[i] == '+'):
        if ts[i] == '-':
            s = -s
        i += 1
    if i >= len(ts) or not isnum(ts[i]):
        raise ValueError('need a number')
    v = pnum(ts[i])
    i += 1
    if frac and i + 1 < len(ts) and ts[i] == '/' and isnum(ts[i + 1]):
        v = rdv(v, pnum(ts[i + 1]))
        i += 2
    return rn(s * v[0], v[1]), i


def pexp(ts, i):
    if i < len(ts) and ts[i] == '(':
        v, i = prat(ts, i + 1, 1)
        if i >= len(ts) or ts[i] != ')':
            raise ValueError('need )')
        return v, i + 1
    return prat(ts, i, 0)


def patom(ts, i):
    if i >= len(ts):
        raise ValueError('ends too soon')
    t = ts[i]
    if t == '(':
        m, i = pmul(ts, i + 1)
        if i >= len(ts) or ts[i] != ')':
            raise ValueError('need )')
        return m, i + 1
    if t == 'sqrt' or t == 'rt':
        q = (2, 1)
        i += 2
        if t == 'rt':
            q, i = prat(ts, i, 0)
            if i >= len(ts) or ts[i] != ',':
                raise ValueError('need a , here')
            i += 1
        m, i = pmul(ts, i)
        if i >= len(ts) or ts[i] != ')':
            raise ValueError('need )')
        return mpow(m, rn(1, idx(q))), i + 1
    m = one()
    if isnum(t):
        m[0] = pnum(t)
        return m, i + 1
    if t.isalpha():
        m[2].append([t, (1, 1)])
        return m, i + 1
    raise ValueError('bad sign ' + t)


def ppow(ts, i):
    m, i = patom(ts, i)
    if i < len(ts) and ts[i] == '^':
        e, i = pexp(ts, i + 1)
        m = mpow(m, e)
    return m, i


def psign(ts, i):
    if i < len(ts) and ts[i] == '-':
        m, i = psign(ts, i + 1)
        m[0] = rn(-m[0][0], m[0][1])
        return m, i
    return ppow(ts, i)


def pmul(ts, i):
    m, i = psign(ts, i)
    while i < len(ts) and ts[i] != ')':
        t = ts[i]
        if t == '*':
            b, i = psign(ts, i + 1)
            m = mmul(m, b)
        elif t == '/':
            b, i = psign(ts, i + 1)
            m = mmul(m, minv(b))
        elif t == '+' or t == '-':
            raise ValueError('no + or - here')
        else:
            b, i = psign(ts, i)
            m = mmul(m, b)
    return m, i


def parse(s):
    ts = tok(s)
    if not ts:
        raise ValueError('nothing typed')
    m, i = pmul(ts, 0)
    if i != len(ts):
        raise ValueError('extra )')
    return m


# ---- writing the answer out ----
def rs(e):
    if e[1] == 1:
        return str(e[0])
    return '(' + str(e[0]) + '/' + str(e[1]) + ')'


def npw(b, e):
    """A number to a power: a fractional one is shown as a radical."""
    if e[1] == 1:
        return pw(str(b), e)
    if e[0] == 1:
        return rdc(e[1], str(b))
    return str(b) + '^' + rs(e)


def pw(b, e):
    if e == (1, 1):
        return b
    return b + '^' + rs(e)


def cat(l):
    o = ''
    for x in l:
        if o and x[0].isdigit():
            o += '*'
        o += x
    return o


def fmt(m):
    m = norm(m)
    co = m[0]
    if co[0] == 0:
        return '0'
    sg = '-' if co[0] < 0 else ''
    nn = []
    dd = []
    if abs(co[0]) != 1:
        nn.append(str(abs(co[0])))
    if co[1] != 1:
        dd.append(str(co[1]))
    for p in m[1]:
        e = p[1]
        if e[0] < 0:
            dd.append(npw(p[0], rn(-e[0], e[1])))
        else:
            nn.append(npw(p[0], e))
    vn = []
    vd = []
    for p in m[2]:
        e = p[1]
        if e[0] < 0:
            vd.append(pw(p[0], rn(-e[0], e[1])))
        else:
            vn.append(pw(p[0], e))
    top = cat(nn + vn)
    bot = cat(dd + vd)
    if top == '':
        top = '1'
    if bot == '':
        return sg + top
    if len(dd) + len(vd) > 1:
        bot = '(' + bot + ')'
    return sg + top + '/' + bot


def flat(m):
    """Same value, but with the whole-number powers worked out."""
    m = norm(m)
    co = m[0]
    nb = []
    for p in m[1]:
        k = p[1][0]
        if p[1][1] == 1 and abs(k) * len(str(p[0])) <= 30:
            co = rml(co, rpw((p[0], 1), k))
        else:
            nb.append(p)
    return [co, nb, m[2]]


def nofrac(m):
    for p in m[1] + m[2]:
        if p[1][1] != 1:
            return 0
    return 1


def rdc(q, inside):
    if q == 2:
        return 'sqrt(' + inside + ')'
    return 'rt(' + str(q) + ',' + inside + ')'


def brk(s):
    if len(s) == 1 or s.isdigit():
        return s
    return '(' + s + ')'


def cut(s):
    """Position of the main / - the one that is the fraction bar."""
    d = 0
    for i in range(len(s)):
        c = s[i]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif c == '/' and d == 0:
            return i
    return -1


def peel(s):
    """Drop brackets that wrap the whole thing."""
    while len(s) > 1 and s[0] == '(' and s[-1] == ')':
        d = 0
        for i in range(len(s)):
            if s[i] == '(':
                d += 1
            elif s[i] == ')':
                d -= 1
                if d == 0 and i != len(s) - 1:
                    return s
        s = s[1:-1]
    return s


def stack(s):
    """Write it as a real fraction, over three lines, if it fits."""
    i = cut(s)
    if i < 0:
        return wrap(s)
    t = s[:i]
    b = peel(s[i + 1:])
    g = ''
    if t[0] == '-':
        g = '- '
        t = t[1:]
    t = peel(t)
    w = max(len(t), len(b))
    if w + len(g) > W:
        return wrap(s)
    pd = ' ' * len(g)
    return [pd + ' ' * ((w - len(t)) // 2) + t,
            g + '-' * w,
            pd + ' ' * ((w - len(b)) // 2) + b]


def wrap(t):
    o = []
    cur = ''
    for x in t.split(' '):
        if cur == '':
            cur = x
        elif len(cur) + 1 + len(x) <= W:
            cur += ' ' + x
        else:
            o.append(cur)
            cur = x
    if cur:
        o.append(cur)
    r = []
    for ln in o:
        while len(ln) > W:
            r.append(ln[:W])
            ln = ln[W:]
        r.append(ln)
    return r


# ---- the five jobs ----
def do1(a):
    m = parse(a[0])
    o = [fmt(m)]
    s = fmt(flat(m))
    if s != o[0]:
        o.append('= ' + s)
    return o


def do2(a):
    m = parse(a[0])
    e = parse_exp(a[1])
    b = fmt(m)
    if e[1] == 1:
        return [pw(brk(b), e)]
    r = rdc(e[1], b)
    k = abs(e[0])
    if k != 1:
        r = '(' + r + ')^' + str(k)
    if e[0] < 0:
        r = '1/' + r
    o = [r]
    t = mpow(m, e)
    if nofrac(norm(t)):
        o.append('simp: ' + fmt(t))
    return o


def do3(a):
    q = idx(parse_exp(a[0]))
    m = parse(a[1])
    e = parse_exp(a[2]) if a[2] else (1, 1)
    if e[1] != 1:
        raise ValueError('power must be whole')
    p = e[0]
    b = fmt(m)
    e = rn(p, q)
    o = [pw(brk(b), e)]
    t = mpow(m, e)
    if nofrac(norm(t)):
        o.append('simp: ' + fmt(t))
    return o


def do4(a):
    c = parse_exp(a[0])
    q = idx(parse_exp(a[1]))
    m = parse(a[2])
    m[0] = rml(m[0], rpw((abs(c[0]), c[1]), q))
    sg = ''
    if c[0] < 0:
        if q % 2:
            m[0] = rn(-m[0][0], m[0][1])
        else:
            sg = '-'
    return [sg + rdc(q, fmt(m))]


def do5(a):
    q = idx(parse_exp(a[0]))
    m = flat(parse(a[1]))
    if m[1]:
        raise ValueError('cannot do that root')
    c = m[0]
    sg = ''
    n = c[0]
    if n < 0:
        if q % 2 == 0:
            raise ValueError('not a real answer')
        sg = '-'
        n = -n
    d = c[1]
    if d != 1:
        if len(str(d)) * (q - 1) > 30:
            raise ValueError('numbers too big')
        n = n * d ** (q - 1)
    on, ins = mix(n, q)
    co = rn(on, d)
    iv = []
    ov = []
    for p in m[2]:
        e = p[1]
        if e[1] != 1 or e[0] < 0:
            raise ValueError('need whole powers')
        if e[0] // q:
            ov.append([p[0], (e[0] // q, 1)])
        if e[0] % q:
            iv.append([p[0], (e[0] % q, 1)])
    si = fmt([(ins, 1), [], iv])
    top = fmt([(co[0], 1), [], ov])
    if si == '1':
        return [sg + fmt([co, [], ov])]
    if top == '1':
        top = ''
    r = sg + top + rdc(q, si)
    if co[1] != 1:
        r = r + '/' + str(co[1])
    return [r]


def parse_exp(s):
    ts = tok(s)
    v, i = prat(ts, 0, 1)
    if i != len(ts):
        raise ValueError('bad number')
    return v


JOB = (do1, do2, do3, do4, do5)
ASK = (('Expr:',), ('Base:', 'Exp:'), ('Index:', 'Inside:', 'Power:'),
       ('Coeff:', 'Index:', 'Inside:'), ('Index:', 'Inside:'))
MENU = ('Simplify,Power->radical,Radical->power,Mixed->entire,'
        'Entire->mixed').split(',')

while True:
    for i in range(5):
        print(str(i + 1) + ' ' + MENU[i])
    try:
        k = input('Pick 1-5:').strip()
    except (KeyboardInterrupt, EOFError):
        break
    if k not in ('1', '2', '3', '4', '5'):
        if k != '':
            print('1 to 5 only')
        continue
    n = int(k)
    a = []
    try:
        for q in ASK[n - 1]:
            a.append(input(q).strip())
    except (KeyboardInterrupt, EOFError):
        break
    if a[0] == '':
        continue
    try:
        out = JOB[n - 1](a)
    except Exception as e:
        out = wrap('Err: ' + (str(e) or 'bad input'))
    for i in range(len(out)):
        for x in (stack(out[i]) if i == 0 else wrap(out[i])):
            print(x)
    try:
        input('EXE=menu')
    except (KeyboardInterrupt, EOFError):
        break
