# rad.py against junk: random typing must give an answer or a clean
# "Err: ..." message - never a Python error leaking through (IndexError,
# KeyError, TypeError, ZeroDivisionError, RecursionError ...), never more
# than 5 seconds, never a line over 21 columns.
#   python3 crash.py [count] [seed]      (run from tests/)
import sys, random, signal

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sys.path.insert(0, '..')
src = open('../rad.py').read()
G = {}
exec(src[:src.index("print('Root equations")], G)
solve, wrap, W = G['solve'], G['wrap'], G['W']
import radsimp

r = random.Random(SEED)
LET = 'abcdefghijklmnopqrstuvwxyz'


def num():
    k = r.random()
    if k < 0.5:
        return str(r.randint(0, 20))
    if k < 0.65:
        return str(r.randint(0, 10 ** r.randint(3, 40)))
    if k < 0.8:
        return '%d.%d' % (r.randint(0, 99), r.randint(0, 999))
    if k < 0.9:
        return '(%d/%d)' % (r.randint(-20, 20), r.randint(-5, 20))
    return r.choice(['0', '0.0', '.5', '5.', '00', '0.000', '1e5', '-0'])


def ex(d):
    # a random expression, mostly well formed
    k = r.random()
    if d > r.randint(2, 7) or k < 0.25:
        return r.choice([num(), r.choice(LET), 'x', 'x', num() + 'x', 'x' + str(r.randint(0, 3))])
    if k < 0.45:
        return 'sqrt(' + ex(d + 1) + ')'
    if k < 0.55:
        return '(' + ex(d + 1) + ')'
    if k < 0.65:
        return '(' + ex(d + 1) + ')' + r.choice(['^2', '^3', '^(1/2)', '^0.5', '^(3/2)', '**2', '^0', '^25',
                                                    '^-1', '^(1/3)', '^x', '^1.5', '^(5/2)', '^(2/4)'])
    op = r.choice(['+', '-', '*', '/', '', '', '+', '-'])
    return ex(d + 1) + op + ex(d + 1)


def junk():
    return ''.join(r.choice(['sqrt(', '(', ')', '+', '-', '*', '/', '^', '**', '=', '.', ' ', 'x', 'y', 's',
                             'q', 'r', 't', '1', '2', '0', '9', 'math.', 'sqrt', 'X', 'Y', ',', '!', '"', '#',
                             '%', '&', '[', ']', '{', '_', '<', '>', '?', '\\', '|', '~', 'e', 'pi', '√', 'é'])
                   for _ in range(r.randint(0, 25)))


def mutate(s):
    # a good question with one slip of the finger
    if not s:
        return s
    i = r.randrange(len(s))
    k = r.random()
    if k < 0.3:
        return s[:i] + s[i + 1:]
    if k < 0.6:
        return s[:i] + r.choice('()+-*/^=.x0sqrt') + s[i:]
    return s[:i] + r.choice('()+-*/^=.x0') + s[i + 1:]


class Slow(Exception):
    pass


def alarm(*a):
    raise Slow()


signal.signal(signal.SIGALRM, alarm)
leaks = {}
slow = []
wide = []
n_ans = n_err = 0
for n in range(N):
    k = r.random()
    if k < 0.35:
        q = ex(0)
    elif k < 0.7:
        q = ex(0) + '=' + ex(0)
    elif k < 0.85:
        q = mutate(ex(0) + r.choice(['', '=' + ex(0)]))
    else:
        q = junk()
    signal.alarm(5)
    try:
        out = solve(q)
        n_ans += 1
    except Slow:
        slow.append(q)
        continue
    except ValueError as e:
        out = ['Err: ' + str(e)]
        n_err += 1
    except Exception as e:
        leaks.setdefault(type(e).__name__ + ': ' + str(e)[:60], []).append(q)
        out = ['Err: ' + str(e)]
    finally:
        signal.alarm(0)
    for l in out:
        for w in wrap(l):
            if len(w) > W:
                wide.append((q, w))
print(N, 'inputs:', n_ans, 'answered,', n_err, 'clean errors')
print('leaked Python errors:', sum(len(v) for v in leaks.values()))
for k in sorted(leaks, key=lambda k: -len(leaks[k])):
    print('  %5d  %s' % (len(leaks[k]), k))
    for q in leaks[k][:3]:
        print('         ', repr(q)[:150])
print('over 5 seconds:', len(slow))
for q in slow[:8]:
    print('         ', repr(q)[:150])
print('lines over 21:', len(wide))
for q, w in wide[:5]:
    print('         ', repr(q)[:100], repr(w))
