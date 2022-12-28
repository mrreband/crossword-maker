from grids import Grid, GridWord


def load_solution(grid: Grid):
    grid_words = [
        GridWord(word="MICHAEL", r=2, c=0, direction="across"),
        GridWord(word="ANNA", r=2, c=7, direction="across"),
    ]
    partial_solution = grid.load_solution(grid_words=grid_words)
    partial_solution.print_trimmed()
    grid.solve(partial_solution=partial_solution)


if __name__ == "__main__":
    input_file_path = "input/grandkids.txt"

    grid = Grid(num_rows=100, num_cols=100, input_file_path=input_file_path)

    # load_solution(grid=grid)

    solutions = grid.solve()
    print(solutions)


