# CHEM - chemical equation balancer + product predictor
# Casio fx-9750GIII  (MicroPython 1.9.4)

W = 21

_ELS = (" H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe "
        "Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In "
        "Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf "
        "Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am "
        "Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og ")


def is_element(s):
    return s != '' and (' ' + s + ' ') in _ELS

DIA = " H:H2 N:N2 O:O2 F:F2 Cl:Cl2 Br:Br2 I:I2 "

POLY = (" NH4:1 OH:-1 NO3:-1 NO2:-1 HCO3:-1 HSO4:-1 H2PO4:-1 ClO:-1 ClO2:-1"
        " ClO3:-1 ClO4:-1 BrO3:-1 IO3:-1 MnO4:-1 CN:-1 SCN:-1 C2H3O2:-1"
        " CO3:-2 SO4:-2 SO3:-2 S2O3:-2 CrO4:-2 Cr2O7:-2 C2O4:-2 HPO4:-2"
        " SiO3:-2 PO4:-3 PO3:-3 AsO4:-3 BO3:-3 ")

CAT = (" Li:1 Na:1 K:1 Rb:1 Cs:1 Fr:1 Ag:1 H:1 Be:2 Mg:2 Ca:2 Sr:2 Ba:2"
       " Ra:2 Zn:2 Cd:2 Ni:2 Co:2 Mn:2 Cu:2 Hg:2 Sn:2 Pb:2 Fe:2 Al:3 Ga:3"
       " In:3 Cr:3 Bi:3 Ti:4 Si:4 C:4 ")

AN = (" F:-1 Cl:-1 Br:-1 I:-1 At:-1 O:-2 S:-2 Se:-2 Te:-2 N:-3 P:-3"
      " As:-3 C:-4 H:-1 ")

ACT = (" Li K Ba Sr Ca Na Mg Al Mn Zn Cr Fe Cd Co Ni Sn Pb H Cu Ag Hg"
       " Pt Au ")
HAL = " F Cl Br I "

MUL = (" Fe:2,3 Cu:1,2 Sn:2,4 Pb:2,4 Cr:2,3 Mn:2,4 Co:2,3 Ni:2,3 Hg:1,2"
       " Au:1,3 Ti:3,4 ")

OXA = (" CO2:H2CO3 SO2:H2SO3 SO3:H2SO4 N2O5:HNO3 N2O3:HNO2 P2O5:H3PO4"
       " P4O10:H3PO4 Cl2O7:HClO4 ")

COV = (" NH:NH3 CH:CH4 SiH:SiH4 PH:PH3 CO:CO2 SO:SO2 NO:NO PO:P2O5"
       " HO:H2O HS:H2S FeO:Fe2O3 BO:B2O3 ")


def sval(tab, key):
    """Text value for key in a ' k:v k:v ' table, or None."""
    i = tab.find(' ' + key + ':')
    if i < 0:
        return None
    j = i + len(key) + 2
    k = tab.find(' ', j)
    return tab[j:k]


def nval(tab, key):
    """Number value for key, or None."""
    v = sval(tab, key)
    return int(v) if v is not None else None


def intab(tab, key):
    return (' ' + key + ' ') in tab


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def parse_formula(s):
    stack = [{}]
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '(':
            stack.append({})
            i += 1
        elif c == ')':
            i += 1
            num = 0
            has = False
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
                has = True
            if not has:
                num = 1
            top = stack.pop()
            if not stack:
                raise ValueError('bad ()')
            for k in top:
                stack[-1][k] = stack[-1].get(k, 0) + top[k] * num
        elif c.isupper():
            sym = c
            i += 1
            while i < n and s[i].islower():
                sym += s[i]
                i += 1
            if not is_element(sym):
                raise ValueError('no element ' + sym)
            num = 0
            has = False
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
                has = True
            if not has:
                num = 1
            stack[-1][sym] = stack[-1].get(sym, 0) + num
        else:
            raise ValueError('bad char ' + c)
    if len(stack) != 1:
        raise ValueError('bad ()')
    return stack[0]


def lead_unit(s):
    if s.startswith('NH4'):
        i = 3
        num = 0
        has = False
        while i < len(s) and s[i].isdigit():
            num = num * 10 + int(s[i])
            i += 1
            has = True
        return 'NH4', (num if has else 1), s[i:]
    if s.startswith('('):
        depth = 0
        i = 0
        while i < len(s):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        inner = s[1:i]
        i += 1
        num = 0
        has = False
        while i < len(s) and s[i].isdigit():
            num = num * 10 + int(s[i])
            i += 1
            has = True
        return inner, (num if has else 1), s[i:]
    if not s or not s[0].isupper():
        raise ValueError('bad formula')
    sym = s[0]
    i = 1
    while i < len(s) and s[i].islower():
        sym += s[i]
        i += 1
    num = 0
    has = False
    while i < len(s) and s[i].isdigit():
        num = num * 10 + int(s[i])
        i += 1
        has = True
    return sym, (num if has else 1), s[i:]


def strip_group(s):
    if s.startswith('('):
        sym, cnt, rest = lead_unit(s)
        if rest == '':
            return sym, cnt
        return None, 0
    if sval(POLY, s) is not None:
        return s, 1
    try:
        sym, cnt, rest = lead_unit(s)
    except Exception:
        return None, 0
    if rest == '' and is_element(sym):
        return sym, cnt
    return None, 0


def split_ion(formula):
    try:
        cat, ncat, rest = lead_unit(formula)
    except Exception:
        return None
    if rest == '':
        return None
    an, nan = strip_group(rest)
    if an is None:
        return None
    ac = None
    ac = nval(POLY, an)
    if ac is None or ac > 0:
        ac = nval(AN, an)
    if ac is None:
        return None
    # the formula itself pins the cation charge: Fe2(SO4)3 means Fe is +3,
    # not whatever the table's default happens to be. Only fall back to the
    # table when the subscripts do not divide evenly.
    cc = None
    need = -nan * ac
    if ncat > 0 and need > 0 and need % ncat == 0:
        cc = need // ncat
    if cc is None:
        cc = nval(POLY, cat)
        if cc is None or cc < 0:
            cc = nval(CAT, cat)
    if cc is None:
        return None
    return (cat, cc, ncat, an, ac, nan)


def wrap_ion(sym, n):
    if n == 1:
        return sym
    if sval(POLY, sym) is not None:
        return '(' + sym + ')' + str(n)
    return sym + str(n)


def make_ionic(cat, cc, an, ac):
    a = abs(ac)
    b = abs(cc)
    g = gcd(a, b)
    if g:
        a = a // g
        b = b // g
    return wrap_ion(cat, a) + wrap_ion(an, b)


# ---------------- balancing ----------------

def _elim(rows, ncols):
    pivots = []
    r = 0
    for c in range(ncols):
        piv = -1
        for rr in range(r, len(rows)):
            if rows[rr][c] != 0:
                piv = rr
                break
        if piv < 0:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for rr in range(len(rows)):
            if rr != r and rows[rr][c] != 0:
                a = rows[r][c]
                b = rows[rr][c]
                g = gcd(a, b) or 1
                m1 = a // g
                m2 = b // g
                rows[rr] = [m1 * rows[rr][k] - m2 * rows[r][k]
                            for k in range(ncols)]
        pivots.append(c)
        r += 1
        if r == len(rows):
            break
    return pivots


def _solve_with(rows, pivots, free, vals, ncols):
    nums = [0] * ncols
    dens = [1] * ncols
    for i in range(len(free)):
        nums[free[i]] = vals[i]
    for i in range(len(pivots)):
        c = pivots[i]
        tot = 0
        for j in range(len(free)):
            tot += rows[i][free[j]] * vals[j]
        nums[c] = -tot
        dens[c] = rows[i][c]
    L = 1
    for d in dens:
        if d:
            L = L * (d // gcd(L, d))
    L = abs(L)
    if L == 0:
        return None
    out = []
    for i in range(ncols):
        if dens[i] == 0:
            return None
        out.append(nums[i] * (L // dens[i]))
    g = 0
    for x in out:
        g = gcd(g, x)
    if g:
        out = [x // g for x in out]
    if out and out[0] < 0:
        out = [-x for x in out]
    for x in out:
        if x <= 0:
            return None
    return out


def balance(compounds, nl):
    parsed = [parse_formula(c) for c in compounds]
    elements = []
    for p in parsed:
        for e in p:
            if e not in elements:
                elements.append(e)
    ncols = len(compounds)
    rows = []
    for e in elements:
        row = []
        for idx in range(ncols):
            v = parsed[idx].get(e, 0)
            row.append(v if idx < nl else -v)
        rows.append(row)
    pivots = _elim(rows, ncols)
    free = [c for c in range(ncols) if c not in pivots]
    if not free:
        raise ValueError('cannot balance')
    if len(free) == 1:
        s = _solve_with(rows, pivots, free, [1], ncols)
        if s:
            return s
        raise ValueError('cannot balance')
    best = None
    lim = 6 if len(free) <= 2 else 3
    combos = [[]]
    for _ in range(len(free)):
        nc = []
        for base in combos:
            for v in range(1, lim + 1):
                nc.append(base + [v])
        combos = nc
        if len(combos) > 2000:
            break
    for vals in combos:
        if len(vals) != len(free):
            continue
        s = _solve_with(rows, pivots, free, vals, ncols)
        if s:
            tot = 0
            for x in s:
                tot += x
            if best is None or tot < best[0]:
                best = (tot, s)
    if best:
        return best[1]
    raise ValueError('cannot balance')


def check_balanced(compounds, coeffs, nl):
    L = {}
    R = {}
    for i in range(len(compounds)):
        f = parse_formula(compounds[i])
        tgt = L if i < nl else R
        for e in f:
            tgt[e] = tgt.get(e, 0) + f[e] * coeffs[i]
    return L == R


# ---------------- prediction helpers ----------------

def as_element(formula):
    f = parse_formula(formula)
    if len(f) == 1:
        for k in f:
            return k
    return None


def elem_form(sym):
    d = sval(DIA, sym)
    if d is not None:
        return d
    if sym == 'P':
        return 'P4'
    if sym == 'S':
        return 'S8'
    return sym


# metals a student actually meets with more than one common charge
# filled in from the menu when the user picks a charge for this run
PICKED = {}


def charge_of_cat(sym):
    if sym in PICKED:
        return PICKED[sym]
    v = nval(POLY, sym)
    if v is not None and v > 0:
        return v
    return nval(CAT, sym)


def charge_of_an(sym):
    v = nval(POLY, sym)
    if v is not None and v < 0:
        return v
    return nval(AN, sym)


def activity_rank(sym):
    return ACT.find(' ' + sym + ' ')


def is_acid(f):
    if f in ('H2', 'He', 'Hf', 'Hg', 'Ho', 'Hs'):
        return False
    if not f.startswith('H'):
        return False
    si = split_ion(f)
    return si is not None and si[0] == 'H'


def has_oh(f):
    si = split_ion(f)
    return si is not None and si[3] == 'OH'


# ---------------- predictors ----------------

NM_OXIDE_ACID = {'CO2': 'H2CO3', 'SO2': 'H2SO3', 'SO3': 'H2SO4',
                 'N2O5': 'HNO3', 'N2O3': 'HNO2', 'P2O5': 'H3PO4',
                 'P4O10': 'H3PO4', 'Cl2O7': 'HClO4'}

COVALENT = {'NH': 'NH3', 'CH': 'CH4', 'SiH': 'SiH4', 'PH': 'PH3',
            'CO': 'CO2', 'SO': 'SO2', 'NO': 'NO', 'PO': 'P2O5',
            'HO': 'H2O', 'HS': 'H2S', 'FeO': 'Fe2O3', 'BO': 'B2O3'}


def _cov(a, b):
    k1 = a + b
    k2 = b + a
    v = sval(COV, k1)
    if v is None:
        v = sval(COV, k2)
    return v


def predict_synthesis(rs):
    if len(rs) != 2:
        raise ValueError('need 2 reactants')
    a = rs[0]
    b = rs[1]
    ea = as_element(a)
    eb = as_element(b)
    if ea and eb:
        c = _cov(ea, eb)
        if c:
            return rs + [c], 2
        if is_metal(ea) and charge_of_an(eb) is not None:
            return rs + [make_ionic(ea, charge_of_cat(ea), eb,
                                    charge_of_an(eb))], 2
        if is_metal(eb) and charge_of_an(ea) is not None:
            return rs + [make_ionic(eb, charge_of_cat(eb), ea,
                                    charge_of_an(ea))], 2
        if ea == 'H' and charge_of_an(eb) is not None:
            return rs + [make_ionic('H', 1, eb, charge_of_an(eb))], 2
        if eb == 'H' and charge_of_an(ea) is not None:
            return rs + [make_ionic('H', 1, ea, charge_of_an(ea))], 2
        raise ValueError('cannot predict')
    if b == 'H2O' or a == 'H2O':
        ox = a if b == 'H2O' else b
        v = sval(OXA, ox)
        if v is not None:
            return rs + [v], 2
        si = split_ion(ox)
        if si and si[3] == 'O' and is_metal(si[0]):
            return rs + [make_ionic(si[0], si[1], 'OH', -1)], 2
    if 'CO2' in rs:
        ox = rs[0] if rs[1] == 'CO2' else rs[1]
        si = split_ion(ox)
        if si and si[3] == 'O' and is_metal(si[0]):
            return rs + [make_ionic(si[0], si[1], 'CO3', -2)], 2
    raise ValueError('cannot predict')


def predict_decomp(rs):
    if len(rs) != 1:
        raise ValueError('need 1 reactant')
    f = rs[0]
    if f == 'H2CO3':
        return rs + ['H2O', 'CO2'], 1
    si = split_ion(f)
    if si:
        cat = si[0]
        cc = si[1]
        an = si[3]
        if is_metal(cat):
            if an == 'CO3':
                return rs + [make_ionic(cat, cc, 'O', -2), 'CO2'], 1
            if an == 'OH':
                return rs + [make_ionic(cat, cc, 'O', -2), 'H2O'], 1
            if an == 'ClO3':
                return rs + [make_ionic(cat, cc, 'Cl', -1), 'O2'], 1
            if an == 'NO3':
                return rs + [make_ionic(cat, cc, 'NO2', -1), 'O2'], 1
    p = parse_formula(f)
    if len(p) == 2:
        out = []
        for e in p:
            out.append(elem_form(e))
        return rs + out, 1
    raise ValueError('cannot predict')


def predict_single(rs):
    if len(rs) != 2:
        raise ValueError('need 2 reactants')
    el = None
    comp = None
    for x in rs:
        if as_element(x) and el is None:
            el = x
        else:
            comp = x
    if el is None or comp is None:
        raise ValueError('need element+compound')
    e = as_element(el)
    si = split_ion(comp)
    if si is None:
        raise ValueError('cannot read ' + comp)
    cat = si[0]
    cc = si[1]
    an = si[3]
    ac = si[4]
    if is_metal(e):
        if comp == 'H2O':
            if activity_rank(e) >= 0 and activity_rank(e) < activity_rank('H'):
                return [el, comp, make_ionic(e, charge_of_cat(e), 'OH', -1),
                        'H2'], 2
            raise ValueError('no reaction')
        if cat == 'H':
            if activity_rank(e) >= 0 and activity_rank(e) < activity_rank('H'):
                return [el, comp, make_ionic(e, charge_of_cat(e), an, ac),
                        'H2'], 2
            raise ValueError('no reaction')
        if is_metal(cat):
            ra = activity_rank(e)
            rb = activity_rank(cat)
            if ra >= 0 and rb >= 0 and ra < rb:
                return [el, comp, make_ionic(e, charge_of_cat(e), an, ac),
                        elem_form(cat)], 2
            raise ValueError('no reaction')
    if intab(HAL, e) and intab(HAL, an):
        if HAL.find(' ' + e + ' ') < HAL.find(' ' + an + ' '):
            return [el, comp, make_ionic(cat, cc, e, charge_of_an(e)),
                    elem_form(an)], 2
        raise ValueError('no reaction')
    raise ValueError('cannot predict')


def predict_double(rs):
    if len(rs) != 2:
        raise ValueError('need 2 reactants')
    s1 = split_ion(rs[0])
    s2 = split_ion(rs[1])
    if s1 is None or s2 is None:
        raise ValueError('cannot read compounds')
    p1 = make_ionic(s1[0], s1[1], s2[3], s2[4])
    p2 = make_ionic(s2[0], s2[1], s1[3], s1[4])
    if p1 == 'HOH':
        p1 = 'H2O'
    if p2 == 'HOH':
        p2 = 'H2O'
    return rs + [p1, p2], 2


def predict_combustion(rs):
    fuel = None
    for x in rs:
        if x != 'O2':
            fuel = x
    if fuel is None:
        raise ValueError('need a fuel')
    p = parse_formula(fuel)
    if 'C' not in p or 'H' not in p:
        raise ValueError('need C+H fuel')
    for e in p:
        if e not in ('C', 'H', 'O', 'S', 'N'):
            raise ValueError('cannot burn ' + e)
    prods = ['CO2', 'H2O']
    if 'S' in p:
        prods.append('SO2')
    if 'N' in p:
        prods.append('NO2')
    return [fuel, 'O2'] + prods, 2


def predict_acidbase(rs):
    if len(rs) != 2:
        raise ValueError('need acid+base')
    acid = None
    base = None
    for x in rs:
        if is_acid(x) and acid is None:
            acid = x
        elif has_oh(x):
            base = x
    if acid is None or base is None:
        raise ValueError('need acid+base')
    sa = split_ion(acid)
    sb = split_ion(base)
    salt = make_ionic(sb[0], sb[1], sa[3], sa[4])
    return [acid, base, salt, 'H2O'], 2


PREDICTORS = [predict_synthesis, predict_decomp, predict_single,
              predict_double, predict_combustion, predict_acidbase]
PNAMES = ['Synthesis', 'Decomp', 'SingleRep', 'DoubleRep',
          'Combustion', 'Acid+Base']


# try the most specific reaction types first; decomposition is the
# greediest (any 2-element compound splits) so it goes last
AUTO_ORDER = (4, 5, 2, 3, 0, 1)


def auto_predict(rs):
    for i in AUTO_ORDER:
        try:
            comps, nl = PREDICTORS[i](rs)
            coeffs = balance(comps, nl)
            if check_balanced(comps, coeffs, nl):
                return comps, nl, PNAMES[i]
        except Exception:
            pass
    raise ValueError('cannot predict')


# ---------------- display ----------------

def eq_string(compounds, coeffs, nl):
    parts = []
    for i in range(len(compounds)):
        pre = '' if coeffs[i] == 1 else str(coeffs[i])
        parts.append(pre + compounds[i])
    return ' + '.join(parts[:nl]) + ' -> ' + ' + '.join(parts[nl:])


def wrap_lines(text, width):
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        if cur == '':
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur = cur + ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur != '':
        lines.append(cur)
    out = []
    for ln in lines:
        while len(ln) > width:
            out.append(ln[:width])
            ln = ln[width:]
        out.append(ln)
    return out


def show_result(comps, coeffs, nl, label):
    if label:
        print('[' + label + ']')
    lines = wrap_lines(eq_string(comps, coeffs, nl), W)
    shown = 0
    for ln in lines:
        print(ln)
        shown += 1
        if shown % 6 == 0 and shown < len(lines):
            input('EXE=more')


def split_side(side):
    out = []
    for p in side.split('+'):
        p = p.strip()
        if p != '':
            out.append(p)
    return out


# pairs that are real elements but far more often mean two elements
# in school chemistry (CO not Co, NO not No, NH not Nh, ...)
SPLIT2 = ('co', 'no', 'cn', 'hf', 'po', 'nh')


def fix_case(s):
    out = ''
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isalpha():
            pair = ''
            if i + 1 < n and s[i + 1].isalpha():
                pair = (c + s[i + 1]).lower()
            if pair != '' and pair not in SPLIT2:
                sym2 = pair[0].upper() + pair[1]
                if (' ' + sym2 + ' ') in _SCH2:
                    out += sym2
                    i += 2
                    continue
            sym1 = c.upper()
            if is_element(sym1):
                out += sym1
                i += 1
                continue
            if pair != '':
                sym2 = pair[0].upper() + pair[1]
                if is_element(sym2):
                    out += sym2
                    i += 2
                    continue
            raise ValueError('no element ' + c)
        out += c
        i += 1
    return out


# two-letter symbols worth guessing from lowercase input; the rest of
# the 118 are still accepted, just typed with capitals (nobody means
# nobelium when they type "no")
_SCH2 = (" He Li Be Ne Na Mg Al Si Cl Ar Ca Ti Cr Mn Fe Co Ni Cu Zn Ga Ge As "
         "Se Br Kr Rb Sr Ag Cd Sn Sb Te Xe Cs Ba Pt Au Hg Pb Bi ")
# and the one-letter symbols worth guessing (U, W, Y, V are real but
# nobody typing "cu" means carbon + uranium)
_SCH1 = " H B C N O F P S K I "


def case_variants(s, cap=4):
    """Ways to read a lowercase formula, e.g. co2 -> Co2 / CO2."""
    states = [(0, '')]
    done = []
    guard = 0
    while states and guard < 300:
        guard += 1
        i, acc = states.pop(0)
        if i >= len(s):
            if acc not in done:
                done.append(acc)
                if len(done) >= cap:
                    break
            continue
        c = s[i]
        if not c.isalpha():
            states.append((i + 1, acc + c))
            continue
        nxt = []
        if i + 1 < len(s) and s[i + 1].isalpha():
            p = (c + s[i + 1]).lower()
            sym2 = p[0].upper() + p[1]
            if (' ' + sym2 + ' ') in _SCH2:
                nxt.append((i + 2, acc + sym2))
        one = c.upper()
        if (' ' + one + ' ') in _SCH1:
            nxt.append((i + 1, acc + one))
        for st in nxt:
            states.append(st)
    return done


def has_upper(s):
    for ch in s:
        if ch.isupper():
            return True
    return False


def run_balance(text):
    if '->' in text:
        left, right = text.split('->', 1)
    elif '=' in text:
        left, right = text.split('=', 1)
    else:
        return None
    lefts = split_side(left)
    rights = split_side(right)
    comps = lefts + rights
    coeffs = balance(comps, len(lefts))
    if not check_balanced(comps, coeffs, len(lefts)):
        raise ValueError('cannot balance')
    return comps, coeffs, len(lefts)


def solve_text(attempt, n):
    if ('->' in attempt) or ('=' in attempt):
        r = run_balance(attempt)
        if r is None:
            raise ValueError('bad input')
        return r[0], r[1], r[2], 'BALANCED'
    rs = split_side(attempt)
    if n == 7:
        comps, nl, lab = auto_predict(rs)
    else:
        lab = PNAMES[n - 1]
        try:
            comps, nl = PREDICTORS[n - 1](rs)
        except Exception:
            comps, nl, lab = auto_predict(rs)
    coeffs = balance(comps, nl)
    if not check_balanced(comps, coeffs, nl):
        raise ValueError('cannot balance')
    return comps, coeffs, nl, lab


def ask_charges(rs):
    """Bare Fe could be Fe2+ or Fe3+; only the user knows which."""
    done = []
    for item in rs:
        try:
            f = fix_case(item)
        except Exception:
            f = item
        try:
            e = as_element(f)
        except Exception:
            e = None
        ov = sval(MUL, e)
        if e is None or ov is None or e in done:
            continue
        done.append(e)
        opts = [int(x) for x in ov.split(',')]
        print(e + ' charge?')
        for i in range(len(opts)):
            print(str(i + 1) + ' ' + e + str(opts[i]) + '+')
        try:
            a = input('Pick:').strip()
        except (KeyboardInterrupt, EOFError):
            return False
        k = 0
        if a.isdigit() and 1 <= int(a) <= len(opts):
            k = int(a) - 1
        PICKED[e] = opts[k]
    return True


# what each menu option actually needs, so the prompts can say so and
# stop on their own instead of waiting for a blank EXE
NEEDS = {1: ['C1:', 'C2:'], 2: ['Compound:'], 3: ['Element:', 'Compound:'],
         4: ['C1:', 'C2:'], 5: ['Fuel:'], 6: ['Acid:', 'Base:']}


def read_fixed(prompts):
    items = []
    for p in prompts:
        try:
            s = input(p).strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if s == '':
            return items
        for q in split_side(s):
            items.append(q)
    return items


def read_list(tag, maxn=8):
    """Read formulas one at a time; blank entry ends the list."""
    items = []
    for i in range(maxn):
        try:
            s = input(tag + str(i + 1) + ':').strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if s == '':
            break
        for p in split_side(s):
            items.append(p)
    return items


# ---------------- menu ----------------

def menu():
    print('1 Synthesis')
    print('2 Decomposition')
    print('3 Single Replace')
    print('4 Double Replace')
    print('5 Combustion')
    print('6 Acid + Base')
    print('7 Auto / Balance')


while True:
    menu()
    try:
        pick = input('Pick 1-7:').strip()
    except (KeyboardInterrupt, EOFError):
        break
    if pick == '':
        continue
    if pick not in ('1', '2', '3', '4', '5', '6', '7'):
        print('1 to 7 only')
        continue
    n = int(pick)
    PICKED.clear()
    try:
        if n == 7:
            print('1 by 1. EXE=done')
            rs = read_list('C')
        else:
            rs = read_fixed(NEEDS[n])
        if rs is None:
            break
        if not rs:
            continue
        ps = []
        whole = ' + '.join(rs)
        if ('->' in whole) or ('=' in whole):
            text = whole
        else:
            if n == 7:
                print('Products?')
                print('none=auto')
                ps = read_list('P')
                if ps is None:
                    break
            if ps:
                text = ' + '.join(rs) + ' -> ' + ' + '.join(ps)
            else:
                # products are being predicted, so a bare multivalent
                # metal's charge decides the answer: let the user say
                if not ask_charges(rs):
                    break
                text = ' + '.join(rs)
    except (KeyboardInterrupt, EOFError):
        break
    if text == '':
        continue
    tries = [text]
    try:
        f = fix_case(text)
        if f not in tries:
            tries.append(f)
    except Exception:
        pass
    try:
        for v in case_variants(text):
            if v not in tries:
                tries.append(v)
    except Exception:
        pass
    good = []
    seen = []
    err = 'bad input'
    # as typed, then the standard school reading: if either works,
    # take it rather than bothering the user with alternatives
    for pref in tries[:2]:
        try:
            res0 = solve_text(pref, n)
            good.append((pref, res0))
            tries = []
            break
        except Exception as e:
            m = str(e)
            if m != '':
                err = m
    for attempt in tries:
        try:
            res = solve_text(attempt, n)
        except ZeroDivisionError:
            err = 'math'
            continue
        except Exception as e:
            m = str(e)
            if m != '':
                err = m
            continue
        key = eq_string(res[0], res[1], res[2])
        if key not in seen:
            seen.append(key)
            good.append((attempt, res))
        if len(good) >= 3:
            break
    if not good:
        if err == 'cannot predict' and not ps:
            err = 'type products in' if n == 7 else 'try opt 7'
        for ln in wrap_lines('Err: ' + err, W):
            print(ln)
    else:
        pickn = 0
        if len(good) > 1:
            print('Which one?')
            for gi in range(len(good)):
                print(str(gi + 1) + ' ' + good[gi][0][:19])
            try:
                ans = input('Pick:').strip()
            except (KeyboardInterrupt, EOFError):
                break
            if ans.isdigit() and 1 <= int(ans) <= len(good):
                pickn = int(ans) - 1
        res = good[pickn][1]
        show_result(res[0], res[1], res[2], res[3])
    try:
        input('EXE=menu')
    except (KeyboardInterrupt, EOFError):
        break
