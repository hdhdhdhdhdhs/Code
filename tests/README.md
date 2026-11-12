# Tests

These run against MicroPython, not CPython, because that is what the
calculator runs. Build the importable half of a program first - the
programs end in an input loop that would block - then run a suite:

    python3 -c "s=open('../kin.py').read();open('kinlib.py','w').write(s[:s.index('while True:')])"
    micropython -c "import sys;sys.path.insert(0,'.');exec(open('ktest.py').read())"

The calculator's MicroPython leaves out some built-ins that the usual
builds have: reversed() is confirmed missing on the device. A lean build
(the unix port's minimal variant, with float, math, slices, min/max and
% formatting switched back on) has no reversed, enumerate, set, filter
or str.count; fac.py's output is compared on it as well.

The fuzzers use CPython for speed and check the program's answers against
formulas it does not itself use.

| file | covers |
|---|---|
| ktest.py, krough.py | kin.py: worked questions, then rubbish input |
| kfuzz.py | kin.py: 40000 solves of accelerating motion |
| kfuzz2.py | kin.py: 15000 checks of options 2-5 |
| kfuzz3.py | kin.py: 15000 solves at constant velocity |
| exam.py | kin.py: 13 real exam questions vs independent physics |
| sheet.py, mine.py, more.py | exp.py: 146 questions with known answers |
| fuzz.py, fuzz2.py, radfuzz.py | exp.py: ~65000 random expressions |
| rough.py | exp.py: rubbish input |
| sigrun.py, siggen.py, sigref.py | sigfig_calc.py: 200 questions + 6000 fuzzed, against an exact-fraction reference |
| torture.py, classify.py | sigfig_calc.py: the stress campaign - four checks per expression, and a classifier that sorts every disagreement by root cause |
| ffuzz.py | fac.py: 20000+ polynomials built from known factors - Ans multiplies back, every factor is finished, Slide line and zeros are right, nothing over 21 columns |
| fxy.py | fac.py: 3000 two-letter polynomials against sympy |
| fsym.py | fac.py: random polynomials, factor list compared with sympy's |
| rfuzz.py | rad.py: hard radical equations in 14 kinds (2-4 roots, roots in roots, quadratics under roots, products, powers, tangent and perfect-square cases, fractions and decimals, ^(1/2) and ^0.5) against sympy resultants, exact real zeros and 120-digit checks; every answer must match and nothing may pass 21 columns |
| sfuzz.py | radsimp.py (rad.py with no =): hard simplifying questions in 10 kinds (combining roots, products, one-term and conjugate bottoms, three-root bottoms, letters, letter conjugates, cancelling, roots of sums, mixed) against sympy with positive letters: the Ans must equal the question to 50 digits at random points and be in simplest form (no root in a bottom, square-free radicands, letters to the power 1 under a root, like roots added) |
| q100.txt, qhard.txt | the 100 normal and 100 bracket questions |
| mkverify.py | shared checker for the exp.py suites |
