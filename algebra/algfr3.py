# ALGFR3 - simplifying fractions, part 3: the answer, with the top
# multiplied out and the bottom factored; with no letter in the bottom,
# the top factored too (Fac), with the steps (algfc) for a polynomial;
# and its NPVs (see algebra.py)
from algfr1 import *


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
    t = sorted(P, key=kk)
    # a + term first when one is as big as the first: x-c, not -c+x
    for k in t:
        if sum(dg(k)) < sum(dg(t[0])):
            break
        if P[k] > 0:
            t.remove(k)
            t.insert(0, k)
            break
    for k in t:
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
    if n > 1 or '^' in b and b[-1] != ')':
        b = '(' + b + ')'
    return ('(' + t + ')' if len(a) > 1 or '^' in t else t) + '/' + b


def ff(v):
    # the top fully factored, when there is no letter in the bottom and
    # it is more than one piece: 3xy(2x+3y), (x+1)(x-4), -(x-3)(x-2)
    p, q, F = v
    m = 0
    t = ''
    n = abs(p) != 1
    if not F and q == 1:
        # a whole number: its primes, 12 is 2^2*3
        a = abs(p)
        j = 2
        while j * j <= a:
            if j > 30000:
                # too big to finish: no Fac rather than a wrong one
                return ''
            e = 0
            while a % j == 0:
                a //= j
                e += 1
            if e:
                t += '*' + str(j) + ('^' + str(e) if e > 1 else '')
            j += 1
        if a > 1:
            t += '*' + str(a)
        return '-' * (p < 0) + t[1:] if t.find('*', 1) > 0 or t.find('^') > 0 else ''
    for k in sorted(F, key=lambda k: (len(k) > 1, es(dict(k)))):
        e = F[k]
        if e < 0:
            return ''
        if len(k) == 1:
            m += k[0][0] * e
        else:
            t += '(' + es(dict(k)) + ')' + ('^' + str(e) if e > 1 else '')
            n += e
    n += m != 0
    if n < 2:
        return ''
    t = ('-' if p == -1 else str(p) if p != 1 else '') + mo(m) + t
    return t + ('/' + str(q) if q != 1 else '')


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


def go(s, d=1):
    # d=0: just Ans and NPV (when the root part asks), with every bottom
    # typed an NPV
    s = s.lower().replace(' ', '').replace('**', '^')
    FL[0] = d
    FL[1] = 0
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
    t = ff(v) if d else ''
    # a polynomial typed alone (no bottom with a letter, more than one
    # term, one or two letters, in the order they come): the steps to
    # factor it too
    x = []
    for c in o[0][5:]:
        if c in LET and c not in x:
            x.append(c)
    a = pm({0: v[0]}, ex(v[2], 1))
    if d and not FL[1] and 0 < len(x) < 3 and len(a) > 1:
        # as {(x power, y power): number}, and its factors as numbers by
        # the power of x
        I = [L.index(c) for c in x] + [99]
        P = {}
        for k in a:
            e = dg(k) + [0] * 100
            P[(e[I[0]], e[I[1]])] = a[k]
        Q = []
        for k in v[2]:
            if v[2][k] > 0 and len(k) > 1:
                c = [0]
                for j in k:
                    e = dg(j[0]) + [0] * 100
                    while len(c) <= e[I[0]]:
                        c.append(0)
                    c[e[I[0]]] = j[1]
                Q.append(c)
        Q.sort(key=len)
        from algfc import steps
        try:
            # (a Fac that is the answer again says nothing new)
            o += [l for l in steps(P, v[1], Q, x) if l[5:] != o[0][5:]]
            t = ''
        except ValueError:
            pass
        # put the steps part away again: it is small to load, and the
        # memory is better kept for the rest
        from algcore import free
        free(('algfc',))
    if t and t != o[0][5:]:
        o.append('Fac: ' + t)
    if N:
        o.append('NPV: ' + ('; '.join(npv()) or 'none'))
    return o
