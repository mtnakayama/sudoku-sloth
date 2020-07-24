from dataclasses import dataclass
import heapq
import itertools
from typing import cast, List, NamedTuple, Set

from .board import Board, Coord, EmptyDomainError


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def convert_puzzle(text: str):
    """Convert puzzle from a single line of text to a matrix"""
    def to_value(ch: str):
        try:
            return int(ch)
        except ValueError:
            return None

    return grouper(9, map(to_value, text))


class MoveChoice(NamedTuple):
    score: int
    neg_num_neighbors: int
    coord: Coord


def calculate_moves(board: Board) -> List[MoveChoice]:
    moves: List[MoveChoice] = []
    for coord, tile in board.gen_all_tiles():
        try:
            score = len(tile)

            num_neighbors = sum(map(lambda x: int(isinstance(board[x], set)),
                                    coord.gen_neighbors()), 0)

            moves.append(MoveChoice(score, -num_neighbors, coord))
        except TypeError:
            # tile is an int
            pass

    heapq.heapify(moves)

    return moves


def refresh_move_scores(board: Board, moves: List[MoveChoice]) -> int:
    for i, move_opt in enumerate(moves):
        _, neg_num_neighbors, coord = move_opt

        tile = board[coord]
        score = len(cast(Set[int], tile))
        moves[i] = MoveChoice(score, neg_num_neighbors, coord)

    heapq.heapify(moves)
    return moves[0].score


@dataclass
class SolutionStats:
    iteration: int = 0
    next_refresh: int = 0
    min_score: int = 1


def solve(board: Board, next_moves: List[MoveChoice],
          _depth=0, _stats: SolutionStats = None) -> Board:

    if not next_moves:
        return board

    if not _stats:
        _stats = SolutionStats()

    _depth += 1
    _stats.iteration += 1

    if next_moves[0].score > _stats.min_score:
        refresh_move_scores(board, next_moves)

    print(board)
    print(_stats)
    print(heapq.nsmallest(10, next_moves))

    choice = heapq.heappop(next_moves)
    coord = choice.coord

    possible_fills = cast(Set[int], board[coord])
    for fill in possible_fills:
        try:
            return solve(board.set_cell(coord, fill), next_moves,
                         _depth=_depth, _stats=_stats)

        except EmptyDomainError:
            pass

    heapq.heappush(next_moves, choice)

    raise EmptyDomainError(f"No valid moves for {coord} {board[coord]}")


def main():
    # from https://qqwing.com/generate.html
    puzzle = ('.....37...7.....8624....1...6.......41..6..355.2....1..2.5...7.'
              '........385.7...4.')

    puzzle_matrix = convert_puzzle(puzzle)

    board = Board(data=puzzle_matrix)

    board = solve(board, calculate_moves(board))

    print(board)


if __name__ == "__main__":
    main()
