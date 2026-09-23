import kinlib as K
tot = 0; bad = 0

def t(fn, a, want):
    global tot, bad
    tot += 1
    try:
        got = ' | '.join(fn(a))
    except Exception as e:
        got = 'Err: ' + (str(e) or '?')
    ok = (got == want)
    for ln in got.split(' | '):
        if len(ln) > 21:
            ok = False
            print('       TOO WIDE: %r' % ln)
    if not ok: bad += 1
    print('  %s %-30s -> %s' % ('ok ' if ok else 'BAD', ' , '.join(a), got))
    if not ok: print('       want -> %s' % want)

print('== uniform acceleration ==')
t(K.job1, ['0','','2','100',''], 'v = 20 m/s |   via v=v0+at | t = 10 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','10km',''], 'v = 442.7 m/s |   via v=v0+at | t = 45.18 s |   via d=v0t+at2/2')
t(K.job1, ['72km/h','0','','','5'], 'a = -4 m/s2 |   via v=v0+at | dist = 50 m |   via d=v0t+at2/2')
t(K.job1, ['20','','-g','15',''], '2 answers: | A v=10.3 t=0.9902 | B v=-10.3 t=3.091 | via d=v0t+at2/2 | via v=v0+at')
t(K.job1, ['0','','-g','','3'], 'v = -29.4 m/s |   via v=v0+at | dist = -44.1 m |   via d=v0t+at2/2')
t(K.job1, ['10','30','','100',''], 'a = 4 m/s2 |   via v2=v02+2ad | t = 5 s |   via v=v0+at')
t(K.job1, ['','','2','','5'], 'Err: need 3 numbers')
t(K.job1, ['0','10','5','100','2'], 'all 5 given | does NOT fit')
t(K.job1, ['0','10','5','10','2'], 'all 5 given | it fits')
t(K.job1, ['20','0','-g','100',''], 'Err: no answer fits')

print('== units ==')
t(K.job1, ['0','','g','1km',''], 'v = 140 m/s |   via v=v0+at | t = 14.29 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','','1min'], 'v = 588 m/s |   via v=v0+at | dist = 17640 m |   = 17.64 km |   via d=v0t+at2/2')
t(K.job1, ['0','','g','100cm',''], 'v = 4.427 m/s |   via v=v0+at | t = 0.4518 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','5mm',''], 'v = 0.313 m/s |   via v=v0+at | t = 0.03194 s |   via d=v0t+at2/2')
t(K.job1, ['0','','2','100','xyz'], 'Err: need a number')
t(K.job1, ['0','','2','100','5xyz'], 'Err: bad unit xyz')
t(K.job1, ['0','','2','100km/h',''], 'Err: bad unit km/h')

print('== rate ==')
t(K.job2, ['0','90km','1.5h'], 'v = 16.67 m/s |   = 60 km/h')
t(K.job2, ['0km/h','60km/h','8'], 'a = 2.083 m/s2')
t(K.job2, ['5','25','4'], 'v = 5 m/s')
t(K.job2, ['0','10','0'], 'Err: time is 0')

print('== vectors ==')
t(K.job3, ['50','30','',''], 'x = 43.3 | y = 25')
t(K.job3, ['','','3','4'], 'size = 5 | 36.87 E of N')
t(K.job3, ['','','-3','-4'], 'size = 5 | 36.87 W of S')
t(K.job3, ['10','90','',''], 'x = 0 | y = 10')
t(K.job3, ['','','','5'], 'Err: size+ang or x,y')
t(K.job4, ['3','0','4','90'], 'size = 5 | 36.87 E of N | x = 3 | y = 4')
t(K.job4, ['10','0','10','180'], 'size = 0 | no direction | they cancel out')
t(K.job3, ['','','0','0'], 'size = 0 | no direction')
t(K.job4, ['5','30','',''], 'Err: need all 4')

t(K.job3, ['','','30E','10S'], 'size = 31.62 | 18.43 S of E')
t(K.job4, ['30','E','10','S'], 'size = 31.62 | 18.43 S of E | x = 30 | y = -10')
t(K.job4, ['5','NE','5','SE'], 'size = 7.071 | due E | x = 7.071 | y = 0')
t(K.job3, ['10','S30W','',''], 'x = -5 | y = -8.66')
t(K.job3, ['','','0','5'], 'size = 5 | due N')
t(K.job4, ['30km/h','E','10km/h','S'], 'velocity = 31.62 km/h | 18.43 S of E | x = 30 km/h | y = -10 km/h')
t(K.job4, ['30km/h','E','5m/s','S'], 'velocity = 34.99 km/h | 30.96 S of E | x = 30 km/h | y = -18 km/h')
t(K.job3, ['','','30km/hE','10km/hS'], 'velocity = 31.62 km/h | 18.43 S of E')
t(K.job3, ['50mph','30','',''], 'x = 43.3 mph | y = 25 mph')
t(K.job3, ['100','S30W','',''], 'x = -50 | y = -86.6')
t(K.job4, ['30km','E','10km','S'], 'displacement | 31.62 km | 18.43 S of E | x = 30 km | y = -10 km')
t(K.job3, ['','','3m/s2','4m/s2'], 'acceleration = 5 m/s2 | 36.87 E of N')
t(K.job4, ['3m/s2','E','4m/s2','N'], 'acceleration = 5 m/s2 | 36.87 E of N | x = 3 m/s2 | y = 4 m/s2')
t(K.job4, ['2g','N','2g','S'], 'size = 0 | no direction | they cancel out')
t(K.job3, ['20m/s2','SW','',''], 'x = -14.14 m/s2 | y = -14.14 m/s2')
t(K.job1, ['0','','g','','1h'], 'v = 35280 m/s |   = 127008 km/h |   via v=v0+at | dist = 63504000 m |   = 63504 km |   via d=v0t+at2/2')
t(K.job4, ['4','3m/s','sw','4m/s'], 'Err: dir: E N W S')
t(K.job4, ['sw','4','nw','3'], 'Err: size: a number')
t(K.job4, ['3m/s**2','SW','4m/s**2','NW'], 'acceleration = 5 m/s2 | 8.13 N of W | x = -4.95 m/s2 | y = 0.7071 m/s2')
t(K.job4, ['3mss','SW','4m/s^2','NW'], 'acceleration = 5 m/s2 | 8.13 N of W | x = -4.95 m/s2 | y = 0.7071 m/s2')
t(K.job4, ['30kmh','E','40km/hr','N'], 'velocity = 50 km/h | 36.87 E of N | x = 30 km/h | y = 40 km/h')
t(K.job3, ['5','xyz','',''], 'Err: dir: E N W S')
print('== projectile ==')
t(K.job5, ['30','40',''], 't air = 3.935 s | t up = 1.968 s | range = 90.44 m | peak = 18.97 m | hit v = 30 m/s')
t(K.job5, ['12','0','45'], 't air = 3.03 s | t up = 0 s | range = 36.37 m | peak = 45 m | hit v = 32.03 m/s')
t(K.job5, ['0','0','20'], 't air = 2.02 s | t up = 0 s | range = 0 m | peak = 20 m | hit v = 19.8 m/s')
t(K.job5, ['20','45',''], 't air = 2.886 s | t up = 1.443 s | range = 40.82 m | peak = 10.2 m | hit v = 20 m/s')
t(K.job5, ['','40',''], 'Err: need a speed')

print()
print('KIN TOTAL', tot, ' FAILURES', bad)
