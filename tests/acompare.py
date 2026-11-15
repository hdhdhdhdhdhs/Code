# algebra/ against the three programs it was made from: every question
# from the rad.py, radsimp.py and frac.py checkers' kinds must give the
# same screen, except for what is new:
#   equations      an NPV line may be added (nothing else changes)
#   roots, no =    an NPV line may be added, and Restr may gain what each
#                  root needs (everything the old Restr said is kept)
#   fractions      exactly the same
#
#   python3 acompare.py [count] [seed]     (run from tests/, needs sympy
#   on PYTHONPATH for the fraction questions)
import sys

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
seen = {'npv lines added': 0, 'restr pieces added': 0}
for n in range(N):
    for kind, g in (('equation', egen), ('roots', sgen), ('fractions', fgen)):
        name, q = g(n)
        a = run(old, q)
        b = run(new, q)
        if a == b:
            continue
        if kind == 'fractions':
            bad.setdefault(kind, []).append((q, a, b))
            continue
        # what may differ: NPV lines added; for roots, Restr pieces added
        b2 = [l for l in b if not l.startswith('NPV: ')]
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
        if a != b2:
            bad.setdefault(kind, []).append((q, a, b))
for k in sorted(bad):
    print('%-28s %d' % (k, len(bad[k])))
    for x in bad[k][:5]:
        print('    ', str(x)[:700])
print(seen)
print(N, 'of each kind;', sum(len(v) for v in bad.values()), 'differences')
