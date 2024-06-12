import pytest

from advent_of_code.grids import Coord2D


def test_coord2d_init():
    coord = Coord2D(1, 2)
    assert coord.x == 1
    assert coord.y == 2


def test_coord2d__add__():
    coord_1 = Coord2D(1, 2)
    coord_2 = Coord2D(10, 20)

    assert coord_1 + coord_2 == Coord2D(11, 22)


def test_coord2d__sub__():
    coord_1 = Coord2D(1, 2)
    assert coord_1 - coord_1 == Coord2D(0, 0)


@pytest.mark.parametrize(
    ("coord_1", "coord_2", "expected"),
    (
        (Coord2D(1, 2), 1,  Coord2D(1, 2)),
        (Coord2D(1, 2), 2,  Coord2D(2, 4)),
        (Coord2D(1, 2), 0,  Coord2D(0, 0)),
    ),
)
def test_coord2d__mul__(coord_1, coord_2, expected: Coord2D):
    coord_1 = Coord2D(1, 2)
    assert (coord_1 * 2) == Coord2D(2, 4)


@pytest.mark.parametrize(
    ("coord_1", "coord_2", "expected"),
    (
        (Coord2D(1, 2), Coord2D(1, 2), True),
        (Coord2D(1, 2), Coord2D(1, 3), False),
        (Coord2D(1, 2), Coord2D(0, 0), False),
    ),
)
def test_coord2d__eq__(coord_1, coord_2, expected):
    assert (coord_1 == coord_2) == expected
