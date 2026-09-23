"""Real Physics 11 questions. Expected values computed here from the
physics, independently of the program, then compared."""
import math, sys
sys.path.insert(0, '.')
import kinlib as K
G = 9.8
bad = 0


def pull(out):
    d = {}
    for ln in out:
        if '=' in ln and not ln.startswith('  '):
            k = ln.split('=')[0].strip()
            t = ln.split('=')[-1].strip()
            p = ''
            for c in t:
                if c.isdigit() or c in '.-+e':
                    p += c
                else:
                    break
            if p not in ('', '-', '+'):
                d[k] = float(p)
    return d


def q(n, text, fn, a, want):
    global bad
    out = fn(a)
    got = pull(out)
    ok = True
    miss = []
    for k in want:
        if k not in got or abs(got[k] - want[k]) > 2e-3 * max(1.0, abs(want[k])):
            ok = False
            miss.append('%s got %s want %.4f' % (k, got.get(k), want[k]))
    if not ok:
        bad += 1
    print('%s Q%-2d %s' % ('ok ' if ok else 'BAD', n, text))
    for ln in out:
        print('        ' + ln)
    for m in miss:
        print('     !! ' + m)


print('--- option 1 ---')
q(1, 'rest to 25 m/s in 8 s: a and d?', K.job1, ['0', '25', '', '', '8'],
  {'a': 25.0 / 8, 'dist': 0.5 * 25 * 8})
q(2, '30 m/s, brakes at 5 m/s2: how far?', K.job1, ['30', '0', '-5', '', ''],
  {'dist': (0 - 900.0) / (2 * -5), 't': 6.0})
q(3, 'dropped from 45 m', K.job1, ['0', '', 'g', '45', ''],
  {'t': (2 * 45 / G) ** 0.5, 'v': (2 * G * 45) ** 0.5})
q(4, 'thrown up at 25 m/s, how high?', K.job1, ['25', '0', '-g', '', ''],
  {'dist': 25.0 ** 2 / (2 * G), 't': 25.0 / G})
q(5, '40 to 10 m/s over 500 m', K.job1, ['40', '10', '', '500', ''],
  {'a': (100.0 - 1600) / 1000, 't': (10.0 - 40) / ((100.0 - 1600) / 1000)})

print('--- option 2 ---')
q(6, '400 m in 50 s', K.job2, ['0', '400', '50'], {'v': 8.0})
q(7, '0 to 100 km/h in 5 s', K.job2, ['0km/h', '100km/h', '5'],
  {'a': (100 / 3.6) / 5})

print('--- option 3 ---')
q(8, '25 m/s at 35 deg', K.job3, ['25', '35', '', ''],
  {'x': 25 * math.cos(math.radians(35)), 'y': 25 * math.sin(math.radians(35))})
q(9, 'x=-12 y=5', K.job3, ['', '', '12W', '5N'], {'size': 13.0})

print('--- option 4 ---')
q(10, 'swim 1.5 N, current 0.8 E', K.job4, ['1.5', 'N', '0.8', 'E'],
   {'size': (1.5 ** 2 + 0.8 ** 2) ** 0.5, 'x': 0.8, 'y': 1.5})
q(11, 'plane 250 km/h W, wind 60 km/h S', K.job4,
   ['250km/h', 'W', '60km/h', 'S'],
   {'velocity': (250.0 ** 2 + 60 ** 2) ** 0.5, 'x': -250.0, 'y': -60.0})

print('--- option 5 ---')
_vy = 20 * math.sin(math.radians(35)); _vx = 20 * math.cos(math.radians(35))
q(12, 'kicked 20 m/s at 35 deg', K.job5, ['20', '35', ''],
   {'t air': 2 * _vy / G, 't up': _vy / G, 'range': _vx * 2 * _vy / G,
    'peak': _vy ** 2 / (2 * G), 'hit v': 20.0})
_t = (2 * 1.2 / G) ** 0.5
q(13, 'rolls off a 1.2 m table at 3 m/s', K.job5, ['3', '0', '1.2'],
   {'t air': _t, 'range': 3 * _t, 'peak': 1.2,
    'hit v': (9 + 2 * G * 1.2) ** 0.5})

print()
print('EXAM QUESTIONS: 13 asked, FAILURES %d' % bad)
