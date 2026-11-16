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
| rfuzz.py | rad.py: hard radical equations in 16 kinds (2-4 roots, roots in roots, quadratics under roots, products, powers, tangent and perfect-square cases, fractions and decimals, ^(1/2) and ^0.5, the letter in a bottom) against sympy resultants, exact real zeros and 120-digit checks; every answer must match and nothing may pass 21 columns |
| sfuzz.py | radsimp.py (rad.py with no =): hard simplifying questions in 13 kinds (combining roots, products, one-term and conjugate bottoms, three-root bottoms, letters, letter conjugates, cancelling, roots of sums, mixed, sums sharing a factor, squares of sums, roots in roots that undo) against sympy with positive letters: the Ans must equal the question to 50 digits at random points and be in simplest form (no root in a bottom, square-free radicands, letters to the power 1 under a root, nothing shared or square left under a root of a sum, nothing sympy can denest, like roots added) |
| consist.py | rad.py against itself: an answer typed back gives itself, (question)-(answer) is 0, the same question typed other ways (** for ^, * put in, spaces, capitals, math.sqrt, ^0.5, letters renamed, sums reordered, sides swapped, multiplied through) gives the same answer, and fraction answers put back in give exactly 0 |
| crash.py | rad.py against random typing and junk: never a Python error leaking through, never over 5 seconds, never a line over 21 columns |
| frfuzz.py | frac.py: rational expressions in 14 kinds (cancel, times, divide, add, complex fractions, negative powers, two letters, grouping, big, pieces with no zero p/q, fraction numbers, many letters, nested, powers of fractions) built from known factors: Ans and Fac equal the question exactly at random fraction points, Ans is in lowest terms and Fac fully factored (sympy), and the NPVs are exactly the zeros of every bottom typed |
| fcheck.py | frac.py against itself and junk: Ans and Fac typed back give the same Ans, (question)-(Ans) is 0, ** / * / spaces / capitals give the same screen, and random typing never leaks a Python error, takes over 5 seconds or passes 21 columns |
| acompare.py | algebra/ (the combined program) against rad.py, radsimp.py and frac.py: the same screen for questions of every kind those checkers make, but for the new lines (NPV for equations and roots, Restr pieces for roots), a root-free answer cancelled and factored as frac.py does, and an answer that changed only where it must equal the old one at numbers put in |
| anpv.py | algebra/'s NPV lines (equations and simplifying with roots) against the zeros of every bottom typed, found by sympy resultants and checked to 150 digits; its Ans NPV line against the zeros of the answer's bottoms that are not NPVs; and its Restr pieces when simplifying, each against what one root typed needs |
| anpvm.py | algebra/'s NPV, Ans NPV and Restr lines when simplifying with roots and two or more letters, at numbers put in: every zero of a bottom typed (with its roots defined) meets an NPV piece and every zero of one of the answer's an NPV or Ans NPV piece, every piece names zeros of such a bottom, where every Restr piece holds each root typed is defined, and each piece is a letter >= 0 or a radicand typed |
| alcd.py | algebra/'s equations whose bottoms share a factor, against sympy: every real answer found, and Fails exactly what fails by hand over the lowest common bottom |
| afac.py | algebra/'s Fac line against sympy: polynomials (one or two letters, with the factoring steps) and whole numbers, multiplied back out to the answer and factored all the way (the same factors as sympy's factor_list), and the Zeros line every real zero |
| acheck.py | algebra/ against itself and junk: an answer typed back gives itself, (question)-(answer) is 0, ** / capitals / spaces / Top and Bottom pieces give the same answer, and random typing never leaks a Python error, takes over 5 seconds or passes 21 columns |
| rfuzz.py, sfuzz.py, frfuzz.py on algebra/ | the same three checkers pointed at the combined program (`python3 rfuzz.py ../algebra`, `python3 sfuzz.py ../algebra`, `SRC=../algebra python3 frfuzz.py`); sfuzz.py then adds a 14th kind, a fraction inside a bottom (1/(1+1/sqrt(x)), (1/sqrt(x)-1/sqrt(y))/(1/x-1/y)) |
| q100.txt, qhard.txt | the 100 normal and 100 bracket questions |
| mkverify.py | shared checker for the exp.py suites |
