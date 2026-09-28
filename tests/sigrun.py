"""Run every sig-fig check. Needs CPython (the reference uses Fractions)."""
import sys
sys.path.insert(0, '.')
import siggen as G, siglib as S

a = [l for l in open('q100.txt').read().split('\n') if l]
b = [l for l in open('qhard.txt').read().split('\n') if l]
n = 0
n += G.run('100 normal', a, S)
n += G.run('100 hard (brackets)', b, S)
n += G.run('3000 fuzz normal', G.build(G.simple, 999, 3000), S, show=4)
n += G.run('3000 fuzz hard', G.build(G.hard, 777, 3000), S, show=4)
print()
print('TOTAL WRONG:', n)
