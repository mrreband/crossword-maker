## Crossword Maker

Makes valid crosswords from a list of words.  Uses python with no dependencies.       

I found a few similar attempts out there (like [this](https://github.com/riverrun/genxword) and [this](https://pypi.org/project/pycrossword/) and [this](https://codereview.stackexchange.com/questions/231222/python-3-code-to-generate-simple-crossword-puzzles-from-a-list-of-words-anagrams)) - each of them had issues either with the logic or with package dependencies 

---

### Structure: 

All code is in `crossword_maker.py`

class structure: 

- Grid
  - Solution
    - GridWord
      - GridLetter
      - Orientation

---

### Usage: 

1. add words to a text file in `./input`, one per line
2. Set parameters in `main.py`: 
   - `num_rows`
   - `num_cols`
   - `input_file_path`
3. run `main.py`

### Output: 

Each solution gets written as a txt file into the `output` directory.

- Solutions are trimmed to the relevant dimensions
- Dimensions are prepended to the solution filenames

----

### Example: 

input: `./input/hello_world.txt`

```
HELLO
WORLD
CROSSWORD
```

output: `./output/hello_world/45 - 9x5 1694677741392.txt`

```
--W------
CROSSWORD
--R------
HELLO----
--D------
```
