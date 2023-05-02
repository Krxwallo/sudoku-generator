"""Main file for sudoku generator"""

from datetime import datetime
import random
import sys
import time

from progress_bar import print_progress


class Sudoku:
    """Class for managing the sudoku instance"""

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        """Resets the sudoku; assign default variables"""
        rows = 9
        columns = 9
        self.board = [[0 for j in range(columns)] for i in range(rows)]

    def print(self):
        """Prints the current state of the sudoku to std out - empty fields are represented by '.'"""
        for i in range(9):
            print(" ".join([str(x) if x != 0 else "." for x in self.board[i]]))

    def number_is_valid(self, row, column, num):
        """Checks if [num] is already in the specified [row], [column] or in the box"""
        # check rows and columns
        for i in range(9):
            if num in (self.board[row][i], self.board[i][column]):
                return False

        # check the box
        # -> get start coordinates ('//' is integer division in python)
        start_row = row // 3 * 3
        start_column = column // 3 * 3
        for i in range(3):
            for j in range(3):
                if self.board[i + start_row][j + start_column] == num:
                    return False
        return True

    def solve(self):
        """Solve the sudoku"""
        # search for an empty field
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    # found empty field
                    for n in range(1, 10):
                        if self.number_is_valid(r, c, n):
                            self.board[r][c] = n
                            # solved?
                            yield from self.solve()
                            self.board[r][c] = 0
                    return
        yield True

    def evaluate(self, difficulty):
        """Get amount of empty cells for a specific [difficulty]"""
        empty_cells = [0, 25, 35, 45, 52, 58, 64]
        if difficulty < 1 or difficulty > len(empty_cells)-1:
            print("Invalid difficulty", file=sys.stderr)
            return 0
        return empty_cells[difficulty]

    def generate(self, difficulty):
        """Generates a brand-new (random) sudoku."""
        self.reset()  # reset values

        # generate diagonal values
        for i in range(0, 9, 3):  # 0, 3, 6
            square = list(range(1, 10))  # list from 1 to 9
            random.shuffle(square)
            for r in range(3):
                for c in range(3):
                    self.board[r + i][c + i] = square.pop()

        # get the first solution
        for _ in self.solve():
            break  # we only need one solution

        # get the amount of empty cells we need, corresponding to the difficulty the user wants
        empty_cells = self.evaluate(difficulty)
        start_empty_cells = empty_cells

        # remove cells
        # create a random list of all fields
        unvisited = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(unvisited)

        while empty_cells > 0 and len(unvisited) > 0:
            print_progress(start_empty_cells-empty_cells, start_empty_cells)

            # get random coordinates
            r, c = unvisited.pop()
            copy = self.board[r][c]  # save a copy of the value
            self.board[r][c] = 0  # remove the cell value

            # check if there is still only one solution
            solutions = list(self.solve())

            # we don't want a sudoku with multiple solutions
            if len(solutions) > 1:
                self.board[r][c] = copy  # restore value
            else:
                empty_cells -= 1  # we successfully removed a cell value

        # check if we could find a sudoku with the given amount of empty cells, or if all cells
        # were tried without success
        if empty_cells > 0:
            print("No solveable sudoku found. Retrying...")
            return 
        print("\n") # new line after progress bar
        return True


    def to_svg(self, cell_size=40, line_color="black"):
        """Generate svg data containing a drawn sudoku board with the current field values."""

        # header
        svg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'
        # simple white rectangle
        svg += f'<rect x="0" y="0" width="{9 * cell_size}" height="{9 * cell_size}" fill="white" />'

        # grid lines
        for i in range(10):
            line_width = 2 if i % 3 == 0 else 0.5
            # row lines
            svg += f'<line x1="{i * cell_size}" y1="0"  x2="{i * cell_size}" y2="{9 * cell_size}" \
                            style="stroke:{line_color}; stroke-width:{line_width}" />'
            # column lines
            svg += f'<line x1="0" y1="{i * cell_size}"  x2="{9 * cell_size}" y2="{i * cell_size}" \
                            style="stroke:{line_color}; stroke-width:{line_width}" />'

        # numbers
        for row in range(9):
            for column in range(9):
                if self.board[row][column] != 0:
                    svg += f'<text x="{(column + 0.5) * cell_size}" y="{(row + 0.5) * cell_size}" \
                        style="font-size:20; text-anchor:middle; dominant-baseline:middle"> {str(self.board[row][column])} </text>'

        svg += '</svg>' # ending
        return svg


DEFAULT_DIFFICULTY = 3
DEFAULT_TIMEOUT = 600


def main():
    """Function called when 'main.py' is executed"""
    # parse console arguments
    args = [int(x) if x.isdecimal() else x for x in sys.argv[1:]]
    if "--help" in args:
        print("Python script for generating a sudoku (and exporting it to .svg)")
        print(f"Usage: {' '.join(sys.argv[:1])} DIFFICULTY TIMEOUT [--export]")
        print("- DIFFICULTY: integer number between 1 and 6 (5 and 6 may take a very long time to generate)")
        print("- TIMEOUT: the maximum time in seconds to spend retrying when no solveable sudoku was found")
        print("- Use '--export' to enable exporting the generated sudoku to a .svg file.")
        sys.exit(0)

    export = False
    if "--export" in args:
        export = True
        args.remove("--export")
    difficulty = args[0] if len(args) > 0 else DEFAULT_DIFFICULTY
    timeout = args[1] if len(args) > 1 else DEFAULT_TIMEOUT
    print(f"Generating sudoku with difficulty {difficulty}...")
    print(f"Will retry for {timeout}s on failure.")
    if export:
        now = datetime.now()
        file_name = f"sudoku-{now:%Y%m%dT%H%M%S}-{difficulty}.svg"
        print(f"Sudoku will be exported to {file_name}")

    # create Sudoku instance
    sudoku = Sudoku()

    end_time = time.time() + timeout
    while time.time() < end_time: # Retry until timeout occurs or solveable sudoku was found
        if sudoku.generate(difficulty):
            if export:
                # User wants us to export the sudoku.
                # Save it to a .svg file with the file name containing the current date, time and the difficulty
                print("Sudoku found. Exporting... ", end = '')
                data = sudoku.to_svg()
                with open(file_name, 'w', encoding="utf-8") as file:
                    file.write(data)
                print("✓")
            else:
                # User doesn't want us to export the sudoku. Just print it to the console.
                print("Sudoku found:")
                sudoku.print()
            break
        sudoku.reset()


if __name__ == "__main__":
    main()
