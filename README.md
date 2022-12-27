## Crossword Maker

Makes valid crosswords from a list of words.    

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
