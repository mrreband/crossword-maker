import pytest

from grids import GridWord, Grid, Solution


@pytest.fixture
def grid_word_hello():
    return GridWord(word="hello", r=5, c=5, direction="across")


@pytest.fixture
def grid_word_world():
    return GridWord(word="world", r=2, c=7, direction="down")


@pytest.fixture
def grid():
    words_path = "./input/words.txt"
    return Grid(num_rows=20, num_cols=20, input_file_path=words_path)


@pytest.fixture
def solution(grid):
    return Solution(solution=[*grid.grid], placed_words=[], all_words=[*grid.words], depth=0,
                    output_folder=grid.output_folder)


def test_grid_word(grid_word_hello, grid_word_world):
    h = grid_word_hello.grid_letters[0]
    w = grid_word_world.grid_letters[0]

    assert all([gl.row == h.row for gl in grid_word_hello.grid_letters])
    assert all([gl.column == w.column for gl in grid_word_world.grid_letters])


def test_grid(grid, solution, grid_word_hello, grid_word_world):
    grid.place_grid_word(grid_word_hello, solution=solution)
    grid.place_grid_word(grid_word_world, solution=solution)
    solution.print_trimmed()


if __name__ == "__main__":
    pytest.main(["test_grids"])
