"""Rubbish input must give a short message, never a crash or a hang."""
import explib as E
bad = 0; n = 0

def r(job, args):
    global bad, n
    n += 1
    try:
        out = job(args)
    except Exception as e:
        m = str(e)
        if not m or len(m) > 21:
            bad += 1
            print('  BAD %-24s message no good: %r' % (' , '.join(args), m))
        else:
            print('  ok  %-24s Err: %s' % (' , '.join(args), m))
        return
    for ln in out:
        for x in E.stack(ln):
            if len(x) > 21:
                bad += 1
                print('  BAD %-24s line too wide: %r' % (' , '.join(args), x))
                return
    print('  ok  %-24s -> %s' % (' , '.join(args), ' | '.join(out)))

for s in ['x+1', 'x-1', '(x', 'x)', 'x^', '1/0', 'x/0', 'x^(1/0)', '$',
          'sqrt', 'sqrt(', 'rt(3)', 'rt(1,5)', 'rt(99,5)', 'rt(0,5)',
          '(-4)^(1/2)', '(-8)^(1/4)', '2^(1/999999)', '9^999999999',
          '999999999^999999999', '((((x))))', 'x^^2', '2^(3/0)', '.',
          '5..2', 'x^1.5.5', ')(', '()', 'sqrt(-1)', 'rt(3,-8)',
          '0^0', '0^-1', '0*x', 'xyzabcmn', '2^-0', 'x^(0/5)',
          'sqrt(sqrt(16))', 'rt(2,rt(2,16))', '1/(x-x)']:
    r(E.do1, [s])

r(E.do2, ['5', 'abc'])
r(E.do2, ['5', '3/0'])
r(E.do2, ['', '1/2'])
r(E.do3, ['0', 'x', '2'])
r(E.do3, ['2', 'x', 'abc'])
r(E.do3, ['999', 'x', '2'])
r(E.do4, ['1', '1', '5'])
r(E.do4, ['abc', '2', '5'])
r(E.do4, ['1/0', '2', '5'])
r(E.do5, ['2', '-9'])
r(E.do5, ['20', '1024'])
r(E.do5, ['2', 'x^-3'])
r(E.do5, ['2', '999999999999'])
r(E.do5, ['19', '1/999999999'])

print()
print('ROUGH TOTAL', n, ' PROBLEMS', bad)
