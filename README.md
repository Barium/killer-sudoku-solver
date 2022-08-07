Killer Sudoku Solver
====================

Killer Sodoku is a variant of Sodoku where there besides the regular nonets of numbers 1 through 9,
are also additional cages that acts as further limitation on which numbers can be where.
The cages are basically the only addition to regular Sudoku, so where the regular Sudoku dictates
that the numbers 1 through 9 can only exist once for each row, column and nonet. Killer Sudoku
builds upon that, and adds an additional limitation that the same number can not be represented more
than once in each cage, and that the sum of the numbers within the cage must be a specific
number.

In Sudoku additional limitations are often an advantage to the player since it greatly limits the
possible combinations that can be played. In Killer Sudoku fewer fields (if any) are filled out from
the start though.

## Performance

On my Core i7 4770K solving an expert level puzzle (without any fields on the board) takes less than
a second using this algorithm. The time it takes to complete varies from puzzle to puzzle, and is
fundamentally based upon how many combinations can be removed from the search tree. To test the
performance locally use the `--bencmark` parameter which will output how long it takes to solve the
given puzzle(s).

## How it works

The code works by basically filling the board with values, test the combination, and if it is not
valid try another combination. Obviously that is a simplified explanation, but fundamentally the
code fills the board one field at a time, until it is completely full, then it validates the board
and if the combination was not valid, the last added value will be removed and the next value is
chosen, and the validation is repeated. This continues until all possible values have been tested at
the last position, if it is still not valid, the next large value is replaced with the next possible
value, and the process repeats.

Simply testing all combinations is not a viable approach however, there is too many possible
combinations 6,670,903,752,021,072,936,960 to be exact. Therefor it is necessary to limit the amount
of combinations tested. First by removing invalid combinations, that is duplicates, and values in
cages exceeding the total. For each cell a minimum and a maximum is calculated. This is the possible
lowest value and the possible highest value that the value of the cell can have.

Consider a cage with the value of 17, consisting of two cells, the minimum value is 8 since, no
other number lower than that can add up to 17. The maximum value is 9. So the cells will each have 8
or 9. No other numbers makes sense in that cage, so there is no reason to test other combinations.
If 8 or 9 is not available, and already taken, then we already know that the combination is invalid,
and there is no reason to continue to the search.

Another simple limitation is cages of size 2, that have en even number. Here the value that is half
this number cannot be used. For instance a cage with the value 10, and size of 2. Can not use the
value 5, since that would require both fields to have the same value, and that is not legal. So here
we can remove another possible search combination.

Each time some of a cages values are filled out, we can subtract those values from the total and
apply the minimum and maximum value optimization on the remaining cells.

## How to use it

The code can be called from Python by creating a board struct, and a cages list. The board
structure is really just a 2 dimensional list of values for each cell. A `0` indicates that the cell
is empty. For expert level challenges these will all be `0`. The cages list is a list of tuples,
each tuple represents a cage. The first value of the tuple is the value of the cage, the second
value is a list of coordinate tuples. The coordinate tuples are the `x` and `y` coordinates of the
cells in the cage. The coordinates are 0-indexed.

To solve a Sudoku puzzle from Python structure, call the method `solve`, which has the signature:
`def solve(board: Board, cages: Cages) -> bool:` The solution found will be reflected in the board
passed as parameter.

The solver can also be called from the command-line. Use the `solve.py` file and provide the file
names of the puzzles to solve. For instance to solve the `expert-1.json` puzzle use the following
command:

    $ python solve.py expert-1.json

# License

This code is licensed under the [MIT License](https://opensource.org/licenses/MIT), see the license
file [`LICENSE`](LICENSE) for details.
