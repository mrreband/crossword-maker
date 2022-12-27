from grids import Grid


if __name__ == "__main__":
    input_file_path = "input/children.txt"

    grid = Grid(num_rows=100, num_cols=100, input_file_path=input_file_path)
    solutions = grid.solve()
    print(solutions)
