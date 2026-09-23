"""Fuzz the simplifier. Independent check: the expression the user typed
and the answer the program printed are both evaluated numerically with
random variable values, and must agree."""
import random, re, sys
sys.path.insert(0, '.')
import explib as E

def sqrt(x):
    return x ** 0.5

def rt(q, x):
    return -((-x) ** (1.0 / q)) if x < 0 else x ** (1.0 / q)

TOK = re.compile(r'sqrt|rt|[a-z]|\d+\.?\d*|[()+\-*/,^]')
FN = ('sqrt', 'rt')

def topy(s):
    o = []
    prev = ''
    for t in TOK.findall(s):
        if prev and prev not in '(^*/+-,' and prev not in FN:
            if t in FN or t == '(' or t[0].isdigit() or t.isalpha():
                o.append('*')
        o.append('**' if t == '^' else t)
        prev = t
    return ''.join(o)

def ev(s, env):
    return eval(topy(s), {'__builtins__': {}, 'sqrt': sqrt, 'rt': rt}, env)

VARS = 'xymn'

def gen(rng, depth=0):
    parts = []
    for _ in range(rng.randint(1, 3)):
        b = str(rng.randint(2, 9)) if rng.random() < 0.45 else rng.choice(VARS)
        r = rng.random()
        if r < 0.40:
            e = rng.randint(-4, 4)
            f = b + '^' + str(e) if e != 1 else b
        elif r < 0.62:
            q = rng.choice([2, 3, 4, 5])
            p = rng.randint(-5, 5) or 1
            f = b + '^(' + str(p) + '/' + str(q) + ')'
        elif r < 0.75:
            q = rng.choice([2, 3, 4])
            f = 'sqrt(' + b + ')' if q == 2 else 'rt(' + str(q) + ',' + b + ')'
        else:
            f = b
        parts.append(f)
    s = '(' + ')('.join(parts) + ')'
    if depth == 0 and rng.random() < 0.4:
        s = '(' + s + ')/(' + gen(rng, 1) + ')'
    if depth == 0 and rng.random() < 0.35:
        e = rng.choice([-3, -2, -1, 2, 3, '(1/2)', '(1/3)', '(-3/2)', '(2/3)',
                        '(3/4)', '(-1/2)', '0.5'])
        s = '(' + s + ')^' + str(e)
    return s

rng = random.Random(20260916)
N = 25000
tot = ok = skip = 0
fails = []
for i in range(N):
    s = gen(rng)
    env = {}
    for v in VARS:
        env[v] = rng.uniform(1.2, 3.0)
    try:
        a = ev(s, dict(env))
    except Exception:
        skip += 1
        continue
    if isinstance(a, complex) or abs(a) > 1e13 or abs(a) < 1e-13:
        skip += 1
        continue
    tot += 1
    try:
        out = E.do1([s])
    except Exception as e:
        fails.append((s, 'ERR ' + str(e), a))
        continue
    for o in out:
        o = o[2:] if o.startswith('= ') else o
        try:
            b = ev(o, dict(env))
        except Exception as e:
            fails.append((s, o + '  <unreadable: ' + str(e) + '>', a))
            break
        if abs(a - b) > 1e-7 * max(1.0, abs(a)):
            fails.append((s, o, (a, b)))
            break
    else:
        ok += 1

print('SIMPLIFY FUZZ: checked %d, agreed %d, skipped %d, MISMATCH %d'
      % (tot, ok, skip, len(fails)))
for f in fails[:10]:
    print('   ', f[0], '=>', f[1], f[2])
