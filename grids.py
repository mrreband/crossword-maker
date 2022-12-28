import math
import ntpath
import os
import random

from copy import deepcopy
from typing import List


class GridLetter:
    def __init__(self, letter: str, row: int, column: int):
        self.letter = letter
        self.row = row
        self.column = column

    @property
    def position(self):
        return self.row, self.column

    def __repr__(self):
        return f"{self.letter} - ({self.position})"


class Orientation:
    def __init__(self, direction: str):
        self.direction = direction

        if self.direction == "across":
            self.multipliers = (0, 1)
            self.orientation = "row"
        elif self.direction == "down":
            self.multipliers = (1, 0)
            self.orientation = "column"
        else:
            raise ValueError(f"unexpected direction {direction}")

    @property
    def direction_idx(self):
        if self.multipliers[0] == 1:
            return 0
        else:
            return 1

    @classmethod
    def orthogonal(cls, direction):
        if direction == "across":
            return cls("down")
        else:
            return cls("across")


class GridWord:
    def __init__(self, word: str, r: int, c: int, direction: str):
        self.word = word
        self.orientation = Orientation(direction=direction)
        self.grid_letters = []

        self.placed_on_grid = r is not None and c is not None and direction is not None
        if self.placed_on_grid:
            for idx, letter in enumerate(word):
                grid_letter = GridLetter(
                    letter=letter,
                    row=r + idx * self.orientation.multipliers[0],
                    column=c + idx * self.orientation.multipliers[1],
                )
                self.grid_letters.append(grid_letter)

    def __repr__(self):
        r, c = self.start_position
        return f"GridWord(word='{self.word}', r={r}, c={c}, direction='{self.direction}')"

    @property
    def direction(self):
        return self.orientation.direction

    @property
    def start_position(self):
        return self.grid_letters[0].position

    @property
    def end_position(self):
        return self.grid_letters[-1].position


class Solution:
    def __init__(self, solution: List, placed_words: List[GridWord], all_words: List[str], depth: int,
                 output_folder: str = "./output"):
        self.solution = solution
        self.placed_words = placed_words
        self.all_words = all_words
        self.depth = depth
        self.output_folder = output_folder

        os.makedirs(self.output_folder, exist_ok=True)

    @property
    def bottom_right(self):
        end_rows = [gw.end_position[0] for gw in self.placed_words]
        end_cols = [gw.end_position[1] for gw in self.placed_words]
        max_end_row = max(end_rows)
        max_end_col = max(end_cols)
        return max_end_row, max_end_col

    @property
    def top_left(self):
        start_rows = [gw.start_position[0] for gw in self.placed_words]
        start_cols = [gw.start_position[1] for gw in self.placed_words]
        min_start_row = min(start_rows)
        min_start_col = min(start_cols)
        return min_start_row, min_start_col

    @property
    def width(self):
        return self.bottom_right[0] - self.top_left[0] + 1

    @property
    def height(self):
        return self.bottom_right[1] - self.top_left[1] + 1

    @property
    def dimensions(self):
        return f"{self.width}x{self.height}"

    @property
    def area(self):
        return f"00{self.height * self.width}"[-3:]

    @property
    def remaining_words(self):
        placed_words = [w.word for w in self.placed_words]
        return [w for w in self.all_words if w not in placed_words]

    @property
    def trimmed(self):
        trimmed_solution = [["-"] * (self.width) for i in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                try:
                    trimmed_solution[i][j] = self.solution[self.top_left[1] + i][self.top_left[0] + j]
                except Exception as ex:
                    print(ex)
        return [*zip(*trimmed_solution)]

    @property
    def transposed(self):
        return [*zip(*self.solution)]

    def __repr__(self):
        return f"depth {self.depth}, dimensions: {self.dimensions}, placed: {len(self.placed_words)}, remaining: {len(self.remaining_words)}"

    def print_trimmed(self):
        print(f"solution: missing {self.remaining_words}")
        print('\n'.join([''.join([item for item in row]) for row in self.trimmed]))

    def write_solution(self):
        solution = '\n'.join([''.join([item for item in row]) for row in self.trimmed])

        output_file_path = f"{self.output_folder}/{self.area} -- {self.dimensions}-{id(self)}.txt"
        print(output_file_path)

        with open(output_file_path, "w") as file:
            file.write(solution)


class Grid:
    def __init__(self, num_rows: int, num_cols: int, input_file_path: str = "./input/words.txt"):
        def load_file(file_path: str):
            with open(file_path) as file:
                words = file.readlines()
                words = [w.upper().strip() for w in words]
                words = [w for w in words if w != ""]
                return words

        self.num_rows = num_rows
        self.num_cols = num_cols

        # empty grid
        self.grid = [["-"] * self.num_cols for i in range(self.num_rows)]
        self.possible_solutions = []

        # list of words (string)
        self.words = load_file(input_file_path)
        self.input_file_path = input_file_path
        self.file_name = ntpath.basename(input_file_path)

        # for output directory
        self.output_folder = f"./output/{self.file_name.rstrip('.txt')}"

        # list of GridWord objects
        self.grid_words = []

    def __repr__(self):
        return self.solution

    @property
    def transposed(self):
        return [*zip(*self.grid)]

    @property
    def solution(self):
        return '\n'.join([''.join([item for item in row]) for row in self.transposed])

    def get_grid_word(self, word: str):
        return next(iter([gw for gw in self.grid_words if gw.word == word]))

    @property
    def placed_words(self) -> List[str]:
        return [gw.word for gw in self.grid_words if gw.placed_on_grid]

    @property
    def remaining_words(self) -> List[str]:
        return [w for w in self.words if w not in self.placed_words]

    @property
    def __approximate_center(self):
        center = (math.floor(self.num_rows / 2), math.floor(self.num_cols / 2))
        return center

    def get_first_word(self, word: str):
        center = self.__approximate_center
        first_word = GridWord(word=word, r=center[0], c=center[1], direction="across")
        return first_word

    def place_grid_word(self, grid_word: GridWord, solution: Solution):
        for letter in grid_word.grid_letters:
            if solution.solution[letter.column][letter.row] != "-":
                would_overwrite = solution.solution[letter.column][letter.row]
                if would_overwrite != letter.letter:
                    raise ValueError(f"{letter} would overwrite {would_overwrite}")
            solution.solution[letter.column][letter.row] = letter.letter
        grid_word.placed_on_grid = True
        solution.placed_words.append(grid_word)

    def traverse(self, word_to_place: GridWord, current_solution: Solution, possible_solutions: list):
        new_solution = deepcopy(current_solution)
        if word_to_place:
            self.place_grid_word(grid_word=word_to_place, solution=new_solution)
            new_solution.depth += 1

        # if len(new_solution.remaining_words) <= 1:
        #     print(f"traverse grid, depth {new_solution.depth} - remaining {new_solution.remaining_words}")
        #     new_solution.print_trimmed()

        if len(new_solution.remaining_words) == 0:
            solutions = [s.solution for s in possible_solutions]
            if new_solution.solution not in solutions:
                new_solution.write_solution()
                possible_solutions.append(new_solution)

        other_grid_words = self.find_other_words(solution=new_solution)
        for other_word in other_grid_words:
            self.traverse(word_to_place=other_word, current_solution=new_solution,
                          possible_solutions=possible_solutions)

        return possible_solutions

    def clear_solutions(self):
        if os.path.exists(self.output_folder):
            import shutil
            shutil.rmtree(self.output_folder)
        os.makedirs(self.output_folder)

    def solve(self, partial_solution: Solution = None):
        self.clear_solutions()
        solutions = []

        if partial_solution is None:
            for word in self.words:
                first_word = self.get_first_word(word=word)
                partial_solution = Solution(solution=[*self.grid], placed_words=[], all_words=[*self.words], depth=0,
                                            output_folder=self.output_folder)
                solutions.extend(
                    self.traverse(word_to_place=first_word, current_solution=partial_solution, possible_solutions=[]))
        else:
            self.traverse(word_to_place=None, current_solution=partial_solution, possible_solutions=[])

        return solutions

    def load_solution(self, grid_words: List[GridWord]):
        solution = Solution(solution=[*self.grid], placed_words=[], all_words=[*self.words], depth=0,
                            output_folder=self.output_folder)
        for grid_word in grid_words:
            if self.word_is_valid(candidate_grid_word=grid_word, solution=solution):
                self.place_grid_word(grid_word=grid_word, solution=solution)
            else:
                raise ValueError(f"invalid solution")
        return solution

    def word_fits(self, grid_word: GridWord):
        return grid_word.end_position[0] <= self.num_cols and grid_word.end_position[1] <= self.num_rows

    def words_are_adjacent(self, grid_word_1: GridWord, grid_word_2: GridWord):
        if self.words_intersect(grid_word_1=grid_word_1, grid_word_2=grid_word_2):
            return False

        for grid_letter_1 in grid_word_1.grid_letters:
            for grid_letter_2 in grid_word_2.grid_letters:
                if grid_letter_1.row == grid_letter_2.row and abs(grid_letter_1.column - grid_letter_2.column) == 1:
                    return True
                if grid_letter_1.column == grid_letter_2.column and abs(grid_letter_1.row - grid_letter_2.row) == 1:
                    return True

        return False

    def get_intersections(self, grid_word_1: GridWord, grid_word_2: GridWord):
        positions_1 = set([gl.position for gl in grid_word_1.grid_letters])
        positions_2 = set([gl.position for gl in grid_word_2.grid_letters])
        intersections = positions_1.intersection(positions_2)
        return list(intersections)

    def words_overlap(self, grid_word_1: GridWord, grid_word_2: GridWord):
        intersections = self.get_intersections(grid_word_1=grid_word_1, grid_word_2=grid_word_2)
        if len(intersections) > 1:
            return True
        else:
            return False

    def words_intersect(self, grid_word_1: GridWord, grid_word_2: GridWord):
        intersections = self.get_intersections(grid_word_1=grid_word_1, grid_word_2=grid_word_2)
        if len(intersections) == 1:
            return True
        else:
            return False

    def word_is_valid(self, candidate_grid_word: GridWord, solution: Solution):
        # check if it's off the grid
        word_fits = self.word_fits(candidate_grid_word)
        if not word_fits:
            return False

        for placed_grid_word in solution.placed_words:
            if self.words_overlap(placed_grid_word, candidate_grid_word):
                return False

            if self.words_are_adjacent(placed_grid_word, candidate_grid_word):
                return False

            if placed_grid_word.direction == candidate_grid_word.direction:
                if self.words_intersect(placed_grid_word, candidate_grid_word):
                    return False

        def try_place_grid_word(grid_word: GridWord):
            for letter in grid_word.grid_letters:
                try:
                    existing_cell = solution.solution[letter.column][letter.row]
                except IndexError:
                    # off the grid
                    return False
                if existing_cell != "-":
                    if existing_cell != letter.letter:
                        return False
            return True

        return try_place_grid_word(grid_word=candidate_grid_word)

    def find_other_words(self, solution: Solution):
        """
        go thru each letter of this grid_word.  find any other words that have that letter
        and that if placed appropriately on the grid would be valid

        :type solution: Solution
        """
        other_words = solution.remaining_words

        other_possible_words = []
        for grid_word in solution.placed_words:
            target_orientation = Orientation.orthogonal(grid_word.direction)

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
                    )
                    if self.word_is_valid(candidate_grid_word=other_possible_word, solution=solution):
                        # print(f"    - {grid_word.word} <--> {other_possible_word})")
                        other_possible_words.append(other_possible_word)

        return other_possible_words
