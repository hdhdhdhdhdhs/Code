# ALGEBRA - solve and simplify, for the Casio fx-9750GIII
#
# One program for three kinds of question. Put all nine files next to
# each other: algebra.py (run this one) and algcore, algeq1, algeq2,
# algeq3, algrt1, algrt2, algfr1, algfr2 (.py). Each part is loaded the
# first time it is needed, so the calculator never compiles too much at
# once.
#
# It asks for one fraction at a time, so no brackets are needed:
#   Top: x       Bottom: x^2-3x-4    + - * / = or EXE: -
#   Top: 4       Bottom: x+1         + - * / = or EXE: (EXE)
# EXE alone for a bottom means 1. After the last fraction, EXE alone
# ends it; = starts the other side of an equation, and =0 (or = and
# anything) finishes it in one go. The whole question typed as one top
# works too. The root key types sqrt( ; ^ or ** for powers (x2 means
# x^2); any letters; powers below 0 and halves (x^(1/2)).
#
#   With =        it solves (one letter): Restr (what each root needs),
#                 NPV (values that make a bottom 0), Ans (every answer),
#                 Fails (what squaring added, or a bottom 0), and the
#                 polynomial it squared down to
#   No =, roots   it simplifies the roots: Restr, NPV, Ans, the decimal
#                 for numbers, and Times (what it multiplied by)
#   No =, others  it simplifies fractions (numbers or letters): Ans with
#                 the top multiplied out and the bottom factored, NPV
from algcore import go, wrap, st


def ask(t):
    # one fraction at a time: top, bottom (EXE alone for 1), then + - * /
    # or = for more, =0 to finish an equation, or EXE to end
    q = ''
    o = ''
    while True:
        t = t or input('Top:').strip()
        if not t:
            return q
        b = input('Bottom:').strip()
        q += o + (t if '=' in t and not b else '((' + t + ')/(' + (b or '1') + '))')
        t = ''
        o = '?'
        while o not in ('', '+', '-', '*', '/') and o[:1] != '=':
            o = input('+ - * / = or EXE:').strip()
        if len(o) > 1:
            return q + o
        if not o:
            return q


print('Algebra: solve with =\nor simplify. Type a\ntop and a bottom,\nthen + - * / = or EXE')
s = ''
while True:
    try:
        s = ask(s)
    except (KeyboardInterrupt, EOFError):
        break
    if s == '':
        continue
    try:
        out = go(s)
    except Exception as e:
        out = ['Err: ' + (str(e) or 'bad input')]
    s = ''
    ls = []
    for ln in out:
        ls += wrap(st(ln))
    try:
        for i in range(len(ls)):
            # typing a top at more.. skips the rest and starts on it
            if i and i % 6 == 0:
                s = input('more..').strip()
                if s:
                    break
            print(ls[i])
    except (KeyboardInterrupt, EOFError):
        break
