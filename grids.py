import math
import random
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
    def __init__(self, word: str, r: int, c: int, direction: str, intersection: int):
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
                if idx == intersection:
                    grid_letter.intersection = True
                self.grid_letters.append(grid_letter)

    def __repr__(self):
        return f"{self.word}, ({self.start_position}) -- ({self.end_position}), {self.direction}"

    @property
    def direction(self):
        return self.orientation.direction

    @property
    def start_position(self):
        return self.grid_letters[0].position

    @property
    def end_position(self):
        return self.grid_letters[-1].position


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

    def traverse(self, word_to_place: GridWord, other_words: List[str], depth: int, possible_solution):
        self.place_grid_word(grid_word=word_to_place)

        if len(other_words) == 0:
            self.possible_solutions.append(possible_solution)

        remaining_words = [w for w in other_words if w != word_to_place.word]
        other_grid_words = self.find_other_words(word_to_place, other_words)
        for other_word in other_grid_words:
            self.traverse(other_word, remaining_words, depth + 1, possible_solution)

    def solve(self):
        first_word = self.get_first_word()
        possible_solution = [*self.grid]
        self.traverse(word_to_place=first_word, other_words=self.words, depth=1, possible_solution=possible_solution)
        return self.possible_solutions

    def get_first_word(self):
        random_idx = random.randint(0, len(self.words))
        random_word = self.words[random_idx]
        center = self.__approximate_center
        first_word = GridWord(word=random_word, r=center[0], c=center[1], direction="across", intersection=None)
        return first_word

    def place_first_word(self):
        first_word = self.get_first_word()
        self.place_grid_word(grid_word=first_word)
        return first_word

    def place_word(self, word: str, r, c, direction, whatif: bool = False):
        grid_word = GridWord(word=word, r=r, c=c, direction=direction)
        self.place_grid_word(grid_word=grid_word, whatif=whatif)
        return grid_word

    def place_grid_word(self, grid_word: GridWord, whatif: bool = False):
        for letter in grid_word.grid_letters:
            if self.grid[letter.column][letter.row] != "-":
                if not letter.intersection:
                    raise ValueError(f"{letter} would overwrite another")
            self.grid[letter.column][letter.row] = letter.letter
        grid_word.placed_on_grid = True
        self.grid_words.append(grid_word)

    def __word_fits(self, grid_word: GridWord):
        return grid_word.end_position[0] <= self.num_cols and grid_word.end_position[1] <= self.num_rows

    def __words_are_adjacent(self, grid_word_1: GridWord, grid_word_2: GridWord):
        if any([gl.intersection for gl in grid_word_2.grid_letters]):
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
                if any([abs(down_column - col) == 1 for col in across_columns]):
                    return True
                if any([abs(across_row - row) == 1 for row in down_rows]):
                    return True
            # elif grid_word_1.direction == "down" and grid_word_2.direction == "across":
            #     # for perpendicular words, need to check the endpoints
            #     down_column = grid_word_2.grid_letters[0].column
            #     down_rows = [gl.row for gl in grid_word_2.grid_letters]

            #     across_row = grid_word_1.grid_letters[0].row
            #     across_columns = [gl.column for gl in grid_word_1.grid_letters]
            #     if any([abs(down_column - col) == 1 for col in across_columns]):
            #         return True
            #     if any([abs(across_row - row) == 1 for row in down_rows]):
            #         return True

        return False

    def __words_overlap(self, grid_word_1: GridWord, grid_word_2: GridWord):
        ...

    def __words_intersect(self, grid_word_1: GridWord, grid_word_2: GridWord):
        ...

    def __word_is_valid(self, candidate_grid_word: GridWord):
        # check if it's off the grid
        word_fits = self.__word_fits(candidate_grid_word)
        if not word_fits:
            return False

        for placed_grid_word in self.grid_words:
            if self.__words_are_adjacent(placed_grid_word, candidate_grid_word):
                return False
        return True

    def find_other_words(self, grid_word: GridWord, other_words: List[str]):
        """
        go thru each letter of this grid_word.  find any other words that have that letter
        and that if placed appropriately on the grid would be valid

        :type grid_word: GridWord
        :type other_words: List[str]
        """
        target_orientation = Orientation.orthogonal(grid_word.direction)

        other_possible_words = []
        for grid_letter in grid_word.grid_letters:
            letter = grid_letter.letter

            print(f"{grid_word.word} - looking for remaining words with {letter} ({grid_letter.position})")
            others_with_letter = [w for w in other_words if w != grid_word.word and letter in w]
            for other in others_with_letter:
                intersection_position = str(other).index(letter)
                other_starting_position = [*grid_letter.position]

                if target_orientation.direction == "down":
                    other_starting_position[0] -= intersection_position
                else:
                    other_starting_position[1] -= intersection_position

                print(f"{other} - {letter} found in {intersection_position}")
                print(f"{other} - starting_position = {other_starting_position}")
                other_possible_word = GridWord(
                    word=other,
                    r=other_starting_position[0],
                    c=other_starting_position[1],
                    direction=target_orientation.direction,
                    intersection=intersection_position,
                )
                if self.__word_is_valid(candidate_grid_word=other_possible_word):
                    other_possible_words.append(other_possible_word)

        return other_possible_words
