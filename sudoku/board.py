from __future__ import annotations


import copy
from itertools import chain
from typing import Iterable, Iterator, List, NamedTuple, Optional, Set, Union


MAX_COORD = 10

Cell = Union[Set[int], int]
BoardData = List[List[Cell]]


def compress_set(values: Set[int]) -> str:
    if not values:
        return ''

    sequence = '{'

    range_start = None
    last = None
    for value in sorted(values):
        if range_start is None:
            range_start = value
        elif value > last + 1:
            if range_start == last:
                sequence += f'{range_start},'
            else:
                sequence += f'{range_start}-{last},'
            range_start = value
        last = value

    # write last value(s)
    if range_start == last:
        sequence += f'{range_start}}}'
    else:
        sequence += f'{range_start}-{last}}}'

    return sequence


class EmptyDomainError(RuntimeError):
    pass


class Coord(NamedTuple):
    x: int
    y: int

    def gen_row(self) -> Iterator[Coord]:
        for x in range(9):
            yield Coord(x, self.y)

    def gen_col(self) -> Iterator[Coord]:
        for y in range(9):
            yield Coord(self.x, y)

    def gen_subregion(self) -> Iterator[Coord]:
        upper_left = Coord(self.x // 3 * 3, self.y // 3 * 3)
        for y in range(3):
            for x in range(3):
                yield Coord(upper_left.x + x, upper_left.y + y)

    def gen_neighbors(self) -> Iterable[Coord]:
        all_coords = chain(self.gen_row(), self.gen_col(),
                           self.gen_subregion())
        return filter(lambda x: x != self, set(all_coords))

    @staticmethod
    def gen_all_coords() -> Iterable[Coord]:
        for y in range(9):
            for x in range(9):
                yield Coord(x, y)


class Board:
    def __init__(self, data: Optional[BoardData] = None):
        self._data: BoardData
        if data is None:
            self._data = [[set(range(1, 10)) for x in range(10)] for y
                          in range(10)]
        else:
            self._data = self._normalize_field(data)

    @classmethod
    def _normalize_field(cls, data: BoardData):
        data = [list(row) for row in data]
        for x, y in Coord.gen_all_coords():
            if not data[y][x]:
                data[y][x] = set(range(1, 10))

        for coord in Coord.gen_all_coords():
            x, y = coord
            value = data[y][x]
            if isinstance(value, int):
                cls._forward_check(data, coord, value)

        return data

    def set_cell(self, coord: Coord, value: int) -> Board:
        new_board = copy.deepcopy(self)

        # raise exception if not in possibilities
        new_board[coord].remove(value)  # type: ignore

        new_board._data[coord.y][coord.x] = value

        self._forward_check(new_board._data, coord, value)

        return new_board

    @staticmethod
    def _forward_check(new_board: BoardData, coord: Coord, value: int):
        for x, y in coord.gen_neighbors():
            possible_values = new_board[y][x]
            try:
                possible_values.discard(value)  # type: ignore
                if not possible_values:
                    raise EmptyDomainError(f"There are no possible values "
                                           f"left for {coord}.")
            except AttributeError:
                # possible_values was not a set
                pass

    def __getitem__(self, key) -> Cell:
        x, y = key
        return self._data[y][x]

    def __repr__(self):
        def process_row(row):
            for val in row:
                try:
                    yield compress_set(val)
                except TypeError:
                    # value is int
                    yield val

        def padded_row(row, pad_amount=16):
            for val in process_row(row):
                yield str(val).ljust(pad_amount)

        return '\n'.join(''.join(padded_row(x)) for x in self._data)

    def gen_all_tiles(self):
        for coord in Coord.gen_all_coords():
            yield coord, self[coord]
