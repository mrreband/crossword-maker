import math
import random
from copy import deepcopy
from typing import List


class GridLetter:
    def __init__(self, letter: str, row: int, column: int):
        self.letter = letter
        self.row = row
        self.column = column
        self.intersection = ""

    @property
    def position(self):
        return self.row, self.column

    def __repr__(self):
        return f"{self.letter} - ({self.position}) {'*' if self.intersection else ''}"


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
    def __init__(self, word: str, r: int, c: int, direction: str, intersection_idx: int = None):
        self.word = word
        self.orientation = Orientation(direction=direction)
        self.grid_letters = []
        self.intersection_idx = intersection_idx

        self.placed_on_grid = r is not None and c is not None and direction is not None
        if self.placed_on_grid:
            for idx, letter in enumerate(word):
                grid_letter = GridLetter(
                    letter=letter,
                    row=r + idx * self.orientation.multipliers[0],
                    column=c + idx * self.orientation.multipliers[1],
                )
                if idx == intersection_idx:
                    grid_letter.intersection = True
                self.grid_letters.append(grid_letter)

    def __repr__(self):
        return f"{self.word}, ({self.start_position}) -- ({self.end_position}), {self.direction}"

    @property
    def intersection(self):
        if self.intersection_idx:
            return self.grid_letters[self.intersection_idx]
        return None

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
    def __init__(self, solution: List, placed_words: List[GridWord], all_words: List[str], depth: int):
        self.solution = solution
        self.placed_words = placed_words
        self.all_words = all_words
        self.depth = depth

    @property
    def remaining_words(self):
        placed_words = [w.word for w in self.placed_words]
        return [w for w in self.all_words if w not in placed_words]

    @property
    def transposed(self):
        return [*zip(*self.solution)]

    def __repr__(self):
        return f"depth {self.depth}, placed: {len(self.placed_words)}, remaining: {len(self.remaining_words)}"


class Grid:
    def __init__(self, num_rows: int, num_cols: int, words: List[str]):
        self.num_rows = num_rows
        self.num_cols = num_cols

        # empty grid
        self.grid = [["-"] * self.num_cols for i in range(self.num_rows)]
        self.possible_solutions = []

        # list of words (string)
        self.words = words

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

    def get_first_word(self):
        random_idx = random.randint(0, len(self.words))
        random_word = self.words[random_idx]
        center = self.__approximate_center
        first_word = GridWord(word=random_word, r=center[0], c=center[1], direction="across", intersection_idx=None)
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

    @staticmethod
    def print_solution(solution, missing):
        print(f"solution: missing {missing}")
        transposed = [*zip(*solution)]
        print('\n'.join([''.join([item for item in row]) for row in transposed]))

    def traverse(self, word_to_place: GridWord, current_solution: Solution, possible_solutions: list):
        print(f"traverse grid, depth {current_solution.depth} - word {word_to_place}")

        new_solution = deepcopy(current_solution)
        self.place_grid_word(grid_word=word_to_place, solution=new_solution)
        new_solution.depth += 1

        if len(current_solution.remaining_words) <= 1:
            self.print_solution(new_solution.solution, new_solution.remaining_words)

        if len(current_solution.remaining_words) == 0:
            possible_solutions.append(new_solution)

        other_grid_words = self.find_other_words(grid_word=word_to_place, solution=new_solution)
        for other_word in other_grid_words:
            self.traverse(word_to_place=other_word, current_solution=new_solution,
                          possible_solutions=possible_solutions)

        print(f"no solution on this branch, depth {new_solution.depth}, missing {new_solution.remaining_words}")

    def solve(self):
        first_word = self.get_first_word()
        current_solution = Solution(solution=[*self.grid], placed_words=[], all_words=[*self.words], depth=0)
        self.traverse(word_to_place=first_word, current_solution=current_solution, possible_solutions=[])
        return self.possible_solutions

    def word_fits(self, grid_word: GridWord):
        return grid_word.end_position[0] <= self.num_cols and grid_word.end_position[1] <= self.num_rows

    def words_are_adjacent(self, grid_word_1: GridWord, grid_word_2: GridWord):
        if self.words_intersect(grid_word_1=grid_word_1, grid_word_2=grid_word_2):
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

            # # check for unexpected intersections
            # intersections = self.get_intersections(placed_grid_word, candidate_grid_word)
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

    def find_other_words(self, grid_word: GridWord, solution: Solution):
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
                if self.word_is_valid(candidate_grid_word=other_possible_word, solution=solution):
                    print(f"    - {grid_word.word} <--> {other_possible_word})")
                    other_possible_words.append(other_possible_word)

        return other_possible_words
