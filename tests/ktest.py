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
    if not ok: bad += 1
    print('  %s %-30s -> %s' % ('ok ' if ok else 'BAD', ' , '.join(a), got))
    if not ok: print('       want -> %s' % want)

print('== uniform acceleration ==')
t(K.job1, ['0','','2','100',''], 'v = 20 m/s |   = 72 km/h |   via v=v0+at | t = 10 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','10km',''], 'v = 442.7 m/s |   = 1594 km/h |   via v=v0+at | t = 45.18 s |   via d=v0t+at2/2')
t(K.job1, ['72km/h','0','','','5'], 'a = -4 m/s2 |   via v=v0+at | d = 50 m |   via d=v0t+at2/2')
t(K.job1, ['20','','-g','15',''], '2 answers: | A v=10.3 t=0.9902 | B v=-10.3 t=3.091 | via d=v0t+at2/2 | via v=v0+at')
t(K.job1, ['0','','-g','','3'], 'v = -29.4 m/s |   = -105.8 km/h |   via v=v0+at | d = -44.1 m |   via d=v0t+at2/2')
t(K.job1, ['10','30','','100',''], 'a = 4 m/s2 |   via v2=v02+2ad | t = 5 s |   via v=v0+at')
t(K.job1, ['','','2','','5'], 'Err: need 3 numbers')
t(K.job1, ['0','10','5','100','2'], 'all 5 given | does NOT fit')
t(K.job1, ['0','10','5','10','2'], 'all 5 given | it fits')
t(K.job1, ['20','0','-g','100',''], 'Err: no answer fits')

print('== units ==')
t(K.job1, ['0','','g','1km',''], 'v = 140 m/s |   = 504 km/h |   via v=v0+at | t = 14.29 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','','1min'], 'v = 588 m/s |   = 2117 km/h |   via v=v0+at | d = 17640 m |   = 17.64 km |   via d=v0t+at2/2')
t(K.job1, ['0','','g','100cm',''], 'v = 4.427 m/s |   via v=v0+at | t = 0.4518 s |   via d=v0t+at2/2')
t(K.job1, ['0','','g','5mm',''], 'v = 0.313 m/s |   via v=v0+at | t = 0.03194 s |   via d=v0t+at2/2')
t(K.job1, ['0','','2','100','xyz'], 'Err: need a number')
t(K.job1, ['0','','2','100','5xyz'], 'Err: bad unit xyz')
t(K.job1, ['0','','2','100km/h',''], 'Err: bad unit km/h')

print('== rate ==')
t(K.job2, ['0','90km','1.5h'], 'v = 16.67 m/s |   = 60 km/h | change 90 km | over 1.5 h')
t(K.job2, ['0km/h','60km/h','8'], 'a = 2.083 m/s2 | change 60 km/h | over 8 s')
t(K.job2, ['5','25','4'], 'v = 5 m/s | change 20 m | over 4 s')
t(K.job2, ['0','10','0'], 'Err: time is 0')

print('== vectors ==')
t(K.job3, ['50','30','',''], 'x = 43.3 | y = 25')
t(K.job3, ['','','3','4'], 'size = 5 | angle = 53.13 deg | 36.87 E of N')
t(K.job3, ['','','-3','-4'], 'size = 5 | angle = 233.1 deg | 36.87 W of S')
t(K.job3, ['10','90','',''], 'x = 0 | y = 10')
t(K.job3, ['','','','5'], 'Err: give size+angle or x+y')
t(K.job4, ['3','0','4','90'], 'size = 5 | angle = 53.13 deg | 36.87 E of N | x = 3 | y = 4')
t(K.job4, ['10','0','10','180'], 'size = 0 | no direction | they cancel out')
t(K.job3, ['','','0','0'], 'size = 0 | no direction')
t(K.job4, ['5','30','',''], 'Err: need all 4')

t(K.job3, ['','','30E','10S'], 'size = 31.62 | angle = 341.6 deg | 18.43 S of E')
t(K.job4, ['30','E','10','S'], 'size = 31.62 | angle = 341.6 deg | 18.43 S of E | x = 30 | y = -10')
t(K.job4, ['5','NE','5','SE'], 'size = 7.071 | angle = 0 deg | due E | x = 7.071 | y = 0')
t(K.job3, ['10','S30W','',''], 'x = -5 | y = -8.66')
t(K.job3, ['','','0','5'], 'size = 5 | angle = 90 deg | due N')
print('== projectile ==')
t(K.job5, ['30','40',''], 't air = 3.935 s | range = 90.44 m | peak = 18.97 m | hit v = 30 m/s')
t(K.job5, ['12','0','45'], 't air = 3.03 s | range = 36.37 m | peak = 45 m | hit v = 32.03 m/s')
t(K.job5, ['0','0','20'], 't air = 2.02 s | range = 0 m | peak = 20 m | hit v = 19.8 m/s')
t(K.job5, ['20','45',''], 't air = 2.886 s | range = 40.82 m | peak = 10.2 m | hit v = 20 m/s')
t(K.job5, ['','40',''], 'Err: need a speed')

print()
print('KIN TOTAL', tot, ' FAILURES', bad)
