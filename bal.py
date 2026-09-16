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


_SCH2 = (" He Li Be Ne Na Mg Al Si Cl Ar Ca Ti Cr Mn Fe Co Ni Cu Zn Ga Ge As "
         "Se Br Kr Rb Sr Ag Cd Sn Sb Te Xe Cs Ba Pt Au Hg Pb Bi ")
_SCH1 = " H B C N O F P S K I "
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




def read_list(tag, maxn=8):
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


print('BALANCER')
print('1 by 1. EXE=done')
while True:
    try:
        rs = read_list('C')
        if rs is None:
            break
        if not rs:
            continue
        print('Products:')
        ps = read_list('P')
        if ps is None:
            break
        if not ps:
            print('need products')
            continue
    except (KeyboardInterrupt, EOFError):
        break
    text = ' + '.join(rs) + ' -> ' + ' + '.join(ps)
    try:
        try:
            r = run_balance(text)
        except Exception:
            r = run_balance(fix_case(text))
        if r is None:
            raise ValueError('bad input')
        for ln in wrap_lines(eq_string(r[0], r[1], r[2]), W):
            print(ln)
    except Exception as e:
        m = str(e)
        if m == '':
            m = 'bad input'
        for ln in wrap_lines('Err: ' + m, W):
            print(ln)
