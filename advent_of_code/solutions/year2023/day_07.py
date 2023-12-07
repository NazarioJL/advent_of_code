from collections import Counter
from operator import itemgetter

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 7

CardRankValues = tuple[int, ...]
HandSignature = tuple[int, ...]

CARDS_RANKS = {rank: val for val, rank in enumerate("23456789TJQKA")}

# Map hands to relative value
HAND_VALUES_MAP = {
    (1, 1, 1, 1, 1): 1,  # High card
    (2, 1, 1, 1): 2,  # One pair
    (2, 2, 1): 3,  # Two pairs
    (3, 1, 1): 4,  # Three of a kind
    (3, 2): 5,  # Full house
    (4, 1): 6,  # Four of a kind
    (5,): 7,  # Five of a kind
}

# Could probably just add the J wildcard count to the most common
HAND_IMPROVEMENTS_MAPS = {
    # 1 Joker
    (4,): (5,),
    (3, 1): (4, 1),
    (2, 2): (3, 2),
    (2, 1, 1): (3, 1, 1),
    (1, 1, 1, 1): (2, 1, 1, 1),
    # 2 Jokers
    (3,): (5,),
    (2, 1): (4, 1),
    (1, 1, 1): (3, 1, 1),
    # 3 Jokers
    (2,): (5,),
    (1, 1): (4, 1),
    # 4 Jokers
    (1,): (5,),
    # 5 Jokers
    (): (5,),
}


def rank_values(cards: str) -> CardRankValues:
    """Convert a hand to its relative rank values"""
    return tuple(CARDS_RANKS[card] for card in cards)


def hand_signature(cards: CardRankValues) -> HandSignature:
    """
    Convert a set to its signature, which is a descending ordered tuple of counts of
    each unique card in the set of cards.

    Since only cardinality of each unique symbol matters, we can uniquely identify each
    hand by the count of each unique item in a set of cards.

    E.g.
        '11223' == 'TTJJQ' since both have signatures of: 2,2,1 (2 pairs)
    """
    return tuple(sorted(Counter(cards).values(), reverse=True))


def improve_hand_1(cards: CardRankValues, wildcard: int) -> HandSignature:
    new_signature = hand_signature(
        # Filter out wildcards
        tuple(val for val in cards if val != wildcard)
    )

    return (
        new_signature
        if sum(new_signature) == 5
        else HAND_IMPROVEMENTS_MAPS[new_signature]
    )


def improve_hand_2(cards: CardRankValues, wildcard: int) -> HandSignature:
    new_signature = hand_signature(
        # Filter out Joker wildcards
        tuple(val for val in cards if val != wildcard)
    )
    total_wildcards = len(cards) - sum(new_signature)

    if total_wildcards == 0:
        # nothing to improve
        return new_signature
    if total_wildcards == 5:
        return (5,)

    first, *rest = new_signature
    # To improve just add count of wildcards to most common card
    return first + total_wildcards, *rest


def hand_value(cards: CardRankValues, wildcard: int | None = None) -> int:
    signature = (
        improve_hand_2(cards, wildcard)
        if wildcard is not None
        else hand_signature(cards)
    )
    return HAND_VALUES_MAP[signature]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    card_bids = {
        parts[0]: int(parts[1])
        for line in s.splitlines()
        if (parts := line.split(maxsplit=1))
    }

    total_hands = len(card_bids)

    # Part 1
    hands_1 = [
        (cards, (hand_value(hrv), *hrv))
        for cards in card_bids.keys()
        if (hrv := rank_values(cards))
    ]
    hands_1.sort(key=itemgetter(1), reverse=True)

    part_1 = sum(
        (total_hands - idx) * card_bids[cards]
        for (idx, (cards, _)) in enumerate(hands_1)
    )

    # Part 2

    # In Part2 J has the least relative value, let's patch it
    NEW_WILDCARD_VALUE = -1
    CARDS_RANKS["J"] = NEW_WILDCARD_VALUE

    hands_2 = [
        (cards, (hand_value(hrv, wildcard=NEW_WILDCARD_VALUE), *hrv))
        for cards in card_bids.keys()
        if (hrv := rank_values(cards))
    ]

    hands_2.sort(key=itemgetter(1), reverse=True)

    part_2 = sum(
        (total_hands - idx) * card_bids[cards]
        for (idx, (cards, _)) in enumerate(hands_2)
    )

    return part_1, part_2


TEST_INPUT = """\
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (6440, 5905)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
