# shared independent verifier, imported by both test suites
import chemlib as C

def _vals(t):
    out = []
    for p in t.split(' '):
        if ':' in p:
            out.append(p.split(':')[1])
    return out

SPECIAL = _vals(C.CV) + _vals(C.OX) + ['H2O', 'CO2', 'SO2', 'NO2', 'NO', 'O2',
                                        'H2', 'N2', 'P4', 'S8']

def g2(a, b):
    a = abs(a); b = abs(b)
    while b:
        a, b = b, a % b
    return a

def atoms_balance(comps, co, nl):
    L = {}; R = {}
    for i in range(len(comps)):
        f = C.pf(comps[i])
        t = L if i < nl else R
        for e in f:
            t[e] = t.get(e, 0) + f[e] * co[i]
    return L == R

def coeffs_ok(co):
    for x in co:
        if x <= 0:
            return False
    g = 0
    for x in co:
        g = g2(g, x)
    return g == 1

def charge_ok(f):
    if f in SPECIAL:
        return True
    s = C.si(f)
    if s is None:
        return True
    return s[2] * s[1] + s[5] * s[4] == 0

def products_charge_ok(comps, nl):
    for f in comps[nl:]:
        if not charge_ok(f):
            return False
    return True

def formulas_parse(comps):
    for f in comps:
        try:
            C.pf(f)
        except Exception:
            return False
    return True

def width_ok(comps, co, nl):
    for L in C.wrap(C.eqs(comps, co, nl)):
        if len(L) > 21:
            return False
    return True

def why_bad(comps, co, nl):
    w = []
    if not formulas_parse(comps):
        w.append('unparseable')
    if not atoms_balance(comps, co, nl):
        w.append('atoms not conserved')
    if not coeffs_ok(co):
        w.append('bad coefficients')
    if not products_charge_ok(comps, nl):
        w.append('product not neutral')
    if not width_ok(comps, co, nl):
        w.append('over 21 cols')
    return w
