# FRAC - simplify rational expressions for the Casio fx-9750GIII
#
# It asks for one fraction at a time, so no brackets are needed:
#   Top: x              Bottom: x^2-3x-4     + - * / or EXE: -
#   Top: 4              Bottom: x+1          + - * / or EXE: (EXE)
# EXE alone for a bottom means 1. A whole expression typed as a top,
# like -3a^-3b^-7c^-6/(12a^-6b^-3c^-3), with EXE for the bottom, works.
# ^ or ** for powers (x2 means x^2), any letters, powers below 0.
#
# It factors every top and bottom, cancels what they share, and shows
#   Ans: the answer, top multiplied out, bottom factored
#   NPV: the non-permissible values, every value that makes any bottom
#        0 on the way (a bottom that cancels still counts, and so does
#        the top of anything you divide by): x!=-3,-1,2 means x is not
#        -3, -1 or 2. Letters that can only not be 0: a,b!=0
W = 21
DIG = '0123456789.'
LET = 'abcdefghijklmnopqrstuvwxyz'
L = []  # letters in the order typed: letter i is 16 bits at 2^(16i)
N = []  # every bottom met on the way (as factors), for the NPVs


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


# ---- polynomials: {letter powers packed: whole number}
def dg(k):
    e = []
    while k:
        e.append(k & 65535)
        k >>= 16
    return e


def pm(a, b):
    c = {}
    for i in a:
        for j in b:
            c[i + j] = c.get(i + j, 0) + a[i] * b[j]
    for k in list(c):
        if not c[k]:
            del c[k]
    return c


def lead(P):
    # the number on the term written first
    return P[min(P, key=kk)]


def vs(P):
    # the letters in P
    o = []
    for k in P:
        e = dg(k)
        for i in range(len(e)):
            if e[i] and i not in o:
                o.append(i)
    o.sort()
    return o


def ky(P):
    return tuple(sorted(P.items()))


def ex(F, s):
    # multiply out the factors whose power has sign s (1: top, -1: bottom)
    P = {0: 1}
    for k in F:
        e = F[k] * s
        if e > 0:
            f = dict(k)
            if len(f) > 1 and e * max([max(dg(j) or [0]) for j in f]) > 120:
                raise ValueError('too big')
            for _ in range(e):
                P = pm(P, f)
    return P


# ---- values: (p, q, F) is p/q times the factors in F, {key: power};
# a power below 0 is in the bottom
def val(p, q, F):
    if not p:
        return (0, 1, {})
    g = gcd(p, q)
    if q < 0:
        g = -g
    G = {}
    for k in F:
        if F[k]:
            G[k] = F[k]
    return (p // g, q // g, G)


def mul(a, b, s=1):
    # a*b, or a/b with s=-1: then b's top factors are bottoms (kept in N)
    if s < 0:
        if not b[0]:
            raise ValueError('divide by 0')
        for k in b[2]:
            if b[2][k] > 0 and k not in N:
                N.append(k)
        b = (b[1], b[0], b[2])
    F = dict(a[2])
    for k in b[2]:
        F[k] = F.get(k, 0) + s * b[2][k]
    return val(a[0] * b[0], a[1] * b[1], F)


def pw(a, n):
    if n < 0:
        return mul((1, 1, {}), pw(a, -n), -1)
    F = {}
    for k in a[2]:
        F[k] = a[2][k] * n
    return val(a[0] ** n, a[1] ** n, F)


def add(T):
    # a sum of (sign, value): over the smallest common bottom, with the
    # factors every term has kept out, then the top factored again
    T = [t for t in T if t[1][0]]
    if len(T) < 2:
        return (T[0][0] * T[0][1][0], T[0][1][1], T[0][1][2]) if T else (0, 1, {})
    D = {}
    G = None
    q = 1
    for s, v in T:
        q = q * v[1] // gcd(q, v[1])
        for k in v[2]:
            if v[2][k] < 0:
                D[k] = min(D.get(k, 0), v[2][k])
        H = {}
        for k in v[2]:
            if v[2][k] > 0 and (G is None or k in G):
                H[k] = v[2][k] if G is None else min(G[k], v[2][k])
        G = H
    P = {}
    for s, v in T:
        F = dict(v[2])
        for k in D:
            F[k] = F.get(k, 0) - D[k]
        for k in G:
            F[k] -= G[k]
        c = s * v[0] * (q // v[1])
        X = ex(F, 1)
        for k in X:
            P[k] = P.get(k, 0) + c * X[k]
            if not P[k]:
                del P[k]
    if not P:
        return (0, 1, {})
    c, F = fct(P)
    for H in (G, D):
        for k in H:
            F[k] = F.get(k, 0) + H[k]
    return val(c, q, F)


# ---- factoring
def fct(P):
    # P = c times the factors in F; each factor has its biggest term
    # (letters in typed order) > 0
    c = 0
    for k in P:
        c = gcd(c, P[k])
    if lead(P) < 0:
        c = -c
    F = {}
    e = None
    for k in P:
        d = dg(k)
        e = d if e is None else [min(e[i], d[i] if i < len(d) else 0) for i in range(len(e))]
    m = 0
    for i in range(len(e)):
        if e[i]:
            F[((1 << 16 * i, 1),)] = e[i]
            m += e[i] << 16 * i
    Q = {}
    for k in P:
        Q[k - m] = P[k] // c
    for f in spl(Q):
        if lead(f) < 0:
            c = -c
            for k in f:
                f[k] = -f[k]
        k = ky(f)
        F[k] = F.get(k, 0) + 1
    return c, F


def spl(P):
    # P (shares no number or letter) as a list of factors
    if len(P) < 2:
        return []
    v = vs(P)
    t = [sum(dg(k)) for k in P]
    if len(v) == 1 or len(v) == 2 and min(t) == max(t):
        # one letter, or two with every term the same total power:
        # factored as one letter (the other as 1), then put back
        i = v[0]
        j = v[-1]
        n = 0
        for k in P:
            n = max(n, dg(k)[i] if i < len(dg(k)) else 0)
        if n > 30:
            return [P]
        c = [0] * (n + 1)
        for k in P:
            d = dg(k)
            c[d[i] if i < len(d) else 0] = P[k]
        o = []
        for f in uf(c):
            n = len(f) - 1
            g = {}
            for a in range(n + 1):
                if f[a]:
                    g[(a << 16 * i) + ((n - a) << 16 * j if j != i else 0)] = f[a]
            o.append(g)
        return o
    # more letters: as a polynomial in one letter, take out what all
    # its numbers (polynomials in the other letters) share: grouping
    for i in v:
        C = {}
        for k in P:
            d = (k >> 16 * i) & 65535
            if d not in C:
                C[d] = {}
            C[d][k - (d << 16 * i)] = P[k]
        if len(C) < 2:
            continue
        G = None
        for d in C:
            C[d] = fct(C[d])
            F = C[d][1]
            H = {}
            for k in F:
                if G is None or k in G:
                    H[k] = F[k] if G is None else min(G[k], F[k])
            G = H
            if not G:
                break
        if G:
            Q = {}
            for d in C:
                g, F = C[d]
                for k in G:
                    F[k] -= G[k]
                X = ex(F, 1)
                for k in X:
                    Q[k + (d << 16 * i)] = g * X[k]
            o = []
            for k in G:
                o += [dict(k)] * G[k]
            return o + spl(Q)
    return [P]


def uf(c):
    # c (low power first, c[0] != 0) into factors: repeated factors,
    # zeros p/q, then pieces x^2+bx+c; each one checked by exact
    # division (fix() below still cancels anything this misses)
    o = []
    st = [c]
    while st:
        c = st.pop()
        if len(c) < 3:
            o.append(c)
            continue
        s = sqf(c)
        f = None
        if len(s) < len(c):
            f = s
        elif abs(c[0]) < 10 ** 8 and abs(c[-1]) < 10 ** 8:
            f = root(c)
            if not f and len(c) > 4:
                f = split(c)
        if f:
            st += [f, pdiv(c, f)]
        else:
            o.append(c)
    return o


# ---- one-letter polynomials, low power first (as in fac.py)
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
    for i in range(len(c) - 1, -1, -1):
        s = s * x + c[i]
    return s


def root(c):
    # a zero p/q needs q-p to divide c(1) and q+p to divide c(-1)
    a = ev(c, 1)
    b = ev(c, -1)
    for q in dvs(c[-1]):
        for p in dvs(c[0]):
            for p in (p, -p):
                if ((q == p or a % (q - p) == 0) and (q == -p or b % (q + p) == 0)
                        and gcd(p, q) == 1 and pdiv(c, [-p, q]) is not None):
                    return [-p, q]
    return None


def split(c):
    # a quadratic factor through the values at -1, 0 and 1 (small ones)
    if max(abs(ev(c, 1)), abs(ev(c, -1)), abs(c[0])) > 10 ** 8:
        return None
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
                    if pdiv(c, g) is not None:
                        return g
    return None


def prim(c):
    g = 0
    for x in c:
        g = gcd(g, x)
    if c[-1] < 0:
        g = -g
    return [x // g for x in c]


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


def fix(v):
    # a one-letter top factor and bottom factor that share a piece the
    # factoring missed (too big for it): split both, so it cancels
    p, q, F = v
    for a in list(F):
        for b in list(F):
            if a in F and b in F and F[a] > 0 > F[b] and len(a) > 1 < len(b) and vs(dict(a)) == vs(dict(b)) == vs(dict(a))[:1]:
                i = vs(dict(a))[0]
                c = [uc(a, i), uc(b, i)]
                h = pg(c[0], c[1])
                if len(h) > 1:
                    for k in (a, b):
                        e = F.pop(k)
                        for t in (h, pdiv(uc(k, i), h)):
                            g, G = fct(dict([(j << 16 * i, t[j]) for j in range(len(t)) if t[j]]))
                            if e > 0:
                                p *= g ** e
                            else:
                                q *= g ** -e
                            for j in G:
                                F[j] = F.get(j, 0) + G[j] * e
    return val(p, q, F)


def uc(k, i):
    # factor k (one letter, letter i) as numbers, low power first
    c = [0] * (max([j >> 16 * i for j, _ in k]) + 1)
    for j, x in k:
        c[j >> 16 * i] = x
    return c


def num(t):
    i = t.find('.')
    if t == '.' or (i >= 0 and t.find('.', i + 1) >= 0):
        raise ValueError('bad number')
    if i < 0:
        return (int(t), 1, {})
    f = t[i + 1:]
    return val(int(t[:i] + f), 10 ** len(f), {})


def tok(s):
    o = []
    i = 0
    while i < len(s):
        j = i + 1
        if s[i] in DIG:
            while j < len(s) and s[j] in DIG:
                j += 1
        elif s[i:i + 4] == 'sqrt':
            raise ValueError('roots: use rad.py')
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
    T = []
    while True:
        s = 1
        while i < len(ts) and ts[i] in '+-':
            if ts[i] == '-':
                s = -s
            i += 1
        t, i = pterm(ts, i)
        T.append((s, t))
        if i >= len(ts) or ts[i] not in '+-':
            return add(T), i


def pterm(ts, i):
    v, i = pfac(ts, i)
    while i < len(ts) and ts[i] not in '+-)':
        t = ts[i]
        if t == '*' or t == '/':
            i += 1
        w, i = pfac(ts, i)
        v = mul(v, w, -1 if t == '/' else 1)
    return v, i


def pfac(ts, i):
    if i >= len(ts):
        raise ValueError('ends too soon')
    t = ts[i]
    i += 1
    if t == '(':
        v, i = pexpr(ts, i)
        i = need(ts, i, ')')
    elif t in LET:
        if t not in L:
            L.append(t)
        v = (1, 1, {((1 << 16 * L.index(t), 1),): 1})
    elif t[0] in DIG:
        v = num(t)
    elif t == '-':
        v, i = pfac(ts, i)
        return (-v[0], v[1], v[2]), i
    else:
        raise ValueError('bad ' + t)
    # power: a whole number, below 0 too. x2 means x^2
    if i < len(ts) and (ts[i] == '^' or (t in LET and ts[i][0] in DIG)):
        if ts[i] == '^':
            i += 1
        e, i = pfac(ts, i)
        if e[2] or e[1] != 1 or abs(e[0]) > 99:
            raise ValueError('bad power')
        v = pw(v, e[0])
    return v, i


# ---- writing it out
def ab():
    return sorted(range(len(L)), key=lambda i: L[i])


def kk(k):
    # term order: biggest total power first, then a before b
    e = dg(k)
    return [-sum(e)] + [-(e[i] if i < len(e) else 0) for i in ab()]


def mo(k):
    s = ''
    e = dg(k)
    for i in ab():
        if i < len(e) and e[i]:
            s += L[i] + ('^' + str(e[i]) if e[i] > 1 else '')
    return s


def es(P):
    if not P:
        return '0'
    s = ''
    for k in sorted(P, key=kk):
        c = P[k]
        m = mo(k)
        s += ('-' if c < 0 else '+') + (str(abs(c)) if abs(c) != 1 or not m else '') + m
    return s[1:] if s[0] == '+' else s


def fac(v):
    # the top multiplied out, over the bottom factored: number,
    # letters, then (factors)
    p, q, F = v
    c = q
    m = 0
    t = ''
    n = c != 1
    for k in sorted(F, key=lambda k: (len(k) > 1, es(dict(k)))):
        e = -F[k]
        if e > 0 and len(k) == 1:
            m += k[0][0] * e
        elif e > 0:
            t += '(' + es(dict(k)) + ')' + ('^' + str(e) if e > 1 else '')
            n += 1
    n += len(vs({m: 1})) if m else 0
    b = (str(c) if c != 1 or not (m or t) else '') + mo(m) + t
    a = pm({0: p}, ex(F, 1))
    t = es(a)
    if b == '1':
        return t
    # brackets round a top or bottom with a power or more than one piece,
    # so 2y^8/9 can not be read as 2y^(8/9): (2y^8)/9
    return ('(' + t + ')' if len(a) > 1 or '^' in t else t) + '/' + ('(' + b + ')' if n > 1 or '^' in b else b)


def npv():
    # each bottom met: the values that make it 0
    Z = []
    V = {}
    O = []
    for k in N:
        P = dict(k)
        v = vs(P)
        i = v[0]
        x = L[i]
        if len(P) == 1:
            Z.append(x)
            continue
        if P.get(0, 0) > 0 and [1 for j in P if P[j] < 0 or [1 for e in dg(j) if e % 2]] == []:
            # even powers, + only and a number (like x^4+4): never 0
            continue
        if len(v) > 1:
            x, t = one(P)
            if not x:
                O.append(t)
                continue
            if x not in V:
                V[x] = []
            V[x].append((9e99, t))
            continue
        n = max(dg(max(P)))
        c = [0] * (n + 1)
        for j in P:
            c[dg(j)[i] if j else 0] = P[j]
        if x not in V:
            V[x] = []
        z = V[x]
        if n == 1:
            g = gcd(c[0], c[1])
            z.append((-c[0] / c[1], str(-c[0] // g) + ('/' + str(c[1] // g)) * (c[1] > g)))
        elif n == 2:
            # (-b+sqrt(D))/(2a) and (-b-sqrt(D))/(2a), squares taken out
            C, B, A = c
            D = B * B - 4 * A * C
            if D > 0:
                s = 1
                j = 2
                while j < 1000 and j * j <= D:
                    while D % (j * j) == 0:
                        D //= j * j
                        s *= j
                    j += 1
                g = gcd(gcd(B, s), 2 * A)
                r = (str(s // g) if s > g else '') + 'sqrt(' + str(D) + ')'
                for h in '+-':
                    t = (str(-B // g) + h if B else '-' * (h == '-')) + r
                    if 2 * A > g:
                        t = ('(' + t + ')' if B else t) + '/' + str(2 * A // g)
                    z.append(((-B + (1 if h == '+' else -1) * s * D ** 0.5) / 2 / A, t))
        else:
            O.append(es(P))
    o = []
    for x in Z:
        if x in V:
            V[x].append((0, '0'))
        else:
            o.append(x)
    o.sort()
    o = [','.join(o) + '!=0'] if o else []
    for x in sorted(V):
        z = V[x]
        z.sort()
        if z:
            o.append(x + '!=' + ','.join([t[1] for t in z]))
    O.sort()
    for t in O:
        o.append(t + '!=0')
    return o


def one(P):
    # x+y -> x!=-y: a letter alone in one term, times 1 or -1, and in no
    # other term
    for i in ab():
        n = 0
        for j in P:
            d = dg(j)
            n += i < len(d) and d[i] > 0
        k = 1 << 16 * i
        if n == 1 and abs(P.get(k, 0)) == 1:
            Q = {}
            for j in P:
                if j != k:
                    Q[j] = -P[j] * P[k]
            return L[i], es(Q)
    return None, es(P)


def go(s):
    s = s.lower().replace(' ', '').replace('**', '^')
    if '=' in s:
        raise ValueError('no =: it simplifies')
    for t in (L, N):
        while t:
            t.pop()
    k = 0
    for c in s:
        k += (c == '(') - (c == ')')
    ts = tok(s + ')' * max(k, 0))
    if not ts:
        raise ValueError('nothing typed')
    v, i = pexpr(ts, 0)
    if i != len(ts):
        raise ValueError('bad ' + ts[i])
    v = fix(v)
    o = ['Ans: ' + fac(v)]
    if N:
        o.append('NPV: ' + ('; '.join(npv()) or 'none'))
    return o


# ---- the screen is 21 wide
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


def ask(t):
    # one fraction at a time, so no brackets are needed: its top, its
    # bottom (EXE alone for 1), then + - * / for another, or EXE to end.
    # A whole expression typed as a top, with EXE for the bottom, works.
    q = ''
    o = ''
    while True:
        t = t or input('Top:').strip()
        if not t:
            return q
        b = input('Bottom:').strip() or '1'
        q += o + '((' + t + ')/(' + b + '))'
        t = ''
        o = '?'
        while len(o) > 1 or o not in '+-*/':
            o = input('+ - * / or EXE:').strip()
        if not o:
            return q


print('Rational expressions')
print('Type each fraction:')
print('its top, its bottom,')
print('then + - * / or EXE')
s = ''
while True:
    try:
        s = ask(s)
    except (KeyboardInterrupt, EOFError):
        break
    if s == '':
        continue
    try:
        out = go(s)
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    s = ''
    ls = []
    for ln in out:
        ls += wrap(ln)
    try:
        for i in range(len(ls)):
            # typing a top at more.. skips the rest and starts on it
            if i and i % 6 == 0:
                s = input('more..').strip()
                if s:
                    break
            print(ls[i])
    except (KeyboardInterrupt, EOFError):
        break
