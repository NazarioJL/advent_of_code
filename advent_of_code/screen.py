from enum import auto
from enum import Enum


class ScreenOrigin(Enum):
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()


class Screen:
    def _get_marker(self, n: int) -> str:
        if n >= len(self._line_markers):
            return "-"
        else:
            return self._line_markers[abs(n)]

    def __init__(
        self,
        start_x: int = 0,
        start_y: int = 0,
        end_x: int = 20,
        end_y: int = 20,
        add_nums: bool = True,
        screen_origin: ScreenOrigin = ScreenOrigin.TOP_LEFT,
        default_pixel: str = ".",
        line_markers: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        title: str | None = "==== Virtual Screen ====",
    ):
        self._start_x = start_x
        self._start_y = start_y
        self._end_x = end_x
        self._end_y = end_y
        self._add_nums = add_nums
        self._screen_origin = screen_origin
        self._default_pixel = default_pixel
        self._line_markers = line_markers
        self._title = title

        self._buffer: dict[tuple[int, int], str] = {}

    def draw(self, s: str, x: int, y: int) -> str | None:
        if x < self._start_x or x >= self._end_x:
            return None
        if y < self._start_y or y >= self._end_y:
            return None
        self._buffer[(x, y)] = s
        return s

    def clear(self) -> None:
        self._buffer.clear()

    def render(self) -> None:
        if self._screen_origin == ScreenOrigin.TOP_LEFT:
            rows = range(self._start_y, self._end_y)
        elif self._screen_origin == ScreenOrigin.BOTTOM_LEFT:
            rows = reversed(range(self._start_y, self._end_y))  # type: ignore
        else:
            raise ValueError(
                f"Cannot understand screen origin option: {self._screen_origin}"
            )

        if self._title:
            print(self._title)

        if self._add_nums:
            hor_markers = "".join(
                self._get_marker(x) for x in range(self._start_x, self._end_x)
            )
            print(f" {hor_markers} ")
        for row in rows:
            line = []
            if self._add_nums:
                line.append(self._get_marker(row))
            for col in range(self._start_x, self._end_x):
                line.append(self._buffer.get((col, row), self._default_pixel))
            if self._add_nums:
                line.append(self._get_marker(row))
            print("".join(line))
        if self._add_nums:
            hor_markers = "".join(
                self._get_marker(x) for x in range(self._start_x, self._end_x)
            )
            print(f" {hor_markers} ")
