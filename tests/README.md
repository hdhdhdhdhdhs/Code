# Tests

These run against MicroPython, not CPython, because that is what the
calculator runs. Build the importable half of a program first - the
programs end in an input loop that would block - then run a suite:

    python3 -c "s=open('../kin.py').read();open('kinlib.py','w').write(s[:s.index('while True:')])"
    micropython -c "import sys;sys.path.insert(0,'.');exec(open('ktest.py').read())"

The fuzzers use CPython for speed and check the program's answers against
formulas it does not itself use.

| file | covers |
|---|---|
| ktest.py, krough.py | kin.py: worked questions, then rubbish input |
| kfuzz.py | kin.py: 40000 solves of accelerating motion |
| kfuzz2.py | kin.py: 15000 checks of options 2-5 |
| kfuzz3.py | kin.py: 15000 solves at constant velocity |
| sheet.py, mine.py, more.py | exp.py: 146 questions with known answers |
| fuzz.py, fuzz2.py, radfuzz.py | exp.py: ~65000 random expressions |
| rough.py | exp.py: rubbish input |
| mkverify.py | shared checker for the exp.py suites |
