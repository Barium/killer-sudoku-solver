import json
import timeit

Cages = list[tuple[int, list[tuple[int, int]]]]
Board = list[list[int]]
MinMaxCache = list[list[tuple[int, int]]]

validations_performed = 0
combinations_tried = 0


def find_cage_index(cages: Cages, x: int, y: int) -> int:
    """Find the index of the cage at coordinate (x, y).

    If the cage at coordinate (x, y) does not exist in the list of cages, an AssertionError is
    raised.

    :param cages: The list of cages to look up
    :param x: The zero indexed x coordinate
    :param y: The zero indexed y coordinate
    :return: Returns the cage index for the cage at x, y
    """
    index = 0
    for total, fields in cages:
        if (x, y) in fields:
            return index
        index += 1

    raise AssertionError(f"Cage for coordinates ({x}, {y}) not found")


def is_same_cage(cages: Cages, x1: int, y1: int, x2: int, y2: int) -> bool:
    """Returns true if two coordinates belong to the same cage.

    If either set of coordinates are not found as a cage, an AssertionError is raised.

    :param cages: The list of cages to look up
    :param x1: The zero indexed x coordinate of the first cage
    :param y1: The zero indexed y coordinate of the first cage
    :param x2: The zero indexed x coordinate of the second cage
    :param y2: The zero indexed y coordinate of the second cage
    :return: Returns true if the cages are the same
    """
    return find_cage_index(cages, x1, y1) == find_cage_index(cages, x2, y2)


def print_board(board: Board, cages: Cages) -> None:
    """Print the board with cages to the console.

    :param board: The board to print
    :param cages: The list of cages to display on the board
    """
    print("+" + "---+" * 9)
    for y in range(9):
        print("|", end="")
        sep_line = "|"
        for x in range(9):
            value = board[y][x]
            end_char = "|"
            if x < 8 and is_same_cage(cages, x, y, x + 1, y):
                end_char = " "
            if y < 8 and is_same_cage(cages, x, y, x, y + 1):
                sep_line += "   +"
            else:
                sep_line += "---+"
            print(f" {value if  value > 0 else ' '} {end_char}", end="")
        print()
        print(sep_line)


def find_taken_value(board: Board, cages: Cages, cage_cache: Board,
                     x: int, y: int) -> list[int]:
    """Find values taken, that will not be available at the cell at coordinate (x, y).

    :param board: The board to search for taken values
    :param cages: The cages to search for taken values but only the one including the coordinate
    :param cage_cache: The lookup cache converting a coordinate to a cage
    :param x: The zero indexed x coordinate of the position to examine
    :param y: The zero indexed y coordinate of the position to examine
    :return: Returns a list of values that is already taken
    """
    taken_values = []

    # Values taken in the nonet
    for ty in find_nonet_range(y):
        for tx in find_nonet_range(x):
            if board[ty][tx] > 0:
                taken_values.append(board[ty][tx])

    # Values taken in cage
    total, fields = cages[cage_cache[y][x]]
    field_count = len(fields)
    for fx, fy in fields:
        val = board[fy][fx]
        if val > 0:
            total -= val
            field_count -= 1
            taken_values.append(val)
    # Calculate values that are too large to now fit in the cage, since we have subtracted the
    # already taken values from the total, and reduced the field count this might reduce the number
    # of possible values considerably
    max_value = min(total - sum([i for i in range(1, 10)][:field_count - 1]), 9)
    if max_value < 9:
        taken_values.extend(range(max_value + 1, 10))
    min_value = max(total - sum([i for i in range(9, 0, -1)][:field_count - 1]), 1)
    if min_value > 1:
        taken_values.extend(range(1, min(min_value, 10)))

    # Find taken values in the column and row that the position is in
    for pos in range(9):
        if board[y][pos] > 0:
            taken_values.append(board[y][pos])
        if board[pos][x] > 0:
            taken_values.append(board[pos][x])

    return taken_values


def find_minmax_value(cages: Cages, x: int, y: int) -> tuple[int, int]:
    """ Find minimum and maximum possible values for a cell on the board

    Since cages is a subset of fields that rarely contain all 9 numbers, it is possible to
    calculate the minimum and maximum possible values of each field in a cage. The naive approach
    used here will consider the entire cage the same. This will help reduce the number of possible
    combinations enough that even the expert boards are solvable in due time.

    This method is only run once, and since it is only run once, and the min/max cache is calculated
    at the same time as the cage cache, we will look up the cage index for each cell.

    :param cages: The cages to evaluate
    :param x: The zero based index of the x coordinate
    :param y: The zero based index of the y coordinate
    :return: Returns a tuple of the minimum and maximum possible values
    """
    cage_index = find_cage_index(cages, x, y)
    total, fields = cages[cage_index]
    field_count = len(fields)
    min_val = max(total - sum([i for i in range(9, 0, -1)][:field_count - 1]), 1)
    max_val = min(total - sum([i for i in range(1, 10)][:field_count - 1]), 9)
    return min_val, max_val


def find_nonet_range(coord: int) -> range:
    """ Find the range of a nonet along a single axis.

    The first 3 fields along an axis are equal to the nonet that resides in the range [0;3[. The
    next 3 equals the range [3;6[ and the final 3 equals [6:9[. Since this is the same for both axis
    this method is called for a single axis at a time.

    :param coord: The zero-based coordinate along an axis
    :return: Returns the range used by the nonet along the specific axis
    """
    if coord < 3:
        return range(0, 3)
    if coord < 6:
        return range(3, 6)
    return range(6, 9)


def find_next_cell(board: Board, x: int, y: int) -> tuple[int, int]:
    """ Find next unoccupied cell in the board, or return (-1, -1).

    The method will search for the next empty cell on the board, not including the one provided by
    the `x` and `y` parameters. The search will first try the cell next to the one specified along
    the x-axis, and continue along this axis as long as there are no free cells. If it reaches the
    end it will continue from the beginning of the next line on the y-axis.

    If no empty cell is found the tuple (-1, -1) will be returned.

    :param board: The board to search
    :param x: The zero based starting x coordinate to search from
    :param y: The zero based starting y coordinate to search from
    :return: Returns a tuple of the x and y coordinates of the next free cell
    """
    col = x
    row = y
    while True:
        col += 1
        if col > 8:
            col = 0
            row += 1
        if row > 8:
            return -1, -1
        if board[row][col] == 0:
            return col, row


def validate_rows(board: Board) -> bool:
    """ Validates rows on the board, verifying that no duplicates exist on a single row.

    Only filled out cells will be validated, meaning a half filled out row can be valid provided it
    does not contain any duplicates. This method only searches for duplicates, and stops searching
    as soon as it discovers one.

    :param board: The board to validate
    :return: Returns a boolean True if no rows contain any duplicates
    """
    for col in range(9):
        row_set = set()
        for row in range(9):
            value = board[row][col]
            if value != 0:
                if value in row_set:
                    return False
                row_set.add(value)
    return True


def validate_cols(board: Board) -> bool:
    """ Validates columns on the board, verifying that no duplicates exist on a single column.

    Only filled out cells will be validated, meaning a half filled out column can be valid provided
    it does not contain any duplicates. This method only searches for duplicates, and stops
    searching as soon as it discovers one.

    :param board: The board to validate
    :return: Returns a boolean True if no columns contain any duplicates
    """
    for row in range(9):
        col_set = set()
        for value in board[row]:
            if value != 0:
                if value in col_set:
                    return False
                col_set.add(value)
    return True


def validate_nonets(board: Board) -> bool:
    """ Validates nonets on the board, verifying that no duplicates exist on a nonet.

    Only filled out cells will be validated, meaning a half filled out nonet can be valid provided
    it does not contain any duplicates. This method only searches for duplicates, and stops
    searching as soon as it discovers one.

    :param board: The board to validate
    :return: Returns a boolean True if no duplicates exist in any nonet
    """
    for nonet_x in range(0, 9, 3):
        range_x = find_nonet_range(nonet_x)
        for nonet_y in range(0, 9, 3):
            nonet_set = set()
            for y in find_nonet_range(nonet_y):
                for x in range_x:
                    value = board[y][x]
                    if value != 0:
                        if value in nonet_set:
                            return False
                        nonet_set.add(value)
    return True


def validate_cages(board: Board, cages: Cages) -> bool:
    """ Validates all cages, verifying that no duplicates exist in these, and that the sum equals
    cage desired total.

    The method iterates through all cages, to test for both duplicates but also the total sum
    within the cage. Only filled out values are examined, so a cage can be valid if it does not
    contain duplicates and are not filled out entirely. If all fields are filled out the total sum
    of the cage is examined and if it does not equal the desired sum of the cage, the method
    will return a boolean False.

    This check could be imposed for unfinished cages as well, where a sum that is higher than, or
    too high to be achieved with the available unclaimed values, would result in a fail. Since this
    method is only really used for leaf nodes, that have all fields filled out, it would not make
    sense to make it more expensive by checking this as well. In other words it would hurt
    performance, and therefor is not done.

    :param board: The board to extract values from
    :param cages: The cages to validate
    :return: Returns a boolean True if no duplicates are found in a cage, and the total equals the
             valid cage total
    """
    for total, fields in cages:
        cage_set = set()
        for x, y in fields:
            value = board[y][x]
            if value != 0:
                if value in cage_set:
                    return False
                cage_set.add(value)
        if len(cage_set) == len(fields):
            if sum(cage_set) != total:
                return False
    return True


def validate(board: Board, cages: Cages) -> bool:
    """ Validate the columns, rows, nonets and cages on the board.

    Validates the columns, rows, nonets and fields in that order. If any of these are not valid the
    function will break out immediately to save processing power. The validation can validate an
    unfinished board, as long as it does not contain any duplicates it will be marked as valid. So
    for a board to be completely valid and finished it must be valid with no empty cells left.

    :param board: The board to validate
    :param cages: The cages to validate
    :return: Returns a boolean True if the board is valid
    """
    global validations_performed
    validations_performed += 1

    return validate_cols(board) and validate_rows(board) and validate_nonets(board) and \
        validate_cages(board, cages)


def fill_out_next(board: Board, cages: Cages, cage_cache: Board,
                  minmax_cache: MinMaxCache, x: int, y: int) -> bool:
    """ Fill out the next value on the board, and if all values are filled out validate the board.

    If the field at (x, y) is already filled out the method will raise an AssertionError.

    This method works by basically taking one value that is not already conflicting with an existing
    value in the row, column, nonet or cage of the coordinate. Apply the value and call itself
    recursively for the next cell, until all cells are filled out, at which point it back-tracks
    and tries the next value available.

    :param board: The board to fill out
    :param cages: The cages to respect
    :param cage_cache: The look-up cage cache
    :param minmax_cache: The min/max value limits to use for limiting search size
    :param x: The zero based x coordinate to fill out
    :param y: The zero based y coordinate to fill out
    :return: Returns a boolean True if this board is valid, and False if it could never be in its
             current form
    """
    if board[y][x] != 0:
        raise AssertionError(f"Field ({x}, {y}) is not empty")

    global combinations_tried
    combinations_tried += 1

    next_x, next_y = find_next_cell(board, x, y)
    taken_values = find_taken_value(board, cages, cage_cache, x, y)

    # If more than one value remains go through all values in the range min to max, and skip the
    # ones that are already taken, reserved (needed elsewhere), or out of reach (too high or low for
    # the cage). If only one value remains, then the taken values list will include all the values
    # that it cannot be, and only one iteration will be completed
    min_value, max_value = minmax_cache[y][x]
    for value in range(min_value, max_value + 1):
        if value not in taken_values:
            board[y][x] = value
            if next_x == -1:
                success = validate(board, cages)
                if not success:
                    board[y][x] = 0
                return success
            if fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y):
                return True
    board[y][x] = 0
    return False


def solve(board: Board, cages: Cages) -> bool:
    """ Solve Sudoku from board and cages

    The method will return a boolean true if the board was solved, or false if it for some reason
    was not possible to solve it. The board parameter will be updated to reflect the solution, when
    the function exits.

    :param board: The initial board to use
    :param cages: The cages of that board
    :return: Returns a boolean true if the Sudoku could be resolved
    """

    # Create look-up caches to speed up the process of finding cages and limiting the possible
    # values of each cell.
    cage_cache = []
    minmax_cache = []
    for y in range(9):
        cage_row = []
        minmax_row = []
        for x in range(9):
            cage_row.append(find_cage_index(cages, x, y))
            minmax_row.append(find_minmax_value(cages, x, y))
        cage_cache.append(cage_row)
        minmax_cache.append(minmax_row)

    # Fill out single cages, we start by doing this, since these are easy to isolate, and will
    # give us a smaller search range
    for total, fields in cages:
        if len(fields) == 1:
            x, y = fields[0]
            board[y][x] = total

    # The fill out next method expects the field to be empty, so ensure that the field we start with
    # are actually empty.
    next_x, next_y = 0, 0
    if board[next_x][next_y] != 0:
        next_x, next_y = find_next_cell(board, next_x, next_y)

    return fill_out_next(board, cages, cage_cache, minmax_cache, next_x, next_y)


def load_from_file(filename: str) -> tuple[Board, Cages]:
    """ Loads board and cage data from a JSON file.

    :param filename: The name of the file to load the board and cage data from
    :return: Returns a tuple of board and cages from the file
    """
    with open(filename) as board_file:
        data = json.load(board_file)

        # Convert cages from basic JSON to useful tuples
        cages = []
        for total, fields in data["cages"]:
            tuples = []
            for x, y in fields:
                tuples.append((x, y))
            cages.append((total, tuples))
        return data["board"], cages


def run_solver(filenames: list[str], show_stats: bool = False, benchmark: bool = False,
               show_initial_board: bool = False) -> None:
    """Run the board solver for a list files.

    :param filenames: The list of file names to load and solve
    :param show_stats: Whether to show stats such as number of validations and unique combinations
    :param benchmark: Will output the time it takes for one iteration
    :param show_initial_board: Whetherh to show the board layout before solving it
    """
    for filename in filenames:
        global validations_performed, combinations_tried
        validations_performed, combinations_tried = 0, 0
        board, cages = load_from_file(filename=filename)
        print(f"Using board and cages from {filename}")
        if show_initial_board:
            print_board(board, cages)

        if benchmark:
            print("Benchmarking...")
            benchmark_result = timeit.timeit(lambda b=board, c=cages: solve(b, c), number=1)
            print_board(board, cages)
            print(f"Benchmarked solving {filename}: took: {benchmark_result} seconds")
        else:
            print("Calculating...")
            success = solve(board, cages)
            if success:
                print("SUCCESS")
            else:
                print("Unable to find solution")
            print_board(board, cages)

        if show_stats:
            print(f"Validations performed: {validations_performed}")
            print(f"Unique combinations tested: {combinations_tried}")
