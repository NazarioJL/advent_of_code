from collections import Counter as cntr
from operator import itemgetter as ig

ranks = {rank: val for val, rank in enumerate("23456789TJQKA")}
hand_vals = {v: k for k, v in enumerate([(1, 1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1), (3, 1, 1), (3, 2), (4, 1), (5,)])}

def improve(crds, wcrd):
    ns = tuple(sorted(cntr(val for val in crds if val != wcrd).values(), reverse=True))
    if len(crds) - sum(ns) == 0: return ns
    if len(crds) - sum(ns) == 5: return (5,)
    return ns[0] + len(crds) - sum(ns), *ns[1:]

def hand_val(crds, wcrd=None):
    sig = improve(crds, wcrd) if wcrd is not None else tuple(sorted(cntr(crds).values(), reverse=True))
    return hand_vals[sig]

cbs = {p[0]: int(p[1]) for ln in open("../../../inputs/2023/day07.txt").read().splitlines() if (p := ln.split(maxsplit=1))}
hands_1 = sorted(((cs, (hand_val(hrv), *hrv)) for cs in cbs.keys() if (hrv := tuple(ranks[c] for c in cs))), key=ig(1), reverse=True)
print("Part 1: ", sum((len(cbs) - i) * cbs[crds] for (i, (crds, _)) in enumerate(hands_1)),)
ranks["J"] = -1
hands_2 = sorted(((cards, (hand_val(hrv, wcrd=-1), *hrv)) for cards in cbs.keys() if (hrv := tuple(ranks[card] for card in cards))), key=ig(1), reverse=True)
hands_2.sort(key=ig(1), reverse=True)
print("Part 2: ", sum((len(cbs) - idx) * cbs[cards] for (idx, (cards, _)) in enumerate(hands_2)))
