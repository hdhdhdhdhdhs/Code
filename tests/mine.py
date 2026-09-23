import explib as E
tot = 0; bad = 0

def t(job, args, want):
    global tot, bad
    tot += 1
    try:
        got = job(args)
    except Exception as e:
        got = ['ERR ' + str(e)]
    g = ' | '.join(got)
    ok = (g == want)
    if not ok: bad += 1
    print('  %s %-32s -> %-28s %s' % ('ok ' if ok else 'BAD', ' , '.join(args),
          g, '' if ok else '(want ' + want + ')'))

print('== my own questions ==')
t(E.do1, ['(x^-3y^2)^-2'], 'x^6/y^4')
t(E.do1, ['(2^3)^(2/3)'], '2^2 | = 4')
t(E.do1, ['(9x^4)^(1/2)'], '3x^2')
t(E.do1, ['(16x^8y^-4)^(3/4)'], '8x^6/y^3')
t(E.do1, ['(a^(1/3))(a^(1/6))'], 'a^(1/2)')
t(E.do1, ['(27/8)^(-2/3)'], '4/9')
t(E.do1, ['(5^-1)(5^-1)'], '1/5^2 | = 1/25')
t(E.do1, ['(3x^2)^0'], '1')
t(E.do1, ['x^5/x^5'], '1')
t(E.do1, ['(-2x)^3'], '-2^3x^3 | = -8x^3')
t(E.do1, ['(x^2y^-1)^-1(xy)^2'], 'y^3')
t(E.do1, ['(8x^6)^(2/3)'], '4x^4')
t(E.do1, ['((2^2)^3)^-1'], '1/2^6 | = 1/64')
t(E.do1, ['(4^(1/2))^3'], '2^3 | = 8')
t(E.do1, ['m^(3/2)n^(1/2)/(m^(1/2)n^(3/2))'], 'm/n')
t(E.do1, ['(2x^2y)^3(3xy^2)^-2'], '2^3x^4/(3^2y) | = 8x^4/(9y)')
t(E.do1, ['(-32x^10)^(1/5)'], '-2x^2')
t(E.do1, ['(x^(2/3))^(3/4)'], 'x^(1/2)')
print('== more radicals of my own ==')
t(E.do5, ['2', '1176'], '14sqrt(6)')
t(E.do5, ['4', '2592'], '6rt(4,2)')
t(E.do5, ['3', '-54'], '-3rt(3,2)')
t(E.do5, ['2', '49'], '7')
t(E.do5, ['2', 'x^7'], 'x^3sqrt(x)')
t(E.do5, ['3', '16x^5'], '2xrt(3,2x^2)')
t(E.do4, ['3', '2', '2'], 'sqrt(18)')
t(E.do4, ['-2', '2', '7'], '-sqrt(28)')
t(E.do4, ['1/3', '3', '81'], 'rt(3,3)')
t(E.do2, ['8', '2/3'], '(rt(3,8))^2 | simp: 4')
t(E.do3, ['4', '81x^8', '2'], '(81x^8)^(1/2) | simp: 9x^4')
print()
print('MINE TOTAL', tot, ' FAILURES', bad)
