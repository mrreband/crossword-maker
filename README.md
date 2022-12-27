## Crossword Maker

Makes valid crosswords from a list of words.    

---

### Usage: 

1. add words to `words.txt`, one per line
2. Set the maximum dimensions in `main.py`
2. run `main.py`

### Output: 

Each solution gets written as a txt file into the `output` directory.

- Solutions are trimmed to the relevant dimensions
- Dimensions are prepended to the solution filenames

----

### Example: 

input: 

```
HELLO
WORLD
CROSSWORD
```

output: 

```
--W------
CROSSWORD
--R------
HELLO----
--D------
```
