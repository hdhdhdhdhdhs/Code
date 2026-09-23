"""Fuzz options 2-5. Every check uses a formula the program does not use:
the projectile's landing is verified by putting the reported time back
into the height equation, and its impact speed by conservation of energy
rather than by components."""
import random, math, sys
sys.path.insert(0, '.')
import kinlib as K

rng = random.Random(31415)
G = 9.8
bad = []
n = 0


def val(line):
    """Pull the number out of 'x = 43.3' style output."""
    t = line.split('=')[-1].strip()
    p = ''
    for c in t:
        if c.isdigit() or c in '.-+e':
            p += c
        else:
            break
    return float(p)


AXA = {'E': 0.0, 'N': 90.0, 'W': 180.0, 'S': 270.0}
CORN = {'NE': 45.0, 'NW': 135.0, 'SW': 225.0, 'SE': 315.0}


def unbear(t):
    """Read the compass line back into an angle - checks the words too."""
    t = t.strip()
    if t.startswith('due '):
        return AXA[t[4:]]
    if t in CORN:
        return CORN[t]
    p = t.split()                      # '18.43 S of E'
    off = float(p[0]); to = p[1]; base = p[3]
    b = AXA[base]
    d = (AXA[to] - b) % 360.0
    if d > 180:
        d -= 360.0
    return (b + (1.0 if d > 0 else -1.0) * off) % 360.0


def near(a, b, tol=2e-3):
    s = max(1.0, abs(a), abs(b))
    return abs(a - b) <= tol * s


# ---- option 2: rate ----
for _ in range(3000):
    n += 1
    a = rng.uniform(-500, 500)
    b = rng.uniform(-500, 500)
    t = rng.uniform(0.1, 500)
    u, m = rng.choice([('', 1.0), ('km', 1000.0), ('cm', 0.01), ('mi', 1609.344)])
    tu, tm = rng.choice([('', 1.0), ('min', 60.0), ('h', 3600.0), ('ms', 0.001)])
    try:
        out = K.job2(['%g%s' % (a, u), '%g%s' % (b, u), '%g%s' % (t, tu)])
    except Exception as e:
        bad.append(('job2', a, b, t, u, tu, str(e)))
        continue
    want = (b * m - a * m) / (t * tm)
    if not near(val(out[0]), want):
        bad.append(('job2 value', a, b, t, u, tu, out[0], want))

# ---- option 3: vector <-> components ----
for _ in range(3000):
    n += 1
    sz = rng.uniform(0.5, 500)
    an = rng.uniform(0, 360)
    o = K.job3(['%g' % sz, '%g' % an, '', ''])
    x = val(o[0])
    y = val(o[1])
    # independent: the pair must have the right length and direction
    if not near((x * x + y * y) ** 0.5, sz):
        bad.append(('job3 length', sz, an, o))
    d = (math.degrees(math.atan2(y, x)) - an) % 360.0
    if min(d, 360.0 - d) > 0.05:
        bad.append(('job3 angle', sz, an, o))
    n += 1
    o2 = K.job3(['', '', '%.10g' % x, '%.10g' % y])
    if o2[1] == 'no direction':
        continue
    if o2[0].startswith('displacement') and '=' not in o2[0]:
        o2 = [o2[0] + ' = ' + o2[1]] + o2[2:]
    sz2 = val(o2[0])
    an2 = unbear(o2[1])
    # independent: rebuild the components from what came back.
    # a 4-figure angle is good to about 0.05 deg, which moves a point by
    # size * 9e-4, so the slack has to scale with the size, not with x.
    tol = sz2 * 3e-3 + 1e-9
    if abs(sz2 * math.cos(math.radians(an2)) - x) > tol or \
       abs(sz2 * math.sin(math.radians(an2)) - y) > tol:
        bad.append(('job3 round trip', sz, an, o, o2))

# ---- option 4: adding two vectors ----
for _ in range(3000):
    n += 1
    s1 = rng.uniform(0.5, 200); a1 = rng.uniform(0, 360)
    s2 = rng.uniform(0.5, 200); a2 = rng.uniform(0, 360)
    o = K.job4(['%g' % s1, '%g' % a1, '%g' % s2, '%g' % a2])
    if len(o) > 1 and o[1] == 'no direction':
        continue
    wx = s1 * math.cos(math.radians(a1)) + s2 * math.cos(math.radians(a2))
    wy = s1 * math.sin(math.radians(a1)) + s2 * math.sin(math.radians(a2))
    if '=' not in o[0]:
        o = [o[0] + ' = ' + o[1]] + o[2:]
    sz = val(o[0]); an = unbear(o[1])
    if not near(sz, (wx * wx + wy * wy) ** 0.5):
        bad.append(('job4 size', s1, a1, s2, a2, o))
    tol = sz * 3e-3 + 1e-9
    if abs(sz * math.cos(math.radians(an)) - wx) > tol or \
       abs(sz * math.sin(math.radians(an)) - wy) > tol:
        bad.append(('job4 dir', s1, a1, s2, a2, o))

# ---- option 5: projectile ----
for _ in range(3000):
    n += 1
    sp = rng.uniform(1, 200)
    an = rng.uniform(-80, 89)
    h = rng.choice([0.0, rng.uniform(0.1, 500)])
    try:
        o = K.job5(['%g' % sp, '%g' % an, '%g' % h])
    except Exception as e:
        if 'give it a height' in str(e) and h == 0 and an <= 0:
            continue
        bad.append(('job5', sp, an, h, str(e)))
        continue
    t = val(o[0]); rg = val(o[1]); pk = val(o[2]); hv = val(o[3])
    vx = sp * math.cos(math.radians(an))
    vy = sp * math.sin(math.radians(an))
    # 1. put the reported time back into the height equation: must land
    land = h + vy * t - 0.5 * G * t * t
    if abs(land) > 2e-3 * max(1.0, h, abs(vy * t)):
        bad.append(('job5 does not land', sp, an, h, o, land))
    if t < 0:
        bad.append(('job5 negative t', sp, an, h, o))
    # 2. range is just how far it travelled sideways in that time
    if not near(rg, vx * t):
        bad.append(('job5 range', sp, an, h, o))
    # 3. peak from the height equation at the moment vy runs out
    wpk = h + (vy * vy) / (2 * G) if vy > 0 else h
    if not near(pk, wpk):
        bad.append(('job5 peak', sp, an, h, o))
    # 4. impact speed by energy, not by components
    if not near(hv, (sp * sp + 2 * G * h) ** 0.5):
        bad.append(('job5 impact', sp, an, h, o))

print('OPTIONS 2-5 FUZZ: %d checks, PROBLEMS %d' % (n, len(bad)))
for b in bad[:8]:
    print('   ', b)
