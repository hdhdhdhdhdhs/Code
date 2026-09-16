# MEM - how much Python memory does this calculator have?
# Run this, then tell Claude the numbers.

try:
    import gc
    gc.collect()
    print('free :', gc.mem_free())
    print('used :', gc.mem_alloc())
except Exception:
    print('no gc module')

# fallback: grow a list until it dies, to find the ceiling
n = 0
blocks = []
try:
    while True:
        blocks.append(bytearray(1024))
        n += 1
        if n > 400:
            break
except Exception:
    pass
print('grabbed', n, 'KB')
blocks = None
input('EXE=end')
