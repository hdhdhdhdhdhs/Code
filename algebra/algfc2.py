# ALGFC2 - every zero of a polynomial worked out as a decimal (Durand-
# Kerner), for the Zeros line of factoring (see algfc.py)
import math


def units(c):
    # every zero found numerically, real ones alone and the rest in
    # conjugate pairs, each as a small real polynomial
    n = len(c) - 1
    # scale x = S*t so every zero has |t| <= 2: keeps the numbers small
    # enough for a calculator that works in single precision
    S = 0.0
    for k in range(n):
        S = max(S, (abs(c[k]) / abs(c[-1])) ** (1.0 / (n - k)))
    S = S or 1.0
    a = [c[k] / c[-1] / S ** (n - k) for k in range(n + 1)]
    z = []
    for k in range(n):
        t = 6.2832 * k / n + 0.4
        z.append([math.cos(t), math.sin(t)])
    w = 0
    for it in range(500):
        mv = 0
        for i in range(n):
            zr, zi = z[i]
            pr, pi = 1.0, 0.0
            for k in range(n - 1, -1, -1):
                pr, pi = pr * zr - pi * zi + a[k], pr * zi + pi * zr
            dr, di = 1.0, 0.0
            for j in range(n):
                if j != i:
                    er = zr - z[j][0]
                    ei = zi - z[j][1]
                    dr, di = dr * er - di * ei, dr * ei + di * er
            m = dr * dr + di * di or 1e-30
            qr = (pr * dr + pi * di) / m
            qi = (pi * dr - pr * di) / m
            z[i] = [zr - qr, zi - qi]
            mv = max(mv, abs(qr) + abs(qi))
        # it closes in fast once near: a few more passes reach full precision
        if mv < 1e-5:
            w += 1
        if mv < 1e-14 or w > 4:
            break
    for p in z:
        if not abs(p[0]) + abs(p[1]) < 10:
            return []
        p[0] *= S
        p[1] *= S
    u = []
    ok = [1] * n
    for i in range(n):
        if not ok[i]:
            continue
        ok[i] = 0
        zr, zi = z[i]
        if abs(zi) < 1e-6 * (1 + abs(zr)):
            u.append((1, [-zr, 1.0]))
            continue
        b = i
        bd = 1e300
        for j in range(n):
            d = abs(z[j][0] - zr) + abs(z[j][1] + zi)
            if ok[j] and d < bd:
                b = j
                bd = d
        ok[b] = 0
        zr = (zr + z[b][0]) / 2
        zi = (abs(zi) + abs(z[b][1])) / 2
        u.append((2, [zr * zr + zi * zi, -2 * zr, 1.0]))
    return u
