"""Independent check: build a motion from v0, a, t where every value is
known exactly, then hand the program every possible set of 3 and require
the true motion back."""
import random, sys
sys.path.insert(0, '.')
import kinlib as K

rng = random.Random(9750)
COMBOS = []
for i in range(5):
    for j in range(i + 1, 5):
        for k in range(j + 1, 5):
            COMBOS.append((i, j, k))

n = 0
bad = []
for trial in range(4000):
    u = rng.uniform(-40, 40)
    a = rng.choice([rng.uniform(-15, 15), -9.8, 9.8])
    t = rng.uniform(0.2, 12)
    if abs(a) < 0.3:
        a = 2.5
    v = u + a * t
    d = u * t + 0.5 * a * t * t
    truth = [u, v, a, d, t]
    for c in COMBOS:
        s = [None] * 5
        for k in c:
            s[k] = truth[k]
        n += 1
        res = K.solve(s)
        if not res:
            bad.append(('no answer', c, truth))
            continue
        hit = 0
        for r in res:
            if K.same(r[0], truth):
                hit = 1
                break
        if not hit:
            bad.append(('truth missing', c, truth, [r[0] for r in res]))
        for r in res:
            if not K.good(r[0]):
                bad.append(('bad answer kept', c, truth, r[0]))

print('KINEMATICS FUZZ: %d solves, PROBLEMS %d' % (n, len(bad)))
for b in bad[:8]:
    print('   ', b)
