# rad.py against itself: answers that must agree with each other.
#
#  idem   a simplified answer, typed back in, must come out the same
#  zero   (question)-(its answer) must simplify to exactly 0
#  typing the same question typed differently must give the same
#         screen: ** for ^, * where it is implied, spaces, capitals,
#         math.sqrt, ^(1/2) and ^0.5 for sqrt, letters renamed, sums
#         reordered (numbers only), sides of an equation swapped, an
#         equation multiplied through by a number or moved to one side
#  back   each fraction answer of an equation put back in, through the
#         simplifier: exactly 0 when it works, not 0 when it fails
#
#   python3 consist.py [count] [seed]     (run from tests/, needs no sympy)
import sys, random, re

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sys.path.insert(0, '..')

src = open('../rad.py').read()
G = {}
exec(src[:src.index("print('Root equations")], G)
solve, wrap, W = G['solve'], G['wrap'], G['W']


def run(q):
    try:
        return solve(q)
    except Exception as e:
        return ['Err: ' + (str(e) or 'bad input')]


def gens():
    # the generators from the two sympy checkers, without sympy
    sys.argv = ['x', '../rad.py', '1', str(SEED)]
    a = {}
    exec(open('rfuzz.py').read().split('# ---------------------------------------------------------- reference')[0], a)
    sys.argv = ['x', '../radsimp.py', '1', str(SEED)]
    b = {}
    exec(open('sfuzz.py').read().split('# ---------------------------------------------------------- checking')[0], b)
    return a['gen'], b['gen']


egen, sgen = gens()


def ans(out):
    for l in out:
        if l.startswith('Ans: '):
            return l[5:]
    return None


# ---- ways of typing the same thing
def balanced(s, i):
    # index after the bracket group that opens at s[i]
    d = 0
    while True:
        d += {'(': 1, ')': -1}.get(s[i], 0)
        i += 1
        if d == 0:
            return i


def as_power(s, r):
    # sqrt(E) -> (E)^(1/2) or (E)^0.5, from the inside out
    while 'sqrt(' in s:
        i = s.rindex('sqrt(')
        j = balanced(s, i + 4)
        s = s[:i] + '(' + s[i + 4:j] + r.choice(['^(1/2)', '^0.5', '**0.5']) + ')' + s[j:]
    return s


def stars(s):
    # put in every * the calculator lets you leave out
    s = s.replace('sqrt(', 'S(')
    s = re.sub(r'(?<=[\da-zS)])(?=[a-zS(])', '*', s)
    s = re.sub(r'(?<=[a-z)])(?=\d)', '*', s)  # never made: x2 means x^2
    return s.replace('S*(', 'S(').replace('S(', 'sqrt(')


def spaces(s, r):
    return ''.join(c + (' ' if r.random() < 0.3 else '') for c in s)


def rename(s, r):
    # each letter to another, keeping their order of first appearance
    used = []
    for c in s.replace('sqrt', ''):
        if c.isalpha() and c not in used:
            used.append(c)
    pool = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in 'sqrt']
    new = r.sample(pool, len(used))
    m = dict(zip(used, new))
    s = s.replace('sqrt(', '\0')
    s = ''.join(m.get(c, c) for c in s)
    return s.replace('\0', 'sqrt(')


def terms(s):
    out = []
    d = 0
    cur = ''
    for c in s:
        if c in '+-' and d == 0 and cur and cur[-1] not in '*/^(':
            out.append(cur)
            cur = ''
        d += {'(': 1, ')': -1}.get(c, 0)
        cur += c
    out.append(cur)
    return out


def shuffle_sum(s, r):
    t = terms(s)
    r.shuffle(t)
    o = ''
    for x in t:
        if o and x[0] not in '+-':
            o += '+'
        o += x
    return o


bad = {}


def flag(kind, *a):
    bad.setdefault(kind, []).append(a)


r = random.Random(SEED)
for n in range(N):
    # ---------------- simplifying
    name, q = sgen(n)
    out = run(q)
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                flag('wide', q, w)
    a = ans(out)
    if a is not None and '|' not in a:  # |x-3| can not be typed back
        a2 = ans(run(a))
        if a2 != a:
            flag('idem', q, a, a2)
        z = ans(run('(' + q + ')-(' + a + ')'))
        if z != '0':
            flag('zero', q, a, z)
    letters = re.sub('sqrt', '', q)
    for kind, v in (('power', as_power(q, r)), ('stars', stars(q)), ('spaces', spaces(q, r)),
                    ('caps', q.upper()), ('math', q.replace('sqrt(', 'math.sqrt(')),
                    ('stars**', stars(q).replace('^', '**'))):
        o2 = run(v)
        if o2 != out:
            flag('typing ' + kind, q, v, out, o2)
    if not re.search('[a-z]', letters):
        v = shuffle_sum(q, r)
        o2 = run(v)
        if ans(o2) != ans(out):
            flag('typing reorder', q, v, ans(out), ans(o2))
    else:
        v = rename(q, r)
        mapping = None
        o2 = run(v)
        if (ans(o2) is None) != (ans(out) is None):
            flag('typing rename', q, v, out, o2)

    # ---------------- equations
    name, e = egen(n)
    out = run(e)
    a = ans(out)
    l, rr = e.split('=')
    for kind, v in (('power', as_power(e, r)), ('spaces', spaces(e, r)), ('caps', e.upper()),
                    ('math', e.replace('sqrt(', 'math.sqrt(')), ('**', e.replace('^', '**')),
                    ('stars', stars(l) + '=' + stars(rr))):
        o2 = run(v)
        if o2 != out:
            flag('eq typing ' + kind, e, v, out, o2)
    for kind, v in (('swap', rr + '=' + l), ('times 3', '3(' + l + ')=3(' + rr + ')'),
                    ('one side', '(' + l + ')-(' + rr + ')=0'), ('halves', '(' + l + ')/2=(' + rr + ')/2')):
        o2 = run(v)
        if ans(o2) != ans(out):
            flag('eq ' + kind, e, v, ans(out), ans(o2))
    v = rename(e, r)
    o2 = run(v)
    if ans(o2) is None and ans(out) is not None:
        flag('eq rename', e, v, out, o2)
    # put fraction answers back in, through the simplifier
    fl = [x for x in out if x.startswith('Fails: ')]
    works = [t for t in (a or '').split(', ') if re.fullmatch(r'x=-?\d+(/\d+)?', t)]
    fails = [t for t in (fl[0][7:] if fl else '').split(', ') if re.fullmatch(r'x=-?\d+(/\d+)?', t)]
    if 'sqrt(' in e and not re.search(r'sqrt\([^()]*sqrt', e):
        for t, want in [(t, True) for t in works] + [(t, False) for t in fails]:
            val = '(' + t[2:] + ')'
            d = '(' + l.replace('x', val) + ')-(' + rr.replace('x', val) + ')'
            got = run(d)
            z = ans(got)
            if want and z != '0':
                flag('back works', e, t, d, got)
            if not want and z == '0':
                flag('back fails', e, t, d, got)

for k in sorted(bad):
    print('%-20s %d' % (k, len(bad[k])))
    for x in bad[k][:4]:
        print('    ', str(x)[:600])
print(N, 'simplify questions and', N, 'equations;', sum(len(v) for v in bad.values()), 'disagreements')
