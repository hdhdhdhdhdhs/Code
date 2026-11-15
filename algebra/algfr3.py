# ALGFR3 - simplifying fractions, part 3: the answer, with the top
# multiplied out and the bottom factored, and its NPVs (see algebra.py)
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
