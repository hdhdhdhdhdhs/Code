def _mantissa_and_exp(raw):
    epos = -1
    for i in range(len(raw)):
        if raw[i] == 'e' or raw[i] == 'E':
            epos = i
            break
    if epos == -1:
        return raw, 0
    return raw[:epos], int(raw[epos + 1:])

def count_sigfigs(raw):
    mant, exp = _mantissa_and_exp(raw)
    if mant[0:1] == '-' or mant[0:1] == '+':
        mant = mant[1:]
    if '.' in mant:
        parts = mant.split('.')
        combined = parts[0] + parts[1]
        stripped = combined.lstrip('0')
        if stripped == '':
            return 1
        return len(stripped)
    else:
        digits = mant.lstrip('0')
        if digits == '':
            return 1
        digits = digits.rstrip('0')
        if digits == '':
            return 1
        return len(digits)

def _leading_digit_pos(mant):
    if '.' in mant:
        ipart, fpart = mant.split('.', 1)
    else:
        ipart, fpart = mant, ''
    core_i = ipart.lstrip('0')
    if core_i != '':
        return len(core_i) - 1
    core_f = fpart.lstrip('0')
    if core_f != '':
        return -(len(fpart) - len(core_f) + 1)
    return 0

def count_decimals(raw):
    mant, exp = _mantissa_and_exp(raw)
    if mant[0:1] == '-' or mant[0:1] == '+':
        mant = mant[1:]
    if mant.replace('.', '').strip('0') == '':
        # zero has no leading digit to count from, so read the places off
        # the text: 0.000 is known to three places, not to none
        after = len(mant.split('.', 1)[1]) if '.' in mant else 0
        return after - exp
    sig = count_sigfigs(raw)
    mag = _leading_digit_pos(mant) + exp
    return sig - mag - 1

BIG = 10 ** 400


def rat(n, d=1):
    """A value is an exact fraction (numerator, denominator), never a
    float. Floats were the cause of two faults at once: a value sitting
    on a rounding boundary could fall either side of it, and a small
    term vanished entirely beside a huge one."""
    if d == 0:
        raise ZeroDivisionError('div by 0')
    # stop before reducing something enormous: tidying 10**100000 takes
    # twelve seconds here, which would be minutes on the calculator
    if n > BIG or n < -BIG or d > BIG:
        raise ValueError('number too big')
    if d < 0:
        n = -n
        d = -d
    a = n if n >= 0 else -n
    b = d
    while b:
        a, b = b, a % b
    g = a or 1
    return (n // g, d // g)


def radd(x, y):
    return rat(x[0] * y[1] + y[0] * x[1], x[1] * y[1])


def rsub(x, y):
    return rat(x[0] * y[1] - y[0] * x[1], x[1] * y[1])


def rmul(x, y):
    return rat(x[0] * y[0], x[1] * y[1])


def rdiv(x, y):
    if y[0] == 0:
        raise ZeroDivisionError('div by 0')
    return rat(x[0] * y[1], x[1] * y[0])


def rpow(x, k):
    if k < 0:
        if x[0] == 0:
            raise ZeroDivisionError('div by 0')
        return rat(x[1] ** (-k), x[0] ** (-k))
    return rat(x[0] ** k, x[1] ** k)


def to_rat(raw):
    """Read a written number exactly: 0.1 is one tenth, not 0.1000...055."""
    mant, exp = _mantissa_and_exp(raw)
    sign = 1
    if mant[0:1] == '-':
        sign = -1
        mant = mant[1:]
    elif mant[0:1] == '+':
        mant = mant[1:]
    if '.' in mant:
        i = mant.index('.')
        digits = mant[:i] + mant[i + 1:]
        exp -= len(mant) - i - 1
    else:
        digits = mant
    if exp > 400 or exp < -400 or len(digits) > 400:
        raise ValueError('number too big')
    n = sign * (int(digits) if digits else 0)
    if exp >= 0:
        return rat(n * 10 ** exp, 1)
    return rat(n, 10 ** (-exp))


def ge_pow10(x, k):
    """Is |x| at least 10**k?"""
    n = x[0] if x[0] >= 0 else -x[0]
    if k >= 0:
        return n >= x[1] * 10 ** k
    return n * 10 ** (-k) >= x[1]


def order_of_magnitude(x):
    """Which power of ten the number sits on. Exact, so there is no
    value just under a power of ten that gets called the one above."""
    if x[0] == 0:
        return 0
    n = x[0] if x[0] > 0 else -x[0]
    k = len(str(n)) - len(str(x[1]))
    while not ge_pow10(x, k):
        k -= 1
    while ge_pow10(x, k + 1):
        k += 1
    return k


def round_digits(x, dec):
    """|x| times 10**dec, rounded half away from zero. Exact - no nudge
    is needed, because there is no float error to lean against."""
    n = x[0] if x[0] >= 0 else -x[0]
    if dec >= 0:
        num = n * 10 ** dec
        den = x[1]
    else:
        num = n
        den = x[1] * 10 ** (-dec)
    return (2 * num + den) // (2 * den)


def round_to_sig(value, sig):
    if value[0] == 0:
        return (0, 1)
    if sig < 1:
        sig = 1
    dec = sig - order_of_magnitude(value) - 1
    q = round_digits(value, dec)
    r = rat(q, 10 ** dec) if dec >= 0 else rat(q * 10 ** (-dec), 1)
    return (-r[0], r[1]) if value[0] < 0 else r


def round_to_dec(value, dec):
    q = round_digits(value, dec)
    r = rat(q, 10 ** dec) if dec >= 0 else rat(q * 10 ** (-dec), 1)
    return (-r[0], r[1]) if value[0] < 0 else r


def decimals_after_rounding(rounded_value, sig):
    if rounded_value[0] == 0:
        return sig - 1 if sig > 1 else 0
    return sig - order_of_magnitude(rounded_value) - 1


def sigfigs_after_rounding(rounded_value, dec):
    if rounded_value[0] == 0:
        return 1
    sig = order_of_magnitude(rounded_value) + dec + 1
    return sig if sig >= 1 else 1


def tokenize(s):
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == ' ' or c == '\t':
            i += 1
            continue
        if c in '+-*/()^':
            tokens.append(('op', c))
            i += 1
            continue
        if c == 'x' or c == 'X':
            tokens.append(('op', '*'))
            i += 1
            continue
        if c.isdigit() or c == '.':
            j = i
            seen_dot = False
            while j < n and (s[j].isdigit() or s[j] == '.'):
                if s[j] == '.':
                    if seen_dot:
                        break
                    seen_dot = True
                j += 1
            if j < n and (s[j] == 'e' or s[j] == 'E'):
                k = j + 1
                if k < n and (s[k] == '+' or s[k] == '-'):
                    k += 1
                if k < n and s[k].isdigit():
                    while k < n and s[k].isdigit():
                        k += 1
                    j = k
            tokens.append(('num', s[i:j]))
            i = j
            continue
        raise ValueError('bad char')
    out = []
    for idx in range(len(tokens)):
        if idx > 0:
            prev = tokens[idx - 1]
            cur = tokens[idx]
            prev_end = prev[1] == ')' or prev[0] == 'num'
            cur_start = (cur[0] == 'op' and cur[1] == '(') or cur[0] == 'num'
            if prev_end and cur_start:
                out.append(('op', '*'))
        out.append(tokens[idx])
    return out

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        t = self.peek()
        self.pos += 1
        return t

    def parse(self):
        result = self.expr()
        if self.pos != len(self.tokens):
            raise ValueError('bad equation')
        return result

    def expr(self):
        result = self.term()
        while True:
            t = self.peek()
            if t is not None and t[0] == 'op' and (t[1] == '+' or t[1] == '-'):
                self.advance()
                rhs = self.term()
                result = combine_add(result, rhs, t[1])
            else:
                break
        return result

    def term(self):
        result = self.power()
        while True:
            t = self.peek()
            if t is not None and t[0] == 'op' and (t[1] == '*' or t[1] == '/'):
                self.advance()
                rhs = self.power()
                result = combine_mul(result, rhs, t[1])
            else:
                break
        return result

    def power(self):
        base = self.unary()
        t = self.peek()
        if t is not None and t[0] == 'op' and t[1] == '^':
            self.advance()
            exp_node = self.unary()
            base = combine_pow(base, exp_node)
        return base

    def unary(self):
        t = self.peek()
        if t is not None and t[0] == 'op' and t[1] == '-':
            self.advance()
            val, sig, dec = self.unary()
            return ((-val[0], val[1]), sig, dec)
        if t is not None and t[0] == 'op' and t[1] == '+':
            self.advance()
            return self.unary()
        return self.primary()

    def primary(self):
        t = self.peek()
        if t is None:
            raise ValueError('bad equation')
        if t[0] == 'num':
            self.advance()
            raw = t[1]
            return (to_rat(raw), count_sigfigs(raw), count_decimals(raw))
        if t[0] == 'op' and t[1] == '(':
            self.advance()
            result = self.expr()
            close = self.advance()
            if close is None or close[1] != ')':
                raise ValueError('missing )')
            return result
        raise ValueError('bad equation')

def combine_add(l, r, op):
    lval, lsig, ldec = l
    rval, rsig, rdec = r
    exact = radd(lval, rval) if op == '+' else rsub(lval, rval)
    new_dec = ldec if ldec < rdec else rdec
    rounded = round_to_dec(exact, new_dec)
    new_sig = sigfigs_after_rounding(rounded, new_dec)
    return (exact, new_sig, new_dec)

def combine_mul(l, r, op):
    lval, lsig, ldec = l
    rval, rsig, rdec = r
    exact = rmul(lval, rval) if op == '*' else rdiv(lval, rval)
    new_sig = lsig if lsig < rsig else rsig
    rounded = round_to_sig(exact, new_sig)
    new_dec = decimals_after_rounding(rounded, new_sig)
    return (exact, new_sig, new_dec)

def combine_pow(base, exp_node):
    bval, bsig, bdec = base
    eval_, esig, edec = exp_node
    if eval_[1] != 1:
        # a root has no exact fraction, so work it out in float and keep
        # seventeen digits - the only place floats are still used
        base_f = bval[0] / float(bval[1])
        exp_f = eval_[0] / float(eval_[1])
        if base_f < 0:
            raise ValueError('bad power')
        exact = to_rat('%.17e' % (base_f ** exp_f))
    else:
        k = eval_[0]
        if k > 60 or k < -60:
            raise ValueError('power too big')
        exact = rpow(bval, k)
    new_sig = bsig
    rounded = round_to_sig(exact, new_sig)
    new_dec = decimals_after_rounding(rounded, new_sig)
    return (exact, new_sig, new_dec)

def format_result(value, sig, dec):
    """Round where the working actually reaches - the decimal place - and
    then write it so that reading it back gives the same count."""
    if value[0] == 0:
        return ('0' if sig <= 1 else '0.' + '0' * (sig - 1)), sig
    sign = '-' if value[0] < 0 else ''
    rounded_int = round_digits(value, dec)
    if rounded_int == 0:
        return '0', 1
    digit_str = str(rounded_int)
    sig = len(digit_str)
    mag = sig - 1 - dec
    sci = digit_str[0] + ('.' + digit_str[1:] if sig > 1 else '')
    sci = sign + sci + 'e' + str(mag)
    if mag > 8 or mag < -5:
        return sci, sig
    if mag < 0:
        body = '0.' + '0' * (-mag - 1) + digit_str
    elif mag + 1 >= len(digit_str):
        body = digit_str + '0' * (mag + 1 - len(digit_str))
    else:
        body = digit_str[:mag + 1] + '.' + digit_str[mag + 1:]
    out = sign + body
    if count_sigfigs(out) == sig:
        return out, sig
    # a whole number whose last zero counts needs a trailing point: 50.
    if '.' not in body and count_sigfigs(out + '.') == sig:
        return out + '.', sig
    # neither 200 nor 200. can say two figures, so say 2.0e2
    return sci, sig


def calculate(equation):
    tokens = tokenize(equation)
    parser = Parser(tokens)
    value, sig, dec = parser.parse()
    return format_result(value, sig, dec)

print("Sig Fig Calc")
print("type equation")
print("EXIT key=stop")

while True:
    try:
        eq = input("> ")
    except (KeyboardInterrupt, EOFError):
        break
    if eq.strip() == '':
        continue
    try:
        text, sig = calculate(eq)
        print("=" + text)
        print(str(sig) + " sig figs")
    except ZeroDivisionError:
        print("Error: /0")
    except Exception:
        print("Error: bad")
