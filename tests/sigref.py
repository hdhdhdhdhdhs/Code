"""An independent sig-fig engine for checking the calculator.

Different on purpose: exact Fractions instead of floats, its own parser,
and the rules applied straight from their statement.
  x and /  -> the answer keeps the FEWEST significant figures
  + and -  -> the answer keeps the FEWEST decimal places
"""
from fractions import Fraction


def mag_of(a):
    """Largest k with 10**k <= a. Exact, no logs."""
    k = 0
    if a >= 1:
        while a >= 10:
            a /= 10
            k += 1
    else:
        while a < 1:
            a *= 10
            k -= 1
    return k


def rnd(v, sig):
    """Round to sig figures, half away from zero. Returns (value, mag)."""
    if v == 0:
        return Fraction(0), 0
    neg = v < 0
    a = -v if neg else v
    d = sig - mag_of(a) - 1
    scaled = a * Fraction(10) ** d
    r = (scaled * 2 + 1) // 2           # floor(x + 1/2)
    out = Fraction(r) * Fraction(10) ** (-d)
    return (-out if neg else out), (mag_of(out) if out else 0)


def split_e(t):
    t = t.lstrip('+-').lower()
    if 'e' in t:
        m, e = t.split('e', 1)
        return m, int(e)
    return t, 0


def lit_sig(t):
    m, e = split_e(t)
    if '.' in m:
        d = m.replace('.', '').lstrip('0')
        return len(d) if d else 1
    d = m.lstrip('0').rstrip('0')
    return len(d) if d else 1


def lit_dec(t):
    """Decimal places. A zero literal keeps the places it was written
    with: 0.000 is known to three places, not zero places."""
    m, e = split_e(t)
    if '.' in m:
        return len(m.split('.', 1)[1]) - e
    z = len(m) - len(m.rstrip('0'))
    return (-z if m.rstrip('0') else 0) - e


def lit_val(t):
    m, e = split_e(t)
    return Fraction(m) * Fraction(10) ** e


def rnd_dp(v, dec):
    """Round to a decimal place, half away from zero. Exact."""
    if v == 0:
        return Fraction(0)
    neg = v < 0
    a = -v if neg else v
    scaled = a * Fraction(10) ** dec
    r = (scaled * 2 + 1) // 2
    out = Fraction(r) * Fraction(10) ** (-dec)
    return -out if neg else out


def sig_from_dec(v, dec):
    """How many figures a value known to `dec` decimal places carries."""
    w = rnd_dp(v, dec)
    if w == 0:
        return 1
    n = mag_of(abs(w)) + 1 + dec
    return n if n >= 1 else 1


def dec_from_sig(v, sig):
    """Which decimal place a value known to `sig` figures reaches."""
    if v == 0:
        return sig - 1
    w, m = rnd(v, sig)
    return sig - m - 1


class P:
    """Values are carried EXACT the whole way. Only the final answer is
    rounded - the middle steps keep their digits, which is the rule."""

    def __init__(s, txt):
        s.t = txt.replace(' ', '')
        s.i = 0

    def peek(s):
        return s.t[s.i] if s.i < len(s.t) else ''

    def expr(s):
        v, sig, dec = s.term()
        while s.peek() != '' and s.peek() in '+-':
            op = s.t[s.i]
            s.i += 1
            w, sg2, dc2 = s.term()
            v = v + w if op == '+' else v - w
            dec = min(dec, dc2)
            sig = sig_from_dec(v, dec)
        return v, sig, dec

    def term(s):
        v, sig, dec = s.pw()
        while s.peek() != '' and (s.peek() in '*/xX' or s.peek() == '('
                                  or s.peek().isdigit() or s.peek() == '.'):
            op = s.t[s.i] if s.peek() in '*/' else '*'
            if s.peek() in '*/xX':
                s.i += 1
            w, sg2, dc2 = s.pw()
            if op == '/' and w == 0:
                raise ZeroDivisionError()
            v = v * w if op == '*' else v / w
            sig = min(sig, sg2)
            dec = dec_from_sig(v, sig)
        return v, sig, dec

    def pw(s):
        v, sig, dec = s.fact()
        if s.peek() == '^':
            s.i += 1
            w, sg2, dc2 = s.fact()
            if w.denominator != 1:
                raise ValueError('fractional power')
            v = v ** int(w)
            dec = dec_from_sig(v, sig)
        return v, sig, dec

    def fact(s):
        c = s.peek()
        if c == '-':
            s.i += 1
            v, sig, dec = s.fact()
            return -v, sig, dec
        if c == '+':
            s.i += 1
            return s.fact()
        if c == '(':
            s.i += 1
            v, sig, dec = s.expr()
            if s.peek() != ')':
                raise ValueError('need )')
            s.i += 1
            return v, sig, dec
        j = s.i
        while s.i < len(s.t) and (s.t[s.i].isdigit() or s.t[s.i] == '.'):
            s.i += 1
        if s.i == j:
            raise ValueError('bad char ' + c)
        if s.i < len(s.t) and s.t[s.i] in 'eE':
            k = s.i + 1
            if k < len(s.t) and s.t[k] in '+-':
                k += 1
            d = k
            while d < len(s.t) and s.t[d].isdigit():
                d += 1
            if d > k:
                s.i = d
        t = s.t[j:s.i]
        return lit_val(t), lit_sig(t), lit_dec(t)


def solve(txt):
    p = P(txt)
    v, sig, dec = p.expr()
    if p.i != len(p.t):
        raise ValueError('extra')
    # round where the working reaches, not to a figure count
    w = rnd_dp(v, dec)
    return w, sig_from_dec(v, dec)


def read(txt):
    """Turn the calculator's printed answer back into an exact number."""
    t = txt.strip()
    if 'e' in t:
        m, e = t.split('e')
        return Fraction(m.rstrip('.') or '0') * Fraction(10) ** int(e)
    return Fraction(t.rstrip('.') or '0')
