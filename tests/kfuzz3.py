"""Constant velocity (a = 0). The first fuzz kept |a| away from zero, so
this covers the most common Unit 1 question of all."""
import random, sys
sys.path.insert(0, '.')
import kinlib as K

rng = random.Random(5150)
COMBOS = [(i, j, k) for i in range(5) for j in range(i + 1, 5)
          for k in range(j + 1, 5)]
n = 0
bad = []
for _ in range(1500):
    u = rng.uniform(1, 60)
    t = rng.uniform(0.2, 40)
    truth = [u, u, 0.0, u * t, t]
    for c in COMBOS:
        s = [None] * 5
        for k in c:
            s[k] = truth[k]
        n += 1
        res = K.solve(s)
        if not res:
            continue          # genuinely not enough to pin the motion down
        for r in res:
            if not K.good(r[0]):
                bad.append(('kept a wrong one', c, truth, r[0]))
        hit = 0
        for r in res:
            if K.same(r[0], truth):
                hit = 1
        if not hit:
            bad.append(('truth missing', c, truth, [r[0] for r in res]))
print('CONSTANT VELOCITY: %d solves, PROBLEMS %d' % (n, len(bad)))
for b in bad[:5]:
    print('   ', b)
