import random

import file_ops
from grids import Grid


if __name__ == "__main__":
    random.seed(1011)

    words = file_ops.read_word_list("./words.txt")
    grid = Grid(100, 100, words)
    solution = grid.solve()
    print(solution)
