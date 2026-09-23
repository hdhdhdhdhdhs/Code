# KIN - kinematics for the Casio fx-9750GIII
#
#   1 Find v,a,d,t   give any 3, leave the other boxes blank
#   2 Rate           (end - start) / time
#   3 Vector <-> x,y fill the top pair OR the bottom pair
#   4 Add 2 vectors  size then direction, twice
#   5 Projectile     speed, angle, height
#
# Units go beside the number:  10km   1.5h   72km/h   3m/s2
# A bare number means metres, seconds, m/s.
# a: type g for 9.8, or -g for -9.8.
# Directions: E N W S NE SE SW NW, or S30W, or plain degrees.
# In an x or y box a letter replaces the minus sign: 10S means -10.
W = 21
G = 9.8

DIST = (' m:1 metre:1 metres:1 meter:1 meters:1 km:1000 kilometre:1000'
        ' kilometres:1000 kilometer:1000 kilometers:1000 cm:0.01'
        ' centimetre:0.01 centimetres:0.01 centimeter:0.01 centimeters:0.01'
        ' mm:0.001 millimetre:0.001 millimetres:0.001 millimeter:0.001'
        ' millimeters:0.001 um:1e-6 nm:1e-9 ft:0.3048 foot:0.3048'
        ' feet:0.3048 in:0.0254 inch:0.0254 inches:0.0254 yd:0.9144'
        ' yard:0.9144 yards:0.9144 mi:1609.344 mile:1609.344'
        ' miles:1609.344 ')
TIME = (' s:1 sec:1 secs:1 second:1 seconds:1 min:60 mins:60 minute:60'
        ' minutes:60 h:3600 hr:3600 hrs:3600 hour:3600 hours:3600'
        ' d:86400 day:86400 days:86400 ms:0.001 us:1e-6 ns:1e-9 ')
VEL = (' m/s:1 ms-1:1 m/sec:1 km/h:0.27777777777778 km/hr:0.27777777777778'
       ' km/hour:0.27777777777778 kmh:0.27777777777778 cm/s:0.01'
       ' mm/s:0.001 km/s:1000 m/min:0.016666666666667 km/min:16.666666666667'
       ' m/h:0.00027777777777778 mph:0.44704 mi/h:0.44704 ft/s:0.3048'
       ' knot:0.51444444444444 knots:0.51444444444444 kt:0.51444444444444 ')
ACC = (' m/s2:1 m/s^2:1 m/s**2:1 m/s/s:1 mss:1 ms-2:1 ms^-2:1 g:9.8'
       ' cm/s2:0.01'
       ' mm/s2:0.001 km/h/s:0.27777777777778 km/s2:1000 ft/s2:0.3048 ')
ANG = ' deg:1 degree:1 degrees:1 rad:57.295779513082 radian:57.295779513082 '
CAN = (' m/s**2:m/s2 m/s^2:m/s2 m/s/s:m/s2 mss:m/s2 ms-2:m/s2'
       ' ms^-2:m/s2 ms-1:m/s m/sec:m/s kmh:km/h km/hr:km/h km/hour:km/h'
       ' mi/h:mph m/min:m/min ')
CMP = (' e:0 east:0 n:90 north:90 w:180 west:180 s:270 south:270'
       ' ne:45 nw:135 sw:225 se:315 northeast:45 northwest:135'
       ' southwest:225 southeast:315 ene:22.5 nne:67.5 nnw:112.5'
       ' wnw:157.5 wsw:202.5 ssw:247.5 sse:292.5 ese:337.5 ')
VD = VEL + DIST + ACC
HRU = (' km/h km/hr km/hour kmh mph mi/h knot knots kt h hr hrs hour'
       ' hours d day days km/min m/h ')
UN = ('m/s', 'm/s', 'm/s2', 'm', 's')
NM = ('v0', 'v', 'a', 'dist', 't')


def sv(t, k):
    i = t.find(' ' + k + ':')
    if i < 0:
        return None
    j = i + len(k) + 2
    return t[j:t.find(' ', j)]


def scan(s):
    """Where the number ends and the unit starts. 3.0e8 counts as one."""
    i = 0
    while i < len(s) and (s[i].isdigit() or s[i] == '.'):
        i += 1
    if i < len(s) and s[i] == 'e':
        j = i + 1
        if j < len(s) and (s[j] == '-' or s[j] == '+'):
            j += 1
        k = j
        while k < len(s) and s[k].isdigit():
            k += 1
        if k > j:
            i = k
    return i


def num(s, tab):
    """Read what was typed - 10km, -g, 1.5h - in the standard unit."""
    s = s.strip().lower().replace(' ', '')
    if s == '':
        return None
    sg = 1.0
    while s and (s[0] == '-' or s[0] == '+'):
        if s[0] == '-':
            sg = -sg
        s = s[1:]
    if s == 'g':
        return sg * G
    i = scan(s)
    if i == 0:
        raise ValueError('need a number')
    v = float(s[:i])
    if v != v or abs(v) > 1e300:
        raise ValueError('number too big')
    u = s[i:]
    if u == '':
        return sg * v
    m = sv(tab, u)
    if m is None:
        raise ValueError('bad unit ' + u)
    return sg * v * float(m)


def ang(s):
    """An angle box: 30, or a compass word like SE, or S30W."""
    s = s.strip().lower().replace(' ', '')
    if s == '':
        return None
    v = sv(CMP, s)
    if v is not None:
        return float(v)
    i = 0
    while i < len(s) and s[i].isalpha():
        i += 1
    j = i
    while j < len(s) and (s[j].isdigit() or s[j] == '.'):
        j += 1
    if i > 0 and j > i:
        b = sv(CMP, s[:i])
        t = sv(CMP, s[j:])
        if b is not None and t is not None:
            b = float(b)
            d = (float(t) - b) % 360.0
            if d > 180:
                d -= 360.0
            k = 1.0 if d > 0 else -1.0
            return (b + k * float(s[i:j])) % 360.0
    return num(s, ANG)


def unitof(s):
    """The unit text the user typed, if any."""
    s = s.strip().lower().replace(' ', '')
    while s[:1] == '-' or s[:1] == '+':
        s = s[1:]
    return s[scan(s):]


def uof(s):
    """The unit typed, ignoring any direction letter after it."""
    u = unitof(s)
    if u and sv(VD, u) is None and u[-1] in 'nsew':
        u = u[:-1]
    return u if u and sv(VD, u) is not None else ''


def show(x, u):
    """Print in the unit typed, but spelled the tidy way."""
    if u == '':
        return ns(x)
    return ns(x / float(sv(VD, u))) + ' ' + (sv(CAN, u) or u)


def two(l, v):
    """Label and value on one line if they fit, else on two."""
    t = l + ' = ' + v
    return [t] if len(t) <= W else [l, v]


def lab(u):
    """Name the answer from the unit: km is a displacement, km/h is not."""
    if u == '':
        return 'size'
    if sv(VEL, u) is not None:
        return 'velocity'
    if sv(ACC, u) is not None:
        return 'acceleration'
    return 'displacement'


def szb(s):
    """A size box. Says so when a direction was typed into it."""
    try:
        return num(s, VD)
    except Exception as e:
        m = str(e)
        raise ValueError('size: a number' if 'need a' in m else m)


def dirb(s):
    """A direction box. Says so when a size was typed into it."""
    try:
        return ang(s)
    except Exception:
        raise ValueError('dir: E N W S')


def comp(s, pos, neg):
    """A component box: 30, or 30E, or 10S - the letter gives the sign."""
    s = s.strip().lower().replace(' ', '')
    if s == '':
        return None
    try:
        return num(s, VD)
    except Exception:
        pass
    if s[-1] in 'nsew':
        c = s[-1]
        if c == pos:
            return num(s[:-1], VD)
        if c == neg:
            return -num(s[:-1], VD)
        raise ValueError('use ' + pos.upper() + ' or ' + neg.upper())
    return num(s, VD)


def deg(y, x):
    import math
    a = math.atan2(y, x) * 57.295779513082
    if a < 0:
        a += 360.0
    if 360.0 - a < 5e-5:
        a = 0.0
    return a


AX = ((0.0, 'E'), (90.0, 'N'), (180.0, 'W'), (270.0, 'S'))
TW = ' EN:N ES:S NW:W NE:E WS:S WN:N SE:E SW:W '


def compass(a):
    """Say the direction the way a physics answer says it."""
    a = a % 360.0
    bd = 999.0
    bn = 'E'
    for x, nm in AX:
        d = (a - x) % 360.0
        if d > 180:
            d -= 360.0
        if abs(d) < abs(bd):
            bd = d
            bn = nm
    if abs(bd) < 0.05:
        return 'due ' + bn
    if bn == 'E':
        to = 'N' if bd > 0 else 'S'
    elif bn == 'N':
        to = 'W' if bd > 0 else 'E'
    elif bn == 'W':
        to = 'S' if bd > 0 else 'N'
    else:
        to = 'E' if bd > 0 else 'W'
    if abs(abs(bd) - 45.0) < 0.05:
        p = 'N' if (bn == 'N' or to == 'N') else 'S'
        q = 'E' if (bn == 'E' or to == 'E') else 'W'
        return p + q
    return ns(abs(bd)) + ' ' + to + ' of ' + bn


def ns(x):
    """A number short enough for the screen."""
    a = abs(x)
    if a < 1e-12:
        return '0'
    r = round(x)
    if abs(x - r) < 1e-9 * (a if a > 1 else 1) and a < 1e9:
        return str(int(r))
    if a >= 1e7 or a < 1e-4:
        return '%.4g' % x
    d = 0
    b = a
    while b >= 1:
        b /= 10.0
        d += 1
    while b < 0.1:
        b *= 10.0
        d -= 1
    p = 4 - d
    if p < 0:
        p = 0
    t = '%.*f' % (p, x)
    if '.' in t:
        while t[-1] == '0':
            t = t[:-1]
        if t[-1] == '.':
            t = t[:-1]
    return t


def alt(k, x, hu=0):
    """The same value in a friendlier unit, when it is worth showing."""
    a = abs(x)
    if k == 3:
        if a >= 10000:
            return ns(x / 1000.0) + ' km'
        if 1e-6 < a < 0.01:
            return ns(x * 1000.0) + ' mm'
    elif k == 4:
        if a >= 3600:
            return ns(x / 3600.0) + ' h'
        if a >= 180:
            return ns(x / 60.0) + ' min'
    elif k < 2 and hu:
        return ns(x * 3.6) + ' km/h'
    return None


def hours(a):
    """Did the question itself talk in km/h or hours?"""
    for t in a:
        u = unitof(t)
        if u and (' ' + u + ' ') in HRU:
            return 1
    return 0


def e1(s, k):
    u, v, a, d, t = s
    if k == 1:
        return [u + a * t]
    if k == 0:
        return [v - a * t]
    if k == 2:
        return [] if t == 0 else [(v - u) / t]
    return [] if a == 0 else [(v - u) / a]


def e2(s, k):
    u, v, a, d, t = s
    if k == 3:
        return [u * t + 0.5 * a * t * t]
    if k == 0:
        return [] if t == 0 else [(d - 0.5 * a * t * t) / t]
    if k == 2:
        return [] if t == 0 else [2.0 * (d - u * t) / (t * t)]
    if a == 0:
        return [] if u == 0 else [d / u]
    q = u * u + 2.0 * a * d
    if q < 0:
        return []
    r = q ** 0.5
    return [(-u + r) / a, (-u - r) / a]


def e3(s, k):
    u, v, a, d, t = s
    if k == 1:
        q = u * u + 2.0 * a * d
        if q < 0:
            return []
        r = q ** 0.5
        return [r, -r]
    if k == 0:
        q = v * v - 2.0 * a * d
        if q < 0:
            return []
        r = q ** 0.5
        return [r, -r]
    if k == 2:
        return [] if d == 0 else [(v * v - u * u) / (2.0 * d)]
    return [] if a == 0 else [(v * v - u * u) / (2.0 * a)]


def e4(s, k):
    u, v, a, d, t = s
    if k == 3:
        return [0.5 * (u + v) * t]
    if k == 0:
        return [] if t == 0 else [2.0 * d / t - v]
    if k == 1:
        return [] if t == 0 else [2.0 * d / t - u]
    return [] if (u + v) == 0 else [2.0 * d / (u + v)]


EQ = ((e1, (0, 1, 2, 4), 'v=v0+at'),
      (e2, (0, 2, 3, 4), 'd=v0t+at2/2'),
      (e3, (0, 1, 2, 3), 'v2=v02+2ad'),
      (e4, (0, 1, 3, 4), 'd=(v+v0)t/2'))


def good(s):
    """Check a finished answer against all four equations."""
    u, v, a, d, t = s
    if t < -1e-9:
        return 0
    b = 1.0
    for x in (u, v, d, a * t):
        if abs(x) > b:
            b = abs(x)
    if abs(v - (u + a * t)) > 1e-6 * b:
        return 0
    dd = abs(d) if abs(d) > 1.0 else 1.0
    if abs(d - (u * t + 0.5 * a * t * t)) > 1e-6 * dd:
        return 0
    if abs(d - 0.5 * (u + v) * t) > 1e-6 * dd:
        return 0
    vv = v * v if v * v > 1.0 else 1.0
    if abs(v * v - (u * u + 2.0 * a * d)) > 1e-5 * vv:
        return 0
    return 1


def fill(s, used, out, dep):
    if None not in s:
        if good(s):
            out.append((list(s), list(used)))
        return
    if dep > 5:
        return
    for fn, vs, nm in EQ:
        ms = []
        for k in vs:
            if s[k] is None:
                ms.append(k)
        if len(ms) != 1:
            continue
        k = ms[0]
        try:
            vals = fn(s, k)
        except Exception:
            vals = []
        if not vals:
            continue
        n0 = len(out)
        for x in vals:
            s2 = list(s)
            s2[k] = x
            fill(s2, used + [(k, nm)], out, dep + 1)
        if len(out) > n0:
            return


def same(a, b):
    for i in range(5):
        p = abs(a[i])
        q = abs(b[i])
        sc = p if p > q else q
        if abs(a[i] - b[i]) > 1e-7 * (sc if sc > 1 else 1):
            return 0
    return 1


def solve(s):
    out = []
    fill(s, [], out, 0)
    keep = []
    for r in out:
        new = 1
        for h in keep:
            if same(h[0], r[0]):
                new = 0
                break
        if new:
            keep.append(r)
    return keep


def job1(a):
    s = [num(a[0], VEL), num(a[1], VEL), num(a[2], ACC),
         num(a[3], DIST), num(a[4], TIME)]
    n = 0
    for x in s:
        if x is not None:
            n += 1
    if n < 3:
        raise ValueError('need 3 numbers')
    if n == 5:
        return ['all 5 given'] + (['it fits'] if good(s) else ['does NOT fit'])
    hu = hours(a)
    miss = []
    for k in range(5):
        if s[k] is None:
            miss.append(k)
    res = solve(s)
    if not res:
        raise ValueError('no answer fits')
    o = []
    if len(res) > 1:
        o.append(str(len(res)) + ' answers:')
        tag = 'ABCDEF'
        for i in range(len(res)):
            ln = tag[i]
            for k in miss:
                ln += ' ' + NM[k] + '=' + ns(res[i][0][k])
            o.append(ln)
        for kk, nm in res[0][1]:
            o.append('via ' + nm)
        return o
    st, us = res[0]
    for k in miss:
        o.append(NM[k] + ' = ' + ns(st[k]) + ' ' + UN[k])
        v = alt(k, st[k], hu)
        if v:
            o.append('  = ' + v)
        for kk, nm in us:
            if kk == k:
                o.append('  via ' + nm)
    return o


def job2(a):
    p = a[0].strip().lower()
    q = a[1].strip().lower()
    kind = 3
    for u in (p, q):
        try:
            num(u, DIST)
        except Exception:
            kind = 0
    tab = VEL if kind == 0 else DIST
    x = num(p, tab)
    y = num(q, tab)
    t = num(a[2], TIME)
    if x is None or y is None or t is None:
        raise ValueError('need all 3')
    if t == 0:
        raise ValueError('time is 0')
    r = (y - x) / t
    k = 2 if kind == 0 else 0
    o = [('a' if k == 2 else 'v') + ' = ' + ns(r) + ' ' + UN[k]]
    v = alt(k, r, hours(a))
    if v:
        o.append('  = ' + v)
    return o


def job3(a):
    sz = szb(a[0])
    an = dirb(a[1])
    x = comp(a[2], 'e', 'w')
    y = comp(a[3], 'n', 's')
    import math
    if sz is not None and an is not None:
        u = uof(a[0])
        r = an * 0.017453292519943
        return ['x = ' + show(sz * math.cos(r), u),
                'y = ' + show(sz * math.sin(r), u)]
    if x is not None and y is not None:
        u = uof(a[2]) or uof(a[3])
        sz = (x * x + y * y) ** 0.5
        if sz < 1e-9 * (abs(x) + abs(y) + 1.0):
            return ['size = 0', 'no direction']
        return two(lab(u), show(sz, u)) + [compass(deg(y, x))]
    raise ValueError('size+ang or x,y')


def job4(a):
    import math
    s1 = szb(a[0])
    a1 = dirb(a[1])
    s2 = szb(a[2])
    a2 = dirb(a[3])
    if s1 is None or a1 is None or s2 is None or a2 is None:
        raise ValueError('need all 4')
    c = 0.017453292519943
    x = s1 * math.cos(a1 * c) + s2 * math.cos(a2 * c)
    y = s1 * math.sin(a1 * c) + s2 * math.sin(a2 * c)
    sz = (x * x + y * y) ** 0.5
    if sz < 1e-9 * (abs(s1) + abs(s2) + 1.0):
        return ['size = 0', 'no direction', 'they cancel out']
    an = deg(y, x)
    u = uof(a[0]) or uof(a[2])
    return two(lab(u), show(sz, u)) + [compass(an),
            'x = ' + show(x, u), 'y = ' + show(y, u)]


def job5(a):
    import math
    sp = num(a[0], VEL)
    an = num(a[1], ANG)
    h = num(a[2], DIST)
    if sp is None:
        raise ValueError('need a speed')
    if an is None:
        an = 0.0
    if h is None:
        h = 0.0
    vx = sp * math.cos(an * 0.017453292519943)
    vy = sp * math.sin(an * 0.017453292519943)
    q = vy * vy + 2.0 * G * h
    if q < 0:
        raise ValueError('never lands')
    t = (vy + q ** 0.5) / G
    if t <= 1e-12:
        raise ValueError('give it a height')
    pk = h + (vy * vy) / (2.0 * G) if vy > 0 else h
    hv = (vx * vx + (vy - G * t) ** 2) ** 0.5
    o = ['t air = ' + ns(t) + ' s',
         't up = ' + ns(vy / G if vy > 0 else 0) + ' s',
         'range = ' + ns(vx * t) + ' m',
         'peak = ' + ns(pk) + ' m', 'hit v = ' + ns(hv) + ' m/s']
    v = alt(3, vx * t)
    if v:
        o.insert(3, '  = ' + v)
    return o


JOB = (job1, job2, job3, job4, job5)
ASK = (('v0:', 'v:', 'a:', 'dist:', 't:'), ('Start:', 'End:', 'Time:'),
       ('size:', 'dir:', 'x:', 'y:'),
       ('V1 size:', 'V1 dir:', 'V2 size:', 'V2 dir:'),
       ('Speed:', 'Angle:', 'Height:'))
MENU = ('Find v,a,d,t|Rate=change/time|Vector <-> x,y|Add 2 vectors|'
        'Projectile').split('|')


def wrap(t):
    o = []
    while len(t) > W:
        o.append(t[:W])
        t = t[W:]
    o.append(t)
    return o


while True:
    for i in range(5):
        print(str(i + 1) + ' ' + MENU[i])
    try:
        k = input('Pick 1-5:').strip()
    except (KeyboardInterrupt, EOFError):
        break
    if k not in ('1', '2', '3', '4', '5'):
        if k != '':
            print('1 to 5 only')
        continue
    n = int(k)
    if n == 1:
        print('Blank = unknown')
    b = []
    try:
        for q in ASK[n - 1]:
            b.append(input(q))
    except (KeyboardInterrupt, EOFError):
        break
    try:
        out = JOB[n - 1](b)
    except Exception as e:
        out = wrap('Err: ' + (str(e) or 'bad input'))
    for ln in out:
        for x in wrap(ln):
            print(x)
    try:
        input('')
    except (KeyboardInterrupt, EOFError):
        break
