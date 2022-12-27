from grids import Grid


def load_file(file_path: str):
    with open(file_path) as file:
        words = file.readlines()
        words = [w.upper().strip() for w in words]
        return words


if __name__ == "__main__":
    import random
    random.seed(1011)

    words = load_file("./words.txt")
    grid = Grid(num_rows=100, num_cols=100, words=words)
    solutions = grid.solve()
    print(solutions)
