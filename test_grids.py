import pytest

from grids import GridWord, Grid


@pytest.fixture
def grid_word_hello():
    return GridWord(word="hello", r=5, c=5, direction="across", intersection_idx=None)


@pytest.fixture
def grid_word_world():
    return GridWord(word="world", r=2, c=7, direction="down", intersection_idx=None)


@pytest.fixture
def grid():
    return Grid(num_rows=20, num_cols=20, words=["hello", "world"])


def test_grid_word(grid_word_hello, grid_word_world):
    h = grid_word_hello.grid_letters[0]
    w = grid_word_world.grid_letters[0]

    assert all([gl.row == h.row for gl in grid_word_hello.grid_letters])
    assert all([gl.column == w.column for gl in grid_word_world.grid_letters])


def test_grid(grid, grid_word_hello, grid_word_world):
    grid.place_grid_word(grid_word_hello)
    print(grid)
    # grid.place_grid_word(grid_word_world)


if __name__ == "__main__":
    pytest.main(["test_grids"])
