# algebra/ against the three programs it was made from: every question
# from the rad.py, radsimp.py and frac.py checkers' kinds must give the
# same screen, except for what is new:
#   equations      an NPV line may be added; an identity says 'but NPV'
#                  for 'except where a bottom is 0'; over the lowest common
#                  bottom, Fails may lose values and the polynomial change
#                  (Restr and Ans stay the same)
#   roots, no =    NPV and Ans NPV lines may be added, and Restr may gain what each
#                  root needs (everything the old Restr said is kept); an
#                  answer with no roots left is as frac.py gives it; and
#                  an answer may change (equal at numbers) when the old
#                  one left a fraction inside a bottom; an Entire line
#                  (one root) is the answer's value
#   fractions      exactly the same, but for a Fac line (the top
#                  factored, with no letter in the bottom; equal at numbers)
#
#   python3 acompare.py [count] [seed]     (run from tests/, needs sympy
#   on PYTHONPATH for the fraction questions)
import sys, re, math, random

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sys.path.insert(0, '..')
sys.path.insert(0, '../algebra')

# the old programs
G = {}
s = open('../rad.py').read()
exec(s[:s.index("print('Roots: solve")], G)
H = {}
s = open('../frac.py').read()
exec(s[:s.index("print('Rational expressions")], H)
import algcore


def old(q):
    t = q.lower().replace(' ', '').replace('**', '^')
    if '=' in t or 'sqrt' in t:
        f = G['solve']
    else:
        try:
            return [G['st'](l) for l in H['go'](q)]
        except ValueError as e:
            if str(e) != 'bad power':
                raise
            f = G['solve']
    return [G['st'](l) for l in f(q)]


def new(q):
    return [algcore.st(l) for l in algcore.go(q)]


def pyx(t):
    # the screen's text as Python
    t = re.sub(r'\|([^|]*)\|', r'A(\1)', t.replace(' ', '').replace('math.', ''))
    t = t.replace('sqrt(', 'S(').replace('^', '**')
    t = re.sub(r'(?<=[\da-z)])(?=[a-zSA(])', '*', t)
    return t


def same(q, a, b):
    # a and b (answers) equal at numbers put in for the letters, where
    # the question is
    V = sorted(set(re.findall('[a-z]', q.lower().replace('sqrt', '').replace('math.', ''))))
    n = 0
    for i in range(80):
        p = dict((v, random.uniform(0.01, (1, 3, 30)[i % 3])) for v in V)
        p['S'] = math.sqrt
        p['A'] = abs
        try:
            x = eval(pyx(q.lower()), p)
            y = eval(pyx(a), p)
            z = eval(pyx(b), p)
        except (ZeroDivisionError, ValueError, OverflowError):
            continue
        if abs(y - z) > 1e-6 * (1 + abs(y)) or abs(x - z) > 1e-6 * (1 + abs(x)):
            return False
        n += 1
    return n > 5 or None


def run(f, q):
    try:
        return f(q)
    except Exception as e:
        return ['Err: ' + (str(e) or 'bad input')]


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
bad = {}
seen = {'npv lines added': 0, 'restr pieces added': 0, 'answers through frac': 0, 'answers changed': 0,
        'answers longer': 0, 'answers changed, no numbers to try': 0, 'entire lines': 0, 'fewer fails': 0,
        'polynomial changed': 0, 'fac lines': 0}
longer = []
for n in range(N):
    for kind, g in (('equation', egen), ('roots', sgen), ('fractions', fgen)):
        name, q = g(n)
        a = run(old, q)
        b = run(new, q)
        if a == b:
            continue
        if kind == 'fractions':
            # a Fac line may be added: the answer's top factored, the
            # same at numbers
            F = [l for l in b if l[:5] == 'Fac: ']
            ba = [l[5:] for l in b if l[:5] == 'Ans: ']
            if F and [l for l in b if l not in F] == a:
                seen['fac lines'] += 1
                if same(q, ba[0], F[0][5:]) is False:
                    bad.setdefault('fractions: Fac wrong', []).append((q, b))
                continue
            bad.setdefault(kind, []).append((q, a, b))
            continue
        # what may differ: NPV lines added; for roots, Restr pieces added
        b2 = [l for l in b if not l.startswith('NPV: ') and not l.startswith('Ans NPV: ')]
        # the entire radical: one root, the same as the answer at numbers
        E = [l for l in b2 if l.startswith('Entire: ')]
        if E:
            seen['entire lines'] += 1
            ea = E[0][8:].split(', ')[0]
            ba = [l[5:] for l in b2 if l[:5] == 'Ans: ']
            if ea.count('sqrt') != 1 or not ba or same(q, ba[0], ea) is False:
                bad.setdefault('roots: Entire wrong', []).append((q, b))
                continue
            b2 = [l for l in b2 if l not in E]
        if kind == 'equation':
            # multiplied by the lowest common bottom: the same answers, and
            # what fails is some of what failed; the polynomial may change
            fa = [l for l in a if l[:7] == 'Fails: ']
            fb = [l for l in b2 if l[:7] == 'Fails: ']
            fa = fa[0][7:].split(', ') if fa else []
            fb = fb[0][7:].split(', ') if fb else []
            if [t for t in fb if t not in fa]:
                bad.setdefault('equation: new Fails', []).append((q, a, b))
                continue
            seen['fewer fails'] += len(fb) < len(fa)
            a = [l for l in a if l[:7] != 'Fails: ']
            b2 = [l for l in b2 if l[:7] != 'Fails: ']
            if [l for l in a if l[:4] in ('Ans:', 'Rest')] == [l for l in b2 if l[:4] in ('Ans:', 'Rest')]:
                seen['polynomial changed'] += a != b2
                continue
        # an identity now names the NPVs it leaves out
        a = [l.replace('every x except where a bottom is 0', 'every x but NPV') for l in a]
        seen['npv lines added'] += len(b2) < len(b)
        if kind == 'roots':
            ra = [l for l in a if l.startswith('Restr: ')]
            rb = [l for l in b2 if l.startswith('Restr: ')]
            pa = ra[0][7:].split(', ') if ra else []
            pb = rb[0][7:].split(', ') if rb else []
            if [p for p in pa if p not in pb]:
                bad.setdefault('roots: Restr lost a piece', []).append((q, a, b))
                continue
            seen['restr pieces added'] += len(pb) > len(pa)
            a = [l for l in a if not l.startswith('Restr: ')]
            b2 = [l for l in b2 if not l.startswith('Restr: ')]
            for i in range(len(a)):
                t = a[i]
                if t[:5] == 'Ans: ' and 'sqrt' not in t and '|' not in t and '~' not in t:
                    try:
                        a[i] = G['st'](H['go'](t[5:].replace('*', ''))[0])
                    except ValueError:
                        pass
                    seen['answers through frac'] += a[i] != t
        if a != b2 and kind == 'roots':
            # a new answer must be the same at numbers, and no longer
            aa = [l[5:] for l in a if l[:5] == 'Ans: ']
            ba = [l[5:] for l in b2 if l[:5] == 'Ans: ']
            if aa and ba and aa[0] != ba[0]:
                k = same(q, aa[0], ba[0])
                if k is None:
                    seen['answers changed, no numbers to try'] += 1
                elif not k:
                    bad.setdefault('roots: new answer not the same', []).append((q, a, b))
                    continue
                seen['answers changed'] += 1
                if len(ba[0]) > len(aa[0]):
                    seen['answers longer'] += 1
                    longer.append((q, aa[0], ba[0]))
                a = [l for l in a if l[:5] != 'Ans: ' and l[:6] != 'Times ']
                b2 = [l for l in b2 if l[:5] != 'Ans: ' and l[:6] != 'Times ']
        if a != b2:
            bad.setdefault(kind, []).append((q, a, b))
for k in sorted(bad):
    print('%-28s %d' % (k, len(bad[k])))
    for x in bad[k][:5]:
        print('    ', str(x)[:700])
print(seen)
for x in longer[:8]:
    print('  longer:', x)
print(N, 'of each kind;', sum(len(v) for v in bad.values()), 'differences')
