"""Main file for sudoku generator"""

import sys


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
            print(" ".join([str(x)if x != 0 else "." for x in self.board[i]]))

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


def main():
    """Function called when 'main.py' is executed"""
    print("Generating sudoku...")
    sudoku = Sudoku()
    sudoku.print()


if __name__ == "__main__":
    main()
