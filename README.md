# sudoku-generator
Sudoku generator in python

### Usage (tested with Python 3.10.4)
`python main.py`

This will generate a sudoku with the default difficulty 3
and print its content to the console.
To specify a difficulty, add a value between 1 and 6 to the
console arguments:

`python main.py 5`

Note that values above 4 tend to take quite a long time (5+ minutes).
The script will try to generate solveable sudokus until a timeout is reached
(by default 600 seconds). To change this timeout, add it as a second
console argument (in seconds):

`python main.py 6 8000`

Additionally, adding `--export` as a console argument enables exporting
the finished generated sudoku to a .svg file:

`python main.py --export`