def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys.
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


def make_beginning_board(dimensions, value):
    """
    Takes in a tuple of dimensions and returns a table of the value
    """
    if not dimensions:
        return value
    else:
        return [
            make_beginning_board(dimensions[1:], value)
            for index in range(dimensions[0])
        ]


def possible_pairs(coordinates, dimensions):
    """
    Takes in a tuple coordinate with the row and column.
    Also takes in a tuple with the dimensions of the game.
    Returns a list of lists of possible locations for rows, and cols
    [[r-1,r,r+1],[c-1,]]
    """
    possible = []
    for index, coord in enumerate(coordinates):
        onetype = [coord]
        if coord - 1 >= 0:
            onetype.append(coord - 1)
        if coord + 1 <= dimensions[index] - 1:
            onetype.append(coord + 1)

        possible.append(onetype)
    # returns 2D list
    return possible


def permutation(possible):
    """
    Takes in possible locations that is created
    with the method possible_pairs().
    Returns a 2d list of different combinations.
    [[r-1, r, r+1], [c-1, c+1]] -> [[r-1,c-1], [r,c-1], [r+1, c-1],etc...]
    [0, [0,1]]
    """
    # base case. If length == 1, return first index
    if len(possible) == 1:
        return [[coord] for coord in possible[0]]
    else:
        # iterates through and uses recursion to append the items to new list
        new_list = []
        for item in possible[0]:
            for rest in permutation(possible[1:]):
                new_list.append([item, *rest])
        return new_list


def all_possible_coord(dimensions):
    """
    Takes in a tuple of dimensions and returns
    every coordinate that can be in the dimension
    """
    # base case
    if len(dimensions) == 0:
        return [[]]

    # recursive case
    else:
        sub_coordinates = all_possible_coord(dimensions[1:])
        coordinates = []
        for i in range(dimensions[0]):
            for sub_coord in sub_coordinates:
                coordinates.append([i] + sub_coord)
        return coordinates


def get_value_at_local(nlist, coordinates):
    """
    Takes in a n dimensional list and a n dimensional tuple of coordinates.
    Returns the value from the n dimensional list
    """
    value = nlist[:]

    # loops through the coordinates
    for coord in coordinates:
        value = value[coord]

    return value


def set_value_at_local(nlist, coordinates, value):
    """
    Takes in a n dimensional list, a n dimensional
    tuple of coordinates, and a value.
    Sets the value to the coordinate in the n dimensional list
    """
    # base case
    if len(coordinates) == 1:
        nlist[coordinates[0]] = value

    # recursive case
    else:
        return set_value_at_local(nlist[coordinates[0]], coordinates[1:], value)


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary
    """
    # creates a board with correct dimensions that is only occupied with 0
    board = make_beginning_board(dimensions, 0)

    # adds mines to starting board
    for mine_local in mines:
        set_value_at_local(board, mine_local, ".")

    # creates a visibility board with False
    visible = make_beginning_board(dimensions, False)

    for coordinate in all_possible_coord(dimensions):
        # checks if the coordinate is currently 0
        if get_value_at_local(board, coordinate) == 0:
            neighbor_mines = 0
            # calls permutation and possible pairs
            neighbors = permutation(possible_pairs(coordinate, dimensions))

            # iterates through potential neighbors
            for neighbor in neighbors:
                # if there is a mine, increases the counter by one
                if get_value_at_local(board, neighbor) == ".":
                    neighbor_mines += 1

            # updates the board with the number of mines
            set_value_at_local(board, coordinate, neighbor_mines)

    return {
        "dimensions": dimensions,
        "board": board,
        "visible": visible,
        "state": "ongoing",
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed
    """
    # checks if already won/lost
    if (
        game["state"] in {"defeat", "victory"}
        or get_value_at_local(game["visible"], coordinates)
    ):
        return 0

    # checks if lost
    if get_value_at_local(game["board"], coordinates) == ".":
        game["state"] = "defeat"
        set_value_at_local(game["visible"], coordinates, True)
        return 1

    def recursive_dig(coordinates):
        revealed = 1
        if get_value_at_local(game["visible"], coordinates):
            return 0

        set_value_at_local(game["visible"], coordinates, True)

        # if the coord 0, checks if other cells are also not visible
        if get_value_at_local(game["board"], coordinates) == 0:
            neighbors = permutation(possible_pairs(coordinates, game["dimensions"]))

            # recursively calls dig_nd for neighbors that are not visible and not mines
            for neighbor in neighbors:
                revealed += recursive_dig(neighbor)
        return revealed

    revealed = recursive_dig(coordinates)

    # calculates number of revealed squares/victory checker
    all_coord = all_possible_coord(game["dimensions"])
    for coord in all_coord:
        if get_value_at_local(game["board"], coord) != "." and not get_value_at_local(game["visible"], coord):
            break
    else:
        game["state"] = "victory"

    return revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)
    """
    dimensions = game["dimensions"]

    result = make_beginning_board(dimensions, "_")

    # iterates through the visibility board
    for coordinate in all_possible_coord(dimensions):
        if (
            all_visible is True
            or get_value_at_local(game["visible"], coordinate) is True
        ):
            if get_value_at_local(game["board"], coordinate) == ".":
                set_value_at_local(result, coordinate, ".")
                continue

            # appends " "
            if get_value_at_local(game["board"], coordinate) == 0:
                set_value_at_local(result, coordinate, " ")

            # appends string numbers
            else:
                set_value_at_local(
                    result,
                    coordinate,
                    str(get_value_at_local(game["board"], coordinate)),
                )

    # returns list
    return result


def play_game(game):
    """
    Play the game interactively, allowing the player to specify where to dig.

    The player will be asked for a coordinate (row, column) in a multi-dimensional game.
    The game continues until the player either wins or loses.

    Args:
       game (dict): The game state dictionary, including 'dimensions', 'board', 'state', 'visible', etc.
    """
    while game['state'] == 'ongoing':
        # Render the game board for the player to see
        print(render_nd(game))

        # Ask the player for the coordinates to dig (in multi-dimensional format)
        try:
            coordinates = input(f"Enter coordinates to dig (comma-separated): ").strip()
            coordinates = tuple(map(int, coordinates.split(',')))

            # Check if coordinates are valid within the dimensions of the game
            if not all(0 <= coord < dim for coord, dim in zip(coordinates, game['dimensions'])):
                print(f"Invalid coordinates. Please enter values within the dimensions {game['dimensions']}.")
                continue

            # Dig the specified location and get the number of revealed squares
            revealed_count = dig_nd(game, coordinates)
            
            # Inform the player of the number of squares revealed
            print(f"{revealed_count} square(s) revealed.")

        except ValueError:
            print("Invalid input. Please enter coordinates in the format 'row,col,etc...'.")
            continue

        # Check for victory or defeat and print the game state
        if game['state'] == 'defeat':
            print("You hit a mine! Game Over!")
            print(render_nd(game, all_visible=True))
            break
        elif game['state'] == 'victory':
            print("Congratulations! You win!")
            print(render_nd(game, all_visible=True))
            break
        else:
            print("Game is still ongoing. Keep playing!")


if __name__ == "__main__":
    # Start a multi-dimensional game example (e.g., 3D)
    game = new_game_nd((3, 3, 3), [(0, 0, 0), (2, 2, 2)])
    play_game(game)
