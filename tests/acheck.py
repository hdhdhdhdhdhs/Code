# algebra/ against itself and against junk (screen lines as shown):
#   idem    a simplified Ans typed back gives the same Ans
#   zero    (question)-(Ans) simplifies to 0
#   typing  ** for ^, spaces, capitals, the question split into
#           Top/Bottom pieces by the input loop: the same screen
#   junk    random typing: an answer or a clean Err, never a Python
#           error leaking out, never over 5 seconds, never over 21 wide
#
#   python3 acheck.py [count] [seed]      (run from tests/, sympy on
#   PYTHONPATH for the fraction questions)
import sys, random, signal

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sys.path.insert(0, '../algebra')
import algcore

W = algcore.W
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
        return [algcore.st(l) for l in algcore.go(q)]
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


def gens():
    sys.argv = ['x', '../rad.py', '1', str(SEED)]
    a = {}
    exec(open('rfuzz.py').read().split('# ---------------------------------------------------------- reference')[0], a)
    sys.argv = ['x', '../radsimp.py', '1', str(SEED)]
    b = {}
    exec(open('sfuzz.py').read().split('# ---------------------------------------------------------- checking')[0], b)
    sys.argv = ['x', '1', str(SEED)]
    c = {'__name__': 'x'}
    exec(open('frfuzz.py').read().split("if __name__")[0], c)
    c['init']()
    return a['gen'], b['gen'], (lambda n: c['gen'](n)[0::2])


egen, sgen, fgen = gens()


def junk():
    return ''.join(r.choice(['sqrt(', '(', ')', '+', '-', '*', '/', '^', '**', '=', '.', ' ', 'x', 'y', 'a', '1',
                             '2', '0', '9', '3', '(x+1)', '(x-1)', 'x^2', '/(', ')^-1', '^0', '^(1/2)', '^0.5',
                             '^40', '^-40', ',', '!', '#', 'X', '99999999999', '=0'])
                   for _ in range(r.randint(0, 20)))


def mutate(s):
    if not s:
        return s
    i = r.randrange(len(s))
    k = r.random()
    if k < 0.3:
        return s[:i] + s[i + 1:]
    if k < 0.6:
        return s[:i] + r.choice('()+-*/^.x0=') + s[i:]
    return s[:i] + r.choice('()+-*/^.x0=') + s[i + 1:]


def pieces(q):
    # the question as the input loop builds it from Top/Bottom pieces:
    # each top-level term its own top, bottom 1
    o = ''
    d = 0
    cur = ''
    for c in q:
        if c in '+-' and d == 0 and cur and cur[-1] not in '*/^(=':
            o += '((' + cur + ')/(1))' + c
            cur = ''
            continue
        if c == '=' and d == 0:
            o += '((' + cur + ')/(1))='
            cur = ''
            continue
        d += (c == '(') - (c == ')')
        cur += c
    return o + '((' + cur + ')/(1))' if cur else o


for n in range(N):
    for kind, g in (('equation', egen), ('roots', sgen), ('fractions', fgen)):
        name, q = g(n)
        out = run(q)
        for l in out:
            for w in algcore.wrap(l):
                if len(w) > W:
                    flag('wide', q, w)
        for k, v in (('**', q.replace('^', '**')), ('caps', q.upper()), ('spaces', ' '.join(q)),
                     ('pieces', pieces(q.replace(' ', '')))):
            o2 = run(v)
            if o2 != out:
                # Top/Bottom pieces add brackets: only the answer must agree
                if k != 'pieces' or ans(o2) != ans(out):
                    flag('typing ' + k, q, v, out, o2)
        a = ans(out)
        if kind == 'equation' or a is None or '|' in a:
            continue
        a2 = ans(run(a))
        if a2 != a:
            flag('idem', q, a, a2)
        z = ans(run('(' + q + ')-(' + a + ')'))
        if z != '0':
            flag('zero', q, a, z)
    # junk, and good questions with a slip of the finger
    for q in (junk(), mutate(egen(n)[1]), mutate(sgen(n)[1]), mutate(fgen(n)[1])):
        out = run(q)
        for l in out:
            for w in algcore.wrap(l):
                if len(w) > W:
                    flag('wide', q, w)

for k in sorted(bad):
    print('%-16s %d' % (k, len(bad[k])))
    for x in bad[k][:4]:
        print('    ', str(x)[:600])
print(N, 'of each kind and', 4 * N, 'junk;', sum(len(v) for v in bad.values()), 'problems')
