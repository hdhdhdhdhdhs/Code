# ALGEBRA - solve and simplify, for the Casio fx-9750GIII
#
# One program for three kinds of question. Put all twelve files next to
# each other: algebra.py (run this one) and algcore, algeq1, algeq2,
# algeq3, algrt1, algrt2, algrt3, algrt4, algfr1, algfr2, algfr3 (.py).
# Each part is loaded the first time it is needed, so the calculator
# never compiles too much at once; if memory runs out, every part is put
# away and it tries again.
#
# It asks for one fraction at a time, so no brackets are needed:
#   Top: x       Bottom: x^2-3x-4    + - * / = or EXE: -
#   Top: 4       Bottom: x+1         + - * / = or EXE: (EXE)
# EXE alone for a bottom means 1. After the last fraction, EXE alone
# ends it; = starts the other side of an equation, and =0 (or = and
# anything) finishes it in one go, typed after a bottom too (x-4=0).
# The whole question typed as one top works too. The root key types
# sqrt( ; ^ or ** for powers (x2 means x^2); any letters; powers below
# 0 and halves (x^(1/2)).
#
#   With =        it solves (one letter): Restr (what each root needs),
#                 NPV (values that make a bottom 0), Ans (every answer),
#                 Fails (what squaring added, or a bottom 0), and the
#                 polynomial it squared down to, after multiplying by
#                 the lowest common bottom (as by hand)
#   No =, roots   it simplifies the roots: Restr (what simplifying took
#                 and what each root needs), NPV (a bottom typed is 0),
#                 Ans with no root in a bottom, Entire (a number or
#                 letters in front of a root put under it: 7sqrt(14) is
#                 sqrt(686)), Ans NPV (the answer's bottom is 0 too), the
#                 decimal for numbers, and Times (what it multiplied by)
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
        # = typed in the bottom: what is after it is the other side
        e = ''
        if '=' in b:
            e = b[b.find('='):]
            b = b[:b.find('=')]
        q += o + (t if '=' in t and not b else '((' + t + ')/(' + (b or '1') + '))')
        if e:
            return q + e
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
