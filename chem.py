W = 21
EL = (" H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe"
      " Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In"
      " Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf"
      " Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am"
      " Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og ")
MET = (" Li Na K Rb Cs Fr Be Mg Ca Sr Ba Ra Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga"
       " Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb La Hf Ta W Re Os Ir Pt Au Hg"
       " Tl Pb Bi Po Al ")
PY = (" NH4:1 OH:-1 NO3:-1 NO2:-1 HCO3:-1 HSO4:-1 H2PO4:-1 ClO:-1 ClO2:-1"
      " ClO3:-1 ClO4:-1 BrO3:-1 IO3:-1 MnO4:-1 CN:-1 SCN:-1 C2H3O2:-1 CO3:-2"
      " SO4:-2 SO3:-2 S2O3:-2 CrO4:-2 Cr2O7:-2 C2O4:-2 HPO4:-2 SiO3:-2"
      " PO4:-3 PO3:-3 AsO4:-3 BO3:-3 ")
CT = (" Li:1 Na:1 K:1 Rb:1 Cs:1 Fr:1 Ag:1 H:1 Be:2 Mg:2 Ca:2 Sr:2 Ba:2 Ra:2"
      " Zn:2 Cd:2 Ni:2 Co:2 Mn:2 Cu:2 Hg:2 Sn:2 Pb:2 Fe:2 Al:3 Ga:3 In:3"
      " Cr:3 Bi:3 Ti:4 Si:4 C:4 ")
AT = " F:-1 Cl:-1 Br:-1 I:-1 At:-1 O:-2 S:-2 Se:-2 Te:-2 N:-3 P:-3 As:-3 C:-4 "
AC = " Li K Ba Sr Ca Na Mg Al Mn Zn Cr Fe Cd Co Ni Sn Pb H Cu Ag Hg Pt Au "
HL = " F Cl Br I "
DI = " H:H2 N:N2 O:O2 F:F2 Cl:Cl2 Br:Br2 I:I2 "
MU = (" Fe:2,3 Cu:1,2 Sn:2,4 Pb:2,4 Cr:2,3 Mn:2,4 Co:2,3 Ni:2,3 Hg:1,2"
      " Au:1,3 Ti:3,4 ")
OX = (" CO2:H2CO3 SO2:H2SO3 SO3:H2SO4 N2O5:HNO3 N2O3:HNO2 P2O5:H3PO4"
      " Cl2O7:HClO4 ")
CV = (" NH:NH3 CH:CH4 SiH:SiH4 PH:PH3 CO:CO2 SO:SO2 NO:NO PO:P2O5 HO:H2O"
      " HS:H2S FeO:Fe2O3 ")
S2 = (" He Li Be Ne Na Mg Al Si Cl Ar Ca Ti Cr Mn Fe Co Ni Cu Zn Ga Ge As Se"
      " Br Kr Rb Sr Ag Cd Sn Sb Te Xe Cs Ba Pt Au Hg Pb Bi ")
SP = ('co', 'no', 'cn', 'hf', 'po', 'nh')
PK = {}


def sv(t, k):
    i = t.find(' ' + k + ':')
    if i < 0:
        return None
    j = i + len(k) + 2
    return t[j:t.find(' ', j)]


def nv(t, k):
    v = sv(t, k)
    return int(v) if v is not None else None


def inn(t, k):
    return k != '' and (' ' + k + ' ') in t


def dg(s, i):
    m = 0
    h = 0
    while i < len(s) and s[i].isdigit():
        m = m * 10 + int(s[i])
        i += 1
        h = 1
    return (m if h else 1), i


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def pf(s):
    st = [{}]
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '(':
            st.append({})
            i += 1
        elif c == ')':
            m, i = dg(s, i + 1)
            t = st.pop()
            if not st:
                raise ValueError('bad ()')
            for k in t:
                st[-1][k] = st[-1].get(k, 0) + t[k] * m
        elif c.isupper():
            y = c
            i += 1
            while i < n and s[i].islower():
                y += s[i]
                i += 1
            if not inn(EL, y):
                raise ValueError('no element ' + y)
            m, i = dg(s, i)
            st[-1][y] = st[-1].get(y, 0) + m
        else:
            raise ValueError('bad char ' + c)
    if len(st) != 1:
        raise ValueError('bad ()')
    return st[0]


def lu(s):
    if s.startswith('NH4'):
        i = 3
    elif s.startswith('('):
        d = 0
        i = 0
        while i < len(s):
            if s[i] == '(':
                d += 1
            elif s[i] == ')':
                d -= 1
                if d == 0:
                    break
            i += 1
        inr = s[1:i]
        m, i = dg(s, i + 1)
        return inr, m, s[i:]
    elif s and s[0].isupper():
        i = 1
        while i < len(s) and s[i].islower():
            i += 1
    else:
        raise ValueError('bad formula')
    y = s[:i]
    m, i = dg(s, i)
    return y, m, s[i:]


def si(f):
    try:
        c, nc, r = lu(f)
    except Exception:
        return None
    if r == '':
        return None
    if r.startswith('('):
        a, na, rr = lu(r)
        if rr != '':
            return None
    elif sv(PY, r) is not None:
        a, na = r, 1
    else:
        try:
            a, na, rr = lu(r)
        except Exception:
            return None
        if rr != '' or not inn(EL, a):
            return None
    ac = nv(PY, a)
    if ac is None or ac > 0:
        ac = nv(AT, a)
    if ac is None:
        return None
    need = -na * ac
    cc = None
    if nc > 0 and need > 0 and need % nc == 0:
        cc = need // nc
    if cc is None:
        cc = nv(PY, c)
        if cc is None or cc < 0:
            cc = nv(CT, c)
    if cc is None:
        return None
    return (c, cc, nc, a, ac, na)


def wi(y, n):
    if n == 1:
        return y
    if sv(PY, y) is not None:
        return '(' + y + ')' + str(n)
    return y + str(n)


def mk(c, cc, a, ac):
    x = abs(ac)
    b = abs(cc)
    g = gcd(x, b)
    if g:
        x //= g
        b //= g
    return wi(c, x) + wi(a, b)


def bal(cs, nl):
    ps = [pf(c) for c in cs]
    els = []
    for q in ps:
        for e in q:
            if e not in els:
                els.append(e)
    nc = len(cs)
    rw = [[(ps[i].get(e, 0) if i < nl else -ps[i].get(e, 0))
           for i in range(nc)] for e in els]
    pv = []
    r = 0
    for c in range(nc):
        k = -1
        for q in range(r, len(rw)):
            if rw[q][c]:
                k = q
                break
        if k < 0:
            continue
        rw[r], rw[k] = rw[k], rw[r]
        for q in range(len(rw)):
            if q != r and rw[q][c]:
                a = rw[r][c]
                b = rw[q][c]
                g = gcd(a, b) or 1
                rw[q] = [(a // g) * rw[q][z] - (b // g) * rw[r][z]
                         for z in range(nc)]
        pv.append(c)
        r += 1
        if r == len(rw):
            break
    fr = [c for c in range(nc) if c not in pv]
    nf = len(fr)
    if not nf:
        raise ValueError('cannot balance')
    lim = 6 if nf == 1 else (4 if nf == 2 else 2)
    tot = 1
    for _ in range(nf):
        tot *= lim
        if tot > 512:
            tot = 512
            break
    best = None
    for z in range(tot):
        o = [0] * nc
        dn = [1] * nc
        for j in range(nf):
            o[fr[j]] = z % lim + 1
            z //= lim
        for i in range(len(pv)):
            c = pv[i]
            t = 0
            for j in range(nf):
                t += rw[i][fr[j]] * o[fr[j]]
            o[c] = -t
            dn[c] = rw[i][c]
        L = 1
        for x in dn:
            L = L * (x // gcd(L, x))
        L = abs(L)
        o = [o[i] * (L // dn[i]) for i in range(nc)]
        g = 0
        for x in o:
            g = gcd(g, x)
        if g:
            o = [x // g for x in o]
        if o[0] < 0:
            o = [-x for x in o]
        t = 0
        for x in o:
            if x <= 0:
                t = -1
                break
            t += x
        if t > 0 and (best is None or t < best[0]):
            best = (t, o)
    if best is None:
        raise ValueError('cannot balance')
    return best[1]


def chk(cs, co, nl):
    L = {}
    R = {}
    for i in range(len(cs)):
        f = pf(cs[i])
        t = L if i < nl else R
        for e in f:
            t[e] = t.get(e, 0) + f[e] * co[i]
    return L == R


def ae(f):
    p = pf(f)
    if len(p) == 1:
        for k in p:
            return k
    return None


def ef(y):
    d = sv(DI, y)
    if d:
        return d
    if y == 'P':
        return 'P4'
    if y == 'S':
        return 'S8'
    return y


def cc_of(y):
    if y in PK:
        return PK[y]
    v = nv(PY, y)
    if v is not None and v > 0:
        return v
    return nv(CT, y)


def ac_of(y):
    v = nv(PY, y)
    if v is not None and v < 0:
        return v
    return nv(AT, y)


def rank(y):
    return AC.find(' ' + y + ' ')


def p1(rs):
    if len(rs) != 2:
        raise ValueError('need 2')
    a, b = rs[0], rs[1]
    x, y = ae(a), ae(b)
    if x and y:
        v = sv(CV, x + y) or sv(CV, y + x)
        if v:
            return rs + [v], 2
        for u, w in ((x, y), (y, x)):
            if (inn(MET, u) or u == 'H') and ac_of(w) is not None:
                return rs + [mk(u, cc_of(u), w, ac_of(w))], 2
        raise ValueError('cannot predict')
    if 'H2O' in rs:
        o = a if b == 'H2O' else b
        v = sv(OX, o)
        if v:
            return rs + [v], 2
        s = si(o)
        if s and s[3] == 'O' and inn(MET, s[0]):
            return rs + [mk(s[0], s[1], 'OH', -1)], 2
    if 'CO2' in rs:
        o = a if b == 'CO2' else b
        s = si(o)
        if s and s[3] == 'O' and inn(MET, s[0]):
            return rs + [mk(s[0], s[1], 'CO3', -2)], 2
    raise ValueError('cannot predict')


def p2(rs):
    if len(rs) != 1:
        raise ValueError('need 1')
    f = rs[0]
    if f == 'H2CO3':
        return rs + ['H2O', 'CO2'], 1
    s = si(f)
    if s and inn(MET, s[0]):
        c, cc, a = s[0], s[1], s[3]
        if a == 'CO3':
            return rs + [mk(c, cc, 'O', -2), 'CO2'], 1
        if a == 'OH':
            return rs + [mk(c, cc, 'O', -2), 'H2O'], 1
        if a == 'ClO3':
            return rs + [mk(c, cc, 'Cl', -1), 'O2'], 1
        if a == 'NO3':
            return rs + [mk(c, cc, 'NO2', -1), 'O2'], 1
    if s and s[0] == 'NH4':
        h = mk('H', 1, s[3], s[4])
        if h == 'HOH':
            h = 'H2O'
        if h == 'H2CO3':
            return rs + ['NH3', 'H2O', 'CO2'], 1
        return rs + ['NH3', h], 1
    p = pf(f)
    if len(p) == 2:
        o = list(p)
        o.sort(key=f.find)
        return rs + [ef(e) for e in o], 1
    raise ValueError('cannot predict')


def p3(rs):
    if len(rs) != 2:
        raise ValueError('need 2')
    el = cp = None
    for x in rs:
        if ae(x) and el is None:
            el = x
        else:
            cp = x
    if el is None or cp is None:
        raise ValueError('need element+cmpd')
    e = ae(el)
    s = si(cp)
    if s is None:
        raise ValueError('cannot read ' + cp)
    c, cc, a, ac = s[0], s[1], s[3], s[4]
    if inn(MET, e):
        if cp == 'H2O':
            if 0 <= rank(e) < rank('H'):
                return [el, cp, mk(e, cc_of(e), 'OH', -1), 'H2'], 2
            raise ValueError('no reaction')
        if c == 'H':
            if 0 <= rank(e) < rank('H'):
                return [el, cp, mk(e, cc_of(e), a, ac), 'H2'], 2
            raise ValueError('no reaction')
        if inn(MET, c):
            if 0 <= rank(e) < rank(c):
                return [el, cp, mk(e, cc_of(e), a, ac), ef(c)], 2
            raise ValueError('no reaction')
    if inn(HL, e) and inn(HL, a):
        if HL.find(' ' + e + ' ') < HL.find(' ' + a + ' '):
            return [el, cp, mk(c, cc, e, ac_of(e)), ef(a)], 2
        raise ValueError('no reaction')
    raise ValueError('cannot predict')


def p4(rs):
    if len(rs) != 2:
        raise ValueError('need 2')
    x, y = si(rs[0]), si(rs[1])
    if x is None or y is None:
        raise ValueError('cannot read')
    o = []
    for a, b in ((x, y), (y, x)):
        f = mk(a[0], a[1], b[3], b[4])
        o.append('H2O' if f == 'HOH' else f)
    return rs + o, 2


def p5(rs):
    fu = None
    for x in rs:
        if x != 'O2':
            fu = x
    if fu is None:
        raise ValueError('need fuel')
    p = pf(fu)
    if 'C' not in p or 'H' not in p:
        raise ValueError('need C+H fuel')
    for e in p:
        if e not in ('C', 'H', 'O', 'S', 'N'):
            raise ValueError('cannot burn ' + e)
    pr = ['CO2', 'H2O']
    if 'S' in p:
        pr.append('SO2')
    if 'N' in p:
        pr.append('NO2')
    return [fu, 'O2'] + pr, 2


def p6(rs):
    if len(rs) != 2:
        raise ValueError('need acid+base')
    ac = bs = None
    for x in rs:
        s = si(x)
        if s is None:
            continue
        if s[0] == 'H' and ac is None and x not in ('H2', 'He', 'Hg'):
            ac = x
        elif s[3] == 'OH':
            bs = x
    if ac is None or bs is None:
        raise ValueError('need acid+base')
    a, b = si(ac), si(bs)
    return [ac, bs, mk(b[0], b[1], a[3], a[4]), 'H2O'], 2


PR = (p1, p2, p3, p4, p5, p6)
MN = ('Synthesis,Decomposition,Single Replace,Double Replace,Combustion,'
      'Acid + Base,Auto / Balance').split(',')
AU = (4, 5, 2, 3, 0, 1)
AK = (['C1:', 'C2:'], ['Compound:'], ['Element:', 'Compound:'],
      ['C1:', 'C2:'], ['Fuel:'], ['Acid:', 'Base:'])


def eqs(cs, co, nl):
    p = [('' if co[i] == 1 else str(co[i])) + cs[i] for i in range(len(cs))]
    return ' + '.join(p[:nl]) + ' -> ' + ' + '.join(p[nl:])


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


def sp(side):
    return [p.strip() for p in side.split('+') if p.strip() != '']


def fix(s):
    o = ''
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isalpha():
            pr = (c + s[i + 1]).lower() if i + 1 < n and s[i + 1].isalpha() \
                else ''
            if pr and pr not in SP and inn(S2, pr[0].upper() + pr[1]):
                o += pr[0].upper() + pr[1]
                i += 2
                continue
            if inn(EL, c.upper()):
                o += c.upper()
                i += 1
                continue
            if pr and inn(S2, pr[0].upper() + pr[1]):
                o += pr[0].upper() + pr[1]
                i += 2
                continue
            raise ValueError('no element ' + c)
        o += c
        i += 1
    return o


def rb(t):
    if '->' in t:
        L, R = t.split('->', 1)
    elif '=' in t:
        L, R = t.split('=', 1)
    else:
        return None
    a = sp(L)
    cs = a + sp(R)
    co = bal(cs, len(a))
    if not chk(cs, co, len(a)):
        raise ValueError('cannot balance')
    return cs, co, len(a)


def solve(t, n):
    if '->' in t or '=' in t:
        r = rb(t)
        if r is None:
            raise ValueError('bad input')
        return r[0], r[1], r[2], 'BALANCED'
    rs = sp(t)
    order = ([n - 1] + list(AU)) if n < 7 else list(AU)
    for i in order:
        try:
            cs, nl = PR[i](rs)
            co = bal(cs, nl)
            if chk(cs, co, nl):
                return cs, co, nl, MN[i]
        except Exception:
            pass
    raise ValueError('cannot predict')


def rd(pr):
    it = []
    for p in pr:
        try:
            v = input(p).strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if v == '':
            break
        for q in sp(v):
            it.append(q)
    return it


def rdn(tag):
    return rd([tag + str(i + 1) + ':' for i in range(8)])


def askq(rs):
    seen = []
    for it in rs:
        try:
            e = ae(fix(it))
        except Exception:
            e = None
        if e is None or e in seen:
            continue
        ov = sv(MU, e)
        if ov is None:
            continue
        seen.append(e)
        op = [int(x) for x in ov.split(',')]
        print(e + ' charge?')
        for i in range(len(op)):
            print(str(i + 1) + ' ' + e + str(op[i]) + '+')
        try:
            a = input('Pick:').strip()
        except (KeyboardInterrupt, EOFError):
            return 0
        PK[e] = op[int(a) - 1 if a.isdigit() and 1 <= int(a) <= len(op) else 0]
    return 1


while True:
    for i in range(7):
        print(str(i + 1) + ' ' + MN[i])
    try:
        k = input('Pick 1-7:').strip()
    except (KeyboardInterrupt, EOFError):
        break
    if k not in ('1', '2', '3', '4', '5', '6', '7'):
        if k != '':
            print('1 to 7 only')
        continue
    n = int(k)
    PK.clear()
    ps = []
    try:
        if n == 7:
            print('1 by 1. EXE=done')
            rs = rdn('C')
            if rs is None:
                break
            if not rs:
                continue
            print('Products?')
            print('none=auto')
            ps = rdn('P')
            if ps is None:
                break
        else:
            rs = rd(AK[n - 1])
            if rs is None:
                break
            if not rs:
                continue
    except (KeyboardInterrupt, EOFError):
        break
    if ps:
        t = ' + '.join(rs) + ' -> ' + ' + '.join(ps)
    else:
        if not askq(rs):
            break
        t = ' + '.join(rs)
    try:
        t2 = fix(t)
    except Exception:
        t2 = t
    r = None
    er = 'bad input'
    for cand in (t, t2):
        try:
            r = solve(cand, n)
            break
        except Exception as e:
            if str(e):
                er = str(e)
        if t2 == t:
            break
    if r is None:
        if er == 'cannot predict' and not ps:
            er = 'type products in' if n == 7 else 'try opt 7'
        for ln in wrap('Err: ' + er):
            print(ln)
    else:
        print('[' + r[3] + ']')
        for ln in wrap(eqs(r[0], r[1], r[2])):
            print(ln)
    try:
        input('EXE=menu')
    except (KeyboardInterrupt, EOFError):
        break
