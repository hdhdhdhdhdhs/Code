import math

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

def count_decimals(raw):
    mant, exp = _mantissa_and_exp(raw)
    if '.' in mant:
        dec = len(mant.split('.')[1])
    else:
        dec = 0
    return dec - exp

def order_of_magnitude(value):
    value = abs(value)
    if value == 0:
        return 0
    m = 0
    if value >= 1:
        while value >= 10:
            value /= 10.0
            m += 1
    else:
        while value < 1:
            value *= 10.0
            m -= 1
    return m

def round_to_sig(value, sig):
    if value == 0:
        return 0.0
    if sig < 1:
        sig = 1
    sign = -1.0 if value < 0 else 1.0
    value = abs(value)
    mag = order_of_magnitude(value)
    dec = sig - mag - 1
    factor = 10.0 ** dec
    shifted = value * factor
    rounded = math.floor(shifted + 0.5 + 1e-9)
    return sign * (rounded / factor)

def decimals_after_rounding(rounded_value, sig):
    if rounded_value == 0:
        return sig - 1 if sig > 1 else 0
    mag = order_of_magnitude(abs(rounded_value))
    return sig - mag - 1

def sigfigs_after_rounding(rounded_value, dec):
    if rounded_value == 0:
        return 1
    mag = order_of_magnitude(abs(rounded_value))
    sig = mag + dec + 1
    return sig if sig >= 1 else 1

def round_to_dec(value, dec):
    factor = 10.0 ** dec
    shifted = value * factor
    if shifted >= 0:
        rounded = math.floor(shifted + 0.5 + 1e-9)
    else:
        rounded = -math.floor(-shifted + 0.5 + 1e-9)
    return rounded / factor

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
            return (-val, sig, dec)
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
            return (float(raw), count_sigfigs(raw), count_decimals(raw))
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
    exact = lval + rval if op == '+' else lval - rval
    new_dec = ldec if ldec < rdec else rdec
    rounded = round_to_dec(exact, new_dec)
    new_sig = sigfigs_after_rounding(rounded, new_dec)
    return (exact, new_sig, new_dec)

def combine_mul(l, r, op):
    lval, lsig, ldec = l
    rval, rsig, rdec = r
    if op == '*':
        exact = lval * rval
    else:
        if rval == 0:
            raise ZeroDivisionError('div by 0')
        exact = lval / rval
    new_sig = lsig if lsig < rsig else rsig
    rounded = round_to_sig(exact, new_sig)
    new_dec = decimals_after_rounding(rounded, new_sig)
    return (exact, new_sig, new_dec)

def combine_pow(base, exp_node):
    bval, bsig, bdec = base
    eval_, esig, edec = exp_node
    exact = bval ** eval_
    new_sig = bsig
    rounded = round_to_sig(exact, new_sig)
    new_dec = decimals_after_rounding(rounded, new_sig)
    return (exact, new_sig, new_dec)

def format_result(value, sig):
    if value == 0:
        if sig <= 1:
            return '0'
        return '0.' + '0' * (sig - 1)
    sign = '-' if value < 0 else ''
    v = abs(value)
    mag = order_of_magnitude(v)
    d = sig - mag - 1
    factor = 10.0 ** d
    shifted = v * factor
    rounded_int = int(math.floor(shifted + 0.5 + 1e-9))
    digit_str = str(rounded_int)
    if len(digit_str) > sig:
        mag += (len(digit_str) - sig)
    elif len(digit_str) < sig:
        digit_str = '0' * (sig - len(digit_str)) + digit_str
    if mag < 0:
        body = '0.' + '0' * (-mag - 1) + digit_str
    elif mag + 1 >= len(digit_str):
        body = digit_str + '0' * (mag + 1 - len(digit_str))
    else:
        cut = mag + 1
        body = digit_str[:cut] + '.' + digit_str[cut:]
    return sign + body

def calculate(equation):
    tokens = tokenize(equation)
    parser = Parser(tokens)
    value, sig, dec = parser.parse()
    return format_result(value, sig), sig

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
