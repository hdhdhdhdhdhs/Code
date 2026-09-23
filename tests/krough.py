"""Rubbish in must give a short message, never a crash or a hang,
and no printed line may be wider than the screen."""
import kinlib as K
n = 0; bad = 0

def r(fn, a):
    global n, bad
    n += 1
    try:
        out = fn(a)
    except Exception as e:
        m = str(e)
        if not m:
            bad += 1; print('  BAD %-28s empty message' % (','.join(a)))
        else:
            print('  ok  %-28s Err: %s' % (','.join(a), m))
        return
    for ln in out:
        if len(ln) > 21:
            bad += 1
            print('  BAD %-28s too wide: %r' % (','.join(a), ln))
            return
    print('  ok  %-28s -> %s' % (','.join(a), ' | '.join(out)))

for a in [['','','','',''], ['x','','2','100',''], ['0','','2','100','-5'],
          ['0','','0','100',''], ['0','0','0','0','0'], ['1e9','','g','',''],
          ['0','','g','999999km',''], ['0','','g','','0'],
          ['..','','2','100',''], ['0','','2','100','1e400'],
          ['0','','g','-10km',''], ['-0','','g','100',''],
          ['0','','2','100','1min30s'], ['0','','2','100s',''],
          ['0','','2','','1h'], ['0','','g','1mm',''],
          ['0','','2','100','5.5.5'], ['+5','','2','100',''],
          ['0','','g','1km','1'], ['5','5','0','','10']]:
    r(K.job1, a)
for a in [['','',''], ['a','b','c'], ['0','10','-5'], ['0','1km/h','1h'],
          ['0km','10m/s','5']]:
    r(K.job2, a)
for a in [['','','',''], ['5','abc','',''], ['0','0','',''],
          ['5','720','',''], ['5','-90','','']]:
    r(K.job3, a)
for a in [['1','0','1','0'], ['0','0','0','0'], ['1e6','45','1e6','225']]:
    r(K.job4, a)
for a in [['','',''], ['30','abc',''], ['30','90',''], ['0','90','0'],
          ['30','-40',''], ['30','40','-100'], ['1e6','45','']]:
    r(K.job5, a)

print()
print('KIN ROUGH', n, ' PROBLEMS', bad)
