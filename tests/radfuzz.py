"""Fuzz the four radical jobs. Independent check: evaluate the printed
answer numerically and compare against what was asked for."""
import random, re, sys
sys.path.insert(0, '.')
import explib as E

def sqrt(x):
    return x ** 0.5

def rt(q, x):
    if x < 0:
        return -((-x) ** (1.0 / q))
    return x ** (1.0 / q)

TOK = re.compile(r'sqrt|rt|[a-z]|\d+\.?\d*|[()+\-*/,^]')
OPEN = ('(', 'sqrt', 'rt')

def topy(s):
    ts = TOK.findall(s)
    o = []
    prev = ''
    for t in ts:
        if prev and prev not in '(^*/+-,' and prev not in ('sqrt', 'rt') and \
           (t in OPEN or t[0].isdigit() or (t.isalpha() and t not in ('sqrt', 'rt')) or t in ('sqrt', 'rt')):
            o.append('*')
        o.append('**' if t == '^' else t)
        prev = t
    return ''.join(o)

def ev(s, env):
    g = {'__builtins__': {}, 'sqrt': sqrt, 'rt': rt}
    return eval(topy(s), g, env)

rng = random.Random(4242)
VARS = 'xy'
bad = []
n = 0

def chk(tag, got, want, env, src):
    global n
    n += 1
    try:
        v = ev(got, dict(env))
    except Exception as e:
        bad.append((tag, src, got, 'unreadable: ' + str(e)))
        return
    if abs(v - want) > 1e-7 * max(1.0, abs(want)):
        bad.append((tag, src, got, 'value %r want %r' % (v, want)))

# ---- mode 2: power -> radical ----
for _ in range(3000):
    base = []
    env = {}
    for v in VARS:
        env[v] = rng.uniform(1.2, 3.0)
    parts = []
    for _ in range(rng.randint(1, 2)):
        if rng.random() < 0.5:
            parts.append(str(rng.randint(2, 30)) + '^' + str(rng.randint(1, 3)))
        else:
            parts.append(rng.choice(VARS) + '^' + str(rng.randint(1, 6)))
    b = '*'.join(parts)
    q = rng.choice([2, 3, 4, 5])
    p = rng.randint(-5, 5) or 1
    try:
        out = E.do2([b, str(p) + '/' + str(q)])[0]
    except Exception as e:
        bad.append(('pow->rad', b + ' ^ %d/%d' % (p, q), 'ERR', str(e)))
        continue
    want = ev(b, dict(env)) ** (float(p) / q)
    chk('pow->rad', out, want, env, b + ' ^ %d/%d' % (p, q))

# ---- mode 3: radical -> power ----
for _ in range(3000):
    env = {}
    for v in VARS:
        env[v] = rng.uniform(1.2, 3.0)
    parts = []
    for _ in range(rng.randint(1, 2)):
        if rng.random() < 0.5:
            parts.append(str(rng.randint(2, 40)))
        else:
            parts.append(rng.choice(VARS) + '^' + str(rng.randint(1, 6)))
    b = '*'.join(parts)
    q = rng.choice([2, 3, 4, 5])
    p = rng.randint(1, 6)
    try:
        out = E.do3([str(q), b, str(p)])[0]
    except Exception as e:
        bad.append(('rad->pow', b, 'ERR', str(e)))
        continue
    want = ev(b, dict(env)) ** (float(p) / q)
    chk('rad->pow', out, want, env, 'rt(%d, %s)^%d' % (q, b, p))

# ---- mode 4: mixed -> entire ----
for _ in range(3000):
    q = rng.choice([2, 3, 4, 5])
    cn = rng.randint(-6, 6) or 2
    cd = rng.choice([1, 1, 1, 2, 5])
    if q % 2 == 0 and cn < 0:
        cn = -cn
    r = rng.randint(2, 60)
    c = '%d/%d' % (cn, cd) if cd != 1 else str(cn)
    try:
        out = E.do4([c, str(q), str(r)])[0]
    except Exception as e:
        bad.append(('mixed->entire', c + ' rt' + str(q) + ' ' + str(r), 'ERR', str(e)))
        continue
    want = (float(cn) / cd) * rt(q, r)
    chk('mixed->entire', out, want, {}, c + ' rt%d(%d)' % (q, r))

# ---- mode 5: entire -> mixed ----
def qfree(x, q):
    d = 2
    while d ** q <= x:
        if x % (d ** q) == 0:
            return False
        d += 1
    return True

for _ in range(3000):
    q = rng.choice([2, 3, 4, 5])
    r = rng.randint(2, 20000)
    try:
        out = E.do5([str(q), str(r)])[0]
    except Exception as e:
        bad.append(('entire->mixed', 'rt%d(%d)' % (q, r), 'ERR', str(e)))
        continue
    chk('entire->mixed', out, rt(q, r), {}, 'rt%d(%d)' % (q, r))
    m = re.search(r'\((?:\d+,)?(\d+)\)$', out)
    if m and not qfree(int(m.group(1)), q):
        bad.append(('entire->mixed', 'rt%d(%d)' % (q, r), out, 'not fully reduced'))

print('RADICAL FUZZ: checked %d, MISMATCH %d' % (n, len(bad)))
for f in bad[:12]:
    print('   ', f)

# ---- round trip: mixed -> entire -> mixed must come back ----
rt5 = 0
for _ in range(3000):
    q = rng.choice([2, 3, 4, 5])
    c = rng.randint(1, 9)
    r = rng.randint(2, 200)
    try:
        ent = E.do4([str(c), str(q), str(r)])[0]
        m = re.match(r'^(?:sqrt|rt)\((?:\d+,)?(-?\d+)\)$', ent)
        if not m:
            continue
        back = E.do5([str(q), m.group(1)])[0]
    except Exception as e:
        bad.append(('roundtrip', '%d rt%d(%d)' % (c, q, r), 'ERR', str(e)))
        continue
    rt5 += 1
    want = c * rt(q, r)
    try:
        v = ev(back, {})
    except Exception as e:
        bad.append(('roundtrip', ent, back, 'unreadable ' + str(e)))
        continue
    if abs(v - want) > 1e-7 * max(1.0, abs(want)):
        bad.append(('roundtrip', ent, back, 'value %r want %r' % (v, want)))

print('ROUND TRIPS: %d' % rt5)
print('RADICAL FUZZ TOTAL: checked %d, MISMATCH %d' % (n + rt5, len(bad)))
for f in bad[:10]:
    print('   ', f)
