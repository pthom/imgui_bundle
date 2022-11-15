# transform a list into a list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c]]
def overlapping_pairs(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b

# transform a list into a circular list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c], [c, a]]
def overlapping_pairs_cyclic(iterable):
    it = iter(iterable)
    a = next(it, None)
    first = a
    for b in it:
        yield (a, b)
        a = b
    last = a
    yield(last, first)
