# frac.py against itself and against junk (no sympy needed):
#   idem    Ans typed back gives the same Ans; so does Fac
#   zero    (question)-(Ans) gives Ans: 0
#   typing  ** for ^, * put in, spaces, capitals: the same screen
#   junk    random typing: an answer or a clean Err, never a Python
#           error leaking out, never over 5 seconds, never over 21 wide
#
#   python3 fcheck.py [count] [seed]      (run from tests/)
import sys, random, re, signal

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
src = open('../frac.py').read()
G = {}
exec(src[:src.index("print('Rational expressions")], G)
go = lambda q: [G['st'](l) for l in G['go'](q)]  # as the screen shows it
wrap, W = G['wrap'], G['W']

# questions from frfuzz's kinds, written out already (it needs sympy to
# multiply out), plus junk made here
qs = open(sys.argv[3]).read().split('\n') if len(sys.argv) > 3 else []
r = random.Random(SEED)


class Slow(Exception):
    pass


def alarm(*a):
    raise Slow()


signal.signal(signal.SIGALRM, alarm)
bad = {}


def flag(k, *a):
    bad.setdefault(k, []).append(a)


def run(q):
    signal.alarm(5)
    try:
        return go(q)
    except Slow:
        flag('slow', q)
        return ['Err: slow']
    except ValueError as e:
        return ['Err: ' + str(e)]
    except Exception as e:
        flag('leak ' + type(e).__name__, q, str(e))
        return ['Err: ' + str(e)]
    finally:
        signal.alarm(0)


def ans(o):
    for l in o:
        if l.startswith('Ans: '):
            return l[5:]


def fac(o):
    for l in o:
        if l.startswith('Fac: '):
            return l[5:]


def junk():
    return ''.join(r.choice(['(', ')', '+', '-', '*', '/', '^', '**', '=', '.', ' ', 'x', 'y', 'a', '1', '2',
                             '0', '9', '3', '(x+1)', '(x-1)', 'x^2', '/(', ')^-1', '^0', '^40', '^-40', 'sqrt',
                             ',', '!', '#', '[', 'X', '99999999999'])
                   for _ in range(r.randint(0, 20)))


def mutate(s):
    if not s:
        return s
    i = r.randrange(len(s))
    k = r.random()
    if k < 0.3:
        return s[:i] + s[i + 1:]
    if k < 0.6:
        return s[:i] + r.choice('()+-*/^.x0') + s[i:]
    return s[:i] + r.choice('()+-*/^.x0') + s[i + 1:]


def stars(s):
    s = re.sub(r'(?<=[\d)a-z])(?=[a-z(])', '*', s)
    return s


n = 0
for i in range(N):
    q = qs[i % len(qs)] if qs and i < len(qs) else (junk() if r.random() < 0.5 else mutate(r.choice(qs) if qs else 'x/(x+1)'))
    out = run(q)
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                flag('wide', q, w)
    a = ans(out)
    if a is None or i >= len(qs):
        continue
    n += 1
    for t in (a, fac(out)):
        if t:
            a2 = ans(run(t))
            if a2 != a:
                flag('idem', q, t, a, a2)
    z = ans(run('(' + q + ')-(' + a + ')'))
    if z != '0':
        flag('zero', q, a, z)
    for kind, v in (('**', q.replace('^', '**')), ('stars', stars(q)), ('spaces', ' '.join(q)), ('caps', q.upper())):
        o2 = run(v)
        if o2 != out:
            flag('typing ' + kind, q, v, out, o2)

for k in sorted(bad):
    print('%-16s %d' % (k, len(bad[k])))
    for x in bad[k][:4]:
        print('    ', str(x)[:500])
print(N, 'inputs,', n, 'answers checked against themselves;', sum(len(v) for v in bad.values()), 'problems')
