# ALGRT3 - simplifying with roots, part 3: the answer with its Restr and
# NPVs (see algebra.py)
from algrt2 import *


def go(s):
    for t in (R, L, U, ST, BX, RX):
        while t:
            t.pop()
    PS.clear()
    v = side(s)
    o = simp(v)
    # a number or letters in front of a root: the entire radical too,
    # 7sqrt(14) is sqrt(686)
    t = en(v)
    if t:
        o.insert(1 + (o[0][:5] == 'Restr'), 'Entire: ' + t)
    x = [t for t in L if t[0] != '(']
    # an answer with more letters and no roots left: cancelled and its
    # bottom factored, the same as for a fraction (with one letter, that
    # is done already)
    for i in range(len(o)):
        t = o[i]
        if len(x) > 1 and t[:4] == 'Ans:' and t.find('sqrt') < 0 and t.find('|') < 0 and t.find('~') < 0:
            from algfr3 import go as g
            try:
                o[i] = g(t[5:])[0]
            except ValueError:
                pass
    # Restr: what simplifying took as >= 0, and what each root needs.
    # NPV: where a bottom typed is 0. One letter: worked out exactly, as
    # for an equation. More letters: letters that make a bottom 0, the
    # rest factored as for a fraction, and a bottom with roots !=0.
    # Ans NPV: what makes one of the answer's bottoms 0 as well (times a
    # conjugate like 1-sqrt(x) adds x=1), when the NPVs do not have it
    r = o[0][7:].split(', ') if o[0][:5] == 'Restr' else []
    o = o[len(r) > 0:]
    n = []
    m = []
    a = bs([t[5:] for t in o if t[:4] == 'Ans:'][0])
    if len(x) > 1:
        Z = []
        for w in BX:
            nb(w[0], Z, n)
        k = len(BX)
        for t in a:
            try:
                side('1/(' + t + ')')
            except ValueError:
                pass
        Y = []
        for w in BX[k:]:
            nb(w[0], Y, m)
        n = nl(Z, n)
        m = [t for t in nl([c for c in Y if c not in Z], m) if t not in n]
        # what is under a root, when it is not just letters (those are
        # in Restr already)
        for v in RX:
            t = es(v[0], v[1]) + '>=0'
            if (len(v[0]) > 1 or t[0] == '-') and [c for c in t.replace('sqrt', '') if c in LET] and t not in r:
                r.append(t)
    elif x:
        try:
            from algeq3 import rn
            a, n, m = rn(s, a)
            for t in a:
                if t not in r:
                    r.append(t)
            if m and n and m[0].find('range') < 0:
                # only the values the NPVs do not have
                v = n[0].split('!=')[1].split(',')
                m = [t for t in m[0].split('!=')[1].split(',') if t not in v]
                m = [n[0].split('!=')[0] + '!=' + ','.join(m)] if m else []
            n = [t[5:] for t in n]
            m = [t[5:] if t[:5] == 'NPV: ' else t for t in m]
        except ValueError:
            pass
    o.insert(1, 'Ans NPV: ' + '; '.join(m)) if m else 0
    return (['Restr: ' + ', '.join(r)] if r else []) + (['NPV: ' + '; '.join(n)] if n else []) + o


def en(v):
    # one term, n times letters times roots (no bottom): it all under
    # one root, sqrt(n^2 letters^2 what is under the roots)
    c, d = v
    if len(c) != 1 or d != 1:
        return ''
    for k in c:
        n = c[k]
    if not k[1] or (abs(n) < 2 and not k[0]):
        return ''
    for e in dg(k[0]):
        if e < 0:
            return ''
    X = {(2 * k[0], 0): n * n}
    j = 0
    m = k[1]
    while m:
        if m & 1:
            for q in R[j]:
                if q[1]:
                    return ''
            if sq(R[j]):
                return ''
            X = pm(X, R[j])
        m >>= 1
        j += 1
    # x in front, when nothing says x>=0, only goes under when it is
    t = ''
    e = dg(k[0])
    for i in range(len(e)):
        if e[i] & 1 and L[i] not in U:
            t += ', ' + L[i] + '>=0'
    return '-' * (n < 0) + 'sqrt(' + es(X, 1) + ')' + t


def nl(Z, n):
    # the NPV pieces: letters that make a bottom 0 first (x,y!=0)
    z = []
    for c in Z:
        if c not in z:
            z.append(c)
    z.sort()
    return ([','.join(z) + '!=0'] if z else []) + n


def nb(c, Z, n):
    # where c is 0, for the NPVs: letters that make it 0 go in Z, the
    # rest in n. One term is 0 when a letter in it is, or what is under
    # a root in it; with no roots it is factored, as for a fraction
    if len(c) == 1:
        for k in c:
            pass
        e = dg(k[0])
        for i in range(len(e)):
            if e[i] > 0 and L[i][0] != '(':
                Z.append(L[i])
            elif e[i]:
                nb2(L[i], Z, n)
        j = 0
        m = k[1]
        while m:
            if m & 1:
                nb(R[j], Z, n)
            m >>= 1
            j += 1
    elif sh(c, Z, n):
        pass
    elif c.get((0, 0), 0) < 1 or [k for k in c if c[k] < 0 or k[0]]:
        # (a number and roots, all +, is never 0.) Letters below 0 are
        # NPVs already, so they are cleared: ysqrt(x)+xsqrt(y), not
        # sqrt(x)/x+sqrt(y)/y
        z = 0
        for i in range(len(L)):
            t = 0
            for k in c:
                e = dg(k[0])
                if i < len(e) and e[i] < t and L[i][0] != '(':
                    t = e[i]
            z += t << (8 * i)
        d = {}
        for k in c:
            d[(k[0] - z, k[1])] = c[k]
        nb2(es(d, 1), Z, n)


def sh(c, Z, n):
    # a root or letter every term of c has: c is 0 where it is, or
    # where the rest is. Returns 1 when it did that
    m = -1
    z = 0
    for k in c:
        m &= k[1]
    for i in range(len(L)):
        t = 99
        for k in c:
            e = dg(k[0])
            t = min(t, e[i] if i < len(e) else 0)
        if t > 0 and L[i][0] != '(':
            Z.append(L[i])
            z += t << (8 * i)
    if not (m or z):
        return 0
    j = 0
    while m >> j:
        if m >> j & 1:
            nb(R[j], Z, n)
        j += 1
    d = {}
    for k in c:
        d[(k[0] - z, k[1] & ~m)] = c[k]
    nb(d, Z, n)
    return 1


def nb2(t, Z, n):
    if not [c for c in t.replace('sqrt', '') if c in LET]:
        return
    if t.find('sqrt') < 0 and t.find('|') < 0:
        from algfr3 import go as g
        for t in g('1/(' + t + ')')[1][5:].split('; '):
            if t[1:3] == '!=' and t[0] in LET:
                # x!=0,2 is x in Z, and x!=2
                v = t[3:].split(',')
                if '0' in v:
                    Z.append(t[0])
                    v.remove('0')
                t = t[:3] + ','.join(v) if v else ''
            elif t[-3:] == '!=0' and not [c for c in t[:-3] if c not in LET + ',']:
                Z += t[:-3].split(',')
                t = ''
            if t[1:3] == '!=' and t[0] in LET:
                # one line for each letter: x!=-y,y
                for i in range(len(n)):
                    if n[i][:3] == t[:3]:
                        for v in t[3:].split(','):
                            if v not in n[i][3:].split(','):
                                n[i] += ',' + v
                        t = ''
            if t and t not in n and t != 'none':
                n.append(t)
    elif t + '!=0' not in n:
        n.append(t + '!=0')


def bs(t):
    # the bottoms in an answer: what follows each /
    o = []
    for i in range(len(t)):
        if t[i] == '/':
            j = i + 1
            e = 0
            while j < len(t) and (e or t[j] not in '+-/)'):
                e += (t[j] == '(') - (t[j] == ')')
                j += 1
            o.append(t[i + 1:j])
    return o
