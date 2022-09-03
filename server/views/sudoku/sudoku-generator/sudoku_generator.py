# !/usr/bin/python

# original author: https://github.com/RutledgePaulV

from argparse import ArgumentParser
from enum import Enum
from Sudoku.Generator import *

# setting difficulties and their cutoffs for each solve method
difficulties = {
    'easy': (35, 0), 
    'medium': (81, 5), 
    'hard': (81, 10), 
    'extreme': (81, 15)
}

class SudokuDifficulty(Enum):
    EASY        ="easy"
    MEDIUM      ="medium"
    HARD        ="hard"
    EXTREME     ="extreme"

base_str="""1 2 3 4 5 6 7 8 9
4 5 6 7 8 9 1 2 3
7 8 9 1 2 3 4 5 6
2 1 4 3 6 5 8 9 7
3 6 5 8 9 7 2 1 4
8 9 7 2 1 4 3 6 5
5 3 1 6 4 2 9 7 8
6 4 2 9 7 8 5 3 1
9 7 8 5 3 1 6 4 2"""

def generate_sudoku(difficulty: SudokuDifficulty):
    # getting desired difficulty
    difficulty = difficulties[difficulty.value]

    # constructing generator object from puzzle str (space delimited columns, line delimited rows)
    gen = Generator(base_str)

    # applying 100 random transformations to puzzle
    gen.randomize(100)

    # getting a copy before slots are removed
    initial = gen.board.copy()

    # applying logical reduction with corresponding difficulty cutoff
    gen.reduce_via_logical(difficulty[0])

    # catching zero case
    if difficulty[1] != 0:
        # applying random reduction with corresponding difficulty cutoff
        gen.reduce_via_random(difficulty[1])

    # getting copy after reductions are completed
    final = gen.board.copy()
    return initial, final

def main():
    parser = ArgumentParser()
    parser.add_argument("difficulty", type=str, choices=difficulties.keys())
    args = parser.parse_args()
    initial, final = generate_sudoku(SudokuDifficulty(args.difficulty))

    # printing out complete board (solution)
    print("The initial board before removals was: \r\n\r\n{0}".format(initial.html()))

    # printing out board after reduction
    print("The generated board after removals was: \r\n\r\n{0}".format(final))

if __name__ == "__main__":
    main()