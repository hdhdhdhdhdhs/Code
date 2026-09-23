import explib as E

tot = 0
bad = 0

def t(job, args, want):
    global tot, bad
    tot += 1
    try:
        got = job(args)
    except Exception as e:
        got = ['ERR ' + str(e)]
    g = ' | '.join(got)
    ok = (got[0] == want)
    if not ok:
        bad += 1
    print('  %s %-30s -> %-26s %s' % ('ok ' if ok else 'BAD',
          ' , '.join(args), g, '' if ok else '(want ' + want + ')'))

print('== PART 1 Q1  write with positive exponents ==')
t(E.do1, ['c^-4'], '1/c^4')
t(E.do1, ['mn^-2'], 'm/n^2')
t(E.do1, ['3x^-3'], '3/x^3')
t(E.do1, ['4m^3n^-2'], '4m^3/n^2')
t(E.do1, ['-2x^-4'], '-2/x^4')
t(E.do1, ['-5x^-3y^-2'], '-5/(x^3y^2)')

print('== PART 1 Q2  simplify ==')
t(E.do1, ['(2^-2)(2^3)'], '2')
t(E.do1, ['(3^0)(3^-3)'], '1/3^3')
t(E.do1, ['5^3/5^-4'], '5^7')
t(E.do1, ['(3^-7)(4)/((3^9)(4^3))'], '1/(3^16*4^2)')
t(E.do1, ['(2^4)^3'], '2^12')
t(E.do1, ['(3^2)^-4'], '1/3^8')
t(E.do1, ['[(4)(2^-3)]^-2'], '2^6/4^2')
t(E.do1, ['(6^2/5^-3)^-3'], '1/(6^6*5^9)')

print('== PART 1 Q3  simplify ==')
t(E.do1, ['(2xy^2)(3x^-1y^0)'], '6y^2')
t(E.do1, ['(-3m^2n)(-4m^4n^-2)'], '12m^6/n')
t(E.do1, ['m^3n^-2/((mn^4)(m^5n^2))'], '1/(m^3n^8)')

print('== PART 2 Q1  exponent laws ==')
t(E.do1, ['(x^(1/2))(x^(7/2))'], 'x^4')
t(E.do1, ['(3m^4)(m^(1/4))'], '3m^(17/4)')
t(E.do1, ['[(x^1.5)(x^2.5)]^0.5'], 'x^2')
t(E.do1, ['(5x^3/(20x))^(1/2)'], 'x/2')

print('== PART 2 Q2  simplify, positive exponents ==')
t(E.do1, ['(y^-2)(y^(5/2))'], 'y^(1/2)')
t(E.do1, ['(-8x^-6)^(1/3)'], '-2/x^2')
t(E.do1, ['(x^3)^(1/2)/(x^(5/2))^(1/5)'], 'x')
t(E.do1, ['(x^(1/4)/(16x^(3/4)))^(1/2)'], '1/(4x^(1/4))')

print('== PART 3 Q1  power -> radical ==')
t(E.do2, ['5', '3/2'], '(sqrt(5))^3')
t(E.do2, ['27^2', '2/3'], '(rt(3,27^2))^2')
t(E.do2, ['4x^3', '0.5'], 'sqrt(4x^3)')
t(E.do2, ['x^4/y^2', '-3/2'], '1/(sqrt(x^4/y^2))^3')
t(E.do2, ['x^6y', '1/3'], 'rt(3,x^6y)')

print('== PART 3 Q2  radical -> power ==')
t(E.do3, ['2', '9x', '3'], '(9x)^(3/2)')
t(E.do3, ['2', '4x^2', '3'], '(4x^2)^(3/2)')
t(E.do3, ['3', '64x^6', ''], '(64x^6)^(1/3)')

print('== PART 3 Q3  mixed -> entire ==')
t(E.do4, ['5', '2', '3'], 'sqrt(75)')
t(E.do4, ['2/5', '2', '10'], 'sqrt(8/5)')
t(E.do4, ['2', '3', '4'], 'rt(3,32)')
t(E.do4, ['-4', '3', '2'], 'rt(3,-128)')
t(E.do4, ['5', '3', '3'], 'rt(3,375)')

print('== PART 3 Q4  entire -> mixed ==')
t(E.do5, ['2', '180'], '6sqrt(5)')
t(E.do5, ['2', '108'], '6sqrt(3)')
t(E.do5, ['3', '750'], '5rt(3,6)')
t(E.do5, ['3', '81'], '3rt(3,3)')
t(E.do5, ['2', '486'], '9sqrt(6)')

print()
print('SHEET TOTAL', tot, ' FAILURES', bad)
