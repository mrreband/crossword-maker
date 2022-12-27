from copy import deepcopy

from grids import GridWord, Solution, Orientation


def place_grid_word(grid_word: GridWord, solution: Solution):
    for letter in grid_word.grid_letters:
        if solution.solution[letter.column][letter.row] != "-":
            would_overwrite = solution.solution[letter.column][letter.row]
            if would_overwrite != letter.letter:
                raise ValueError(f"{letter} would overwrite {would_overwrite}")
        solution.solution[letter.column][letter.row] = letter.letter
    grid_word.placed_on_grid = True
    solution.placed_words.append(grid_word)

def solve(grid, words):
    first_word = get_first_word()
    current_solution = Solution(solution=[*grid], placed_words=[], all_words=[*words], depth=0)
    solutions = traverse(word_to_place=first_word, current_solution=current_solution, possible_solutions=[])
    return solutions

def traverse(word_to_place: GridWord, current_solution: Solution, possible_solutions: list):
    # print(f"traverse grid, depth {current_solution.depth} - word {word_to_place}")

    new_solution = deepcopy(current_solution)
    place_grid_word(grid_word=word_to_place, solution=new_solution)
    new_solution.depth += 1

    if len(new_solution.remaining_words) == 1:
        new_solution.print_solution()

    if len(new_solution.remaining_words) == 0:
        possible_solutions.append(new_solution)
        # new_solution.print_solution()
        return

    other_grid_words = find_other_words(grid_word=word_to_place, solution=new_solution)
    for other_word in other_grid_words:
        traverse(word_to_place=other_word, current_solution=new_solution,
                      possible_solutions=possible_solutions)

    # print(f"no solution on this branch, depth {new_solution.depth}, missing {new_solution.remaining_words}")


def word_fits(grid_word: GridWord, solution):
    return grid_word.end_position[0] <= solution.num_cols and grid_word.end_position[1] <= solution.num_rows


def words_are_adjacent(grid_word_1: GridWord, grid_word_2: GridWord):
    if words_intersect(grid_word_1=grid_word_1, grid_word_2=grid_word_2):
        return False

    if grid_word_1.direction == "across" and grid_word_2.direction == "across":
        # for parallel words, need to check each letter
        for grid_letter_1 in grid_word_1.grid_letters:
            for grid_letter_2 in grid_word_2.grid_letters:
                if grid_letter_1.column == grid_letter_2.column:
                    if abs(grid_letter_1.row - grid_letter_2.row) == 1:
                        return True
    elif grid_word_1.direction == "down" and grid_word_2.direction == "down":
        for grid_letter_1 in grid_word_1.grid_letters:
            for grid_letter_2 in grid_word_2.grid_letters:
                if grid_letter_1.row == grid_letter_2.row:
                    if abs(grid_letter_1.column - grid_letter_2.column) == 1:
                        return True
    else:
        if grid_word_1.direction == "across" and grid_word_2.direction == "down":
            # for perpendicular words, need to check the endpoints
            down_column = grid_word_2.grid_letters[0].column
            down_rows = [gl.row for gl in grid_word_2.grid_letters]

            across_row = grid_word_1.grid_letters[0].row
            across_columns = [gl.column for gl in grid_word_1.grid_letters]
        elif grid_word_1.direction == "down" and grid_word_2.direction == "across":
            down_column = grid_word_1.grid_letters[0].column
            down_rows = [gl.row for gl in grid_word_1.grid_letters]

            across_row = grid_word_2.grid_letters[0].row
            across_columns = [gl.column for gl in grid_word_2.grid_letters]
        else:
            raise ValueError(f"unexpected directions: {grid_word_1.direction} vs {grid_word_2.direction}")

        if any([abs(down_column - col) == 1 for col in across_columns]):
            return True
        if any([abs(across_row - row) == 1 for row in down_rows]):
            return True

    return False


def get_intersections(grid_word_1: GridWord, grid_word_2: GridWord):
    positions_1 = set([gl.position for gl in grid_word_1.grid_letters])
    positions_2 = set([gl.position for gl in grid_word_2.grid_letters])
    intersections = positions_1.intersection(positions_2)
    return list(intersections)


def words_overlap(grid_word_1: GridWord, grid_word_2: GridWord):
    intersections = get_intersections(grid_word_1=grid_word_1, grid_word_2=grid_word_2)
    if len(intersections) > 1:
        return True
    else:
        return False


def words_intersect(grid_word_1: GridWord, grid_word_2: GridWord):
    intersections = get_intersections(grid_word_1=grid_word_1, grid_word_2=grid_word_2)
    if len(intersections) == 1:
        return True
    else:
        return False


def word_is_valid(candidate_grid_word: GridWord, solution: Solution):
    # check if it's off the grid
    if not word_fits(candidate_grid_word, solution):
        return False

    for placed_grid_word in solution.placed_words:
        if words_overlap(placed_grid_word, candidate_grid_word):
            return False

        if words_are_adjacent(placed_grid_word, candidate_grid_word):
            return False

        # # check for unexpected intersections
        # intersections = get_intersections(placed_grid_word, candidate_grid_word)
        # if intersections and candidate_grid_word.intersection:
        #     if candidate_grid_word.intersection.position != intersections[0]:
        #         return False

    def try_place_grid_word(grid_word: GridWord):
        for letter in grid_word.grid_letters:
            if solution.solution[letter.column][letter.row] != "-":
                would_overwrite = solution.solution[letter.column][letter.row]
                if would_overwrite != letter.letter:
                    return False
        return True

    return try_place_grid_word(grid_word=candidate_grid_word)

def find_other_words(grid_word: GridWord, solution: Solution):
    """
    go thru each letter of this grid_word.  find any other words that have that letter
    and that if placed appropriately on the grid would be valid

    :type grid_word: GridWord
    :type solution: Solution
    """
    other_words = solution.remaining_words
    target_orientation = Orientation.orthogonal(grid_word.direction)

    other_possible_words = []
    for grid_letter in grid_word.grid_letters:
        letter = grid_letter.letter

        # print(f"    - {grid_word.word} - looking for remaining words with {letter} ({grid_letter.position})")
        others_with_letter = [w for w in other_words if w != grid_word.word and letter in w]
        for other in others_with_letter:
            intersection_position = str(other).index(letter)
            other_starting_position = [*grid_letter.position]

            if target_orientation.direction == "down":
                other_starting_position[0] -= intersection_position
            else:
                other_starting_position[1] -= intersection_position

            # print(f"        - {other} - {letter} found in {intersection_position}")
            # print(f"        - {other} - starting_position = {other_starting_position}")
            other_possible_word = GridWord(
                word=other,
                r=other_starting_position[0],
                c=other_starting_position[1],
                direction=target_orientation.direction,
                intersection_idx=intersection_position,
            )
            if word_is_valid(candidate_grid_word=other_possible_word, solution=solution):
                # print(f"    - {grid_word.word} <--> {other_possible_word})")
                other_possible_words.append(other_possible_word)

    return other_possible_words
