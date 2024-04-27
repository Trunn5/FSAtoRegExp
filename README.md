# FSAtoRegExp.py

A barebones Python library for translate deterministic and non-determinstic finite automata to regular expression string. Made for University Assignment.

`FSAtoRegExp.py` can give a Regex String for any FSA.

## Usage

### Initialization
```python
from FSAtoRegExp import FSAtoRegExpTranslator
```


### Creation
```python
fsa = FSAtoRegExpTranslator()
fsa.input_data('input.txt') # filename
```

    type: str t // t ∈ {deterministic, non-deterministic}

    states: list[str] [s1,s2,...] // s1 , s2, ... ∈ latin letters, words and numbers

    alphabet: list[str] [a1,a2,...] // a1 , a2, ... ∈ latin letters, words, numbers and character '_' (underscore)

    initial: str [s] // s ∈ states

    accepting: list[str] [s1,s2,...] // s1, s2 ∈ states

    transitions: dict[str, dict[str, set[str]]] [s1>a>s2,...] // s1,s2,...∈ states; a ∈ alphabet
    ----------------[from---[trans, {to-states}]]----


### Get Regex String
```python
s = fsa.get_regex_string()
```

