import utils
import board_utils

starting_white = [
    "-4 5 -1",
    "-3 4 -1",
    "-2 3 -1",
    "-1 2 -1",
    "0 1 -1",
    "1 1 -2",
    "2 1 -3",
    "3 1 -4",
    "4 1 -5"
]
starting_black = [
    "-4 -1 5",
    "-3 -1 4",
    "-2 -1 3",
    "-1 -1 2",
    "0 -1 1",
    "1 -2 1",
    "2 -3 1",
    "3 -4 1",
    "4 -5 1"
]
white_promotion = [
    "-5 0 5",
    "-4 -1 5",
    "-3 -2 5",
    "-2 -3 5",
    "-1 -4 5",
    "0 -5 5",
    "1 -5 4",
    "2 -5 3",
    "3 -5 2",
    "4 -5 1",
    "5 -5 0"
]
black_promotion = [
    "-5 5 0",
    "-4 5 -1",
    "-3 5 -2",
    "-2 5 -3",
    "-1 5 -4",
    "0 5 -5",
    "1 4 -5",
    "2 3 -5",
    "3 2 -5",
    "4 1 -5",
    "5 0 -5"
]


"""
    Validate the moves for pawns - left separate due to en passant shennanigans
"""
def move_like_white_pawn(starting_cell, fen, prev_fen):
    cells = board_utils.initialize_board(fen)
    valid_cells = []

    #Starting coordinates
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    #Necessary for checking if it's still on the starting cell of a friendly-colored pawn (and eventually promotion)
    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    #Cell values for each...
    one_cell_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] - 1, start_coords[2] + 1, fen)
    two_cells_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] - 2, start_coords[2] + 2, fen)
    upper_left = utils.get_cell_with_coordinates(start_coords[0] - 1, start_coords[1], start_coords[2] + 1, fen)
    upper_right = utils.get_cell_with_coordinates(start_coords[0] + 1, start_coords[1] - 1, start_coords[2], fen)

    en_passant_target = get_two_cell_move_white_enpassant(prev_fen, fen)
    en_passant_target_cell = None
    en_passant_passed_pawn = None

    #If the cell exists and it's not occupied...
    if one_cell_forward != None and cells[one_cell_forward].occupied_by == None:
        valid_cells.append(one_cell_forward)

    if one_cell_forward != None and two_cells_forward != None and (cells[two_cells_forward].occupied_by == None) and (cells[one_cell_forward].occupied_by == None) and (string_form_coords in starting_white):
        valid_cells.append(two_cells_forward)

    if upper_left != None and cells[upper_left].occupied_by != None and cells[upper_left].occupied_by.islower():    
       valid_cells.append(upper_left)

    if upper_right != None and cells[upper_right].occupied_by != None and cells[upper_right].occupied_by.islower():    
       valid_cells.append(upper_right)

    if (en_passant_target is not None) and (en_passant_target == upper_right or en_passant_target == upper_left):
        valid_cells.append(en_passant_target)
        en_passant_target_cell = en_passant_target or None
        en_passant_passed_pawn = en_passant_target + 11


    return (valid_cells, en_passant_target_cell, en_passant_passed_pawn)
def move_like_black_pawn(starting_cell, fen, prev_fen):
    cells = board_utils.initialize_board(fen)
    valid_cells = []
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    one_cell_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] + 1, start_coords[2] - 1, fen)
    two_cells_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] + 2, start_coords[2] - 2, fen)
    lower_left = utils.get_cell_with_coordinates(start_coords[0] - 1, start_coords[1] + 1, start_coords[2], fen)
    lower_right = utils.get_cell_with_coordinates(start_coords[0] + 1, start_coords[1], start_coords[2] - 1, fen)

    en_passant_target = get_two_cell_move_black_enpassant(prev_fen, fen)
    #en_passant_target_coords = utils.get_coordinates_from_cell(en_passant_target) if en_passant_target != None else None
    en_passant_target_cell = None
    en_passant_passed_pawn = None


    if one_cell_forward != None and cells[one_cell_forward].occupied_by == None:
        valid_cells.append(one_cell_forward)

    if one_cell_forward != None and two_cells_forward != None and (cells[two_cells_forward].occupied_by == None) and (cells[one_cell_forward].occupied_by == None) and (string_form_coords in starting_black):
        valid_cells.append(two_cells_forward)

    if lower_left != None and cells[lower_left].occupied_by != None and cells[lower_left].occupied_by.isupper():    
       valid_cells.append(lower_left)

    if lower_right != None and cells[lower_right].occupied_by != None and cells[lower_right].occupied_by.isupper():    
       valid_cells.append(lower_right)

    if (en_passant_target != None) and (en_passant_target == lower_left or en_passant_target == lower_right):
        valid_cells.append(en_passant_target)
        en_passant_target_cell = en_passant_target or None
        en_passant_passed_pawn = en_passant_target - 11
    

    return (valid_cells, en_passant_target_cell, en_passant_passed_pawn)

def move_like_bishop(starting_cell, fen, color):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    '''Upper Right'''
    upper_right_q = start_coords[0] + 1
    upper_right_r = start_coords[1] - 2
    upper_right_s = start_coords[2] + 1

    moves = 1

    while upper_right_q <= 5 and upper_right_r >= -5 and upper_right_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] - (moves * 2), start_coords[2] + moves, fen)
        
        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_right_q += 1
        upper_right_r -= 2
        upper_right_s += 1

    '''Right'''
    right_q = start_coords[0] + 2
    right_r = start_coords[1] - 1
    right_s = start_coords[2] - 1

    moves = 1

    while right_q <= 5 and right_r >= -5 and right_s >= -5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + (moves * 2), start_coords[1] - moves, start_coords[2] - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        right_q += 2
        right_r -= 1
        right_s -= 1

    '''Lower right'''
    lower_right_q = start_coords[0] + 1
    lower_right_r = start_coords[1] + 1
    lower_right_s = start_coords[2] - 2

    moves = 1

    while lower_right_q <= 5 and lower_right_r <= 5 and lower_right_s >= -5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] + moves, start_coords[2] - (moves * 2), fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_right_q += 1
        lower_right_r += 1
        lower_right_s -= 2

    '''Lower left'''
    lower_left_q = start_coords[0] - 1
    lower_left_r = start_coords[1] + 2
    lower_left_s = start_coords[2] - 1

    moves = 1

    while lower_left_q >= -5 and lower_left_r <= 5 and lower_left_s >= -5:
        cell =  utils.get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] + (moves * 2), start_coords[2] - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_left_q -= 1
        lower_left_r += 2
        lower_left_s -= 1

    '''Left'''
    left_q = start_coords[0] - 2
    left_r = start_coords[1] + 1
    left_s = start_coords[2] + 1

    moves = 1

    while left_q >= -5 and left_r <= 5 and left_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] - (moves * 2), start_coords[1] + moves, start_coords[2] + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        left_q -= 2
        left_r += 1
        left_s += 1

    '''Upper left'''
    upper_left_q = start_coords[0] - 1
    upper_left_r = start_coords[1] - 1
    upper_left_s = start_coords[2] + 2

    moves = 1

    while upper_left_q >= -5 and upper_left_r >= -5 and upper_left_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] - moves, start_coords[2] + (moves * 2), fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_left_q -= 1
        upper_left_r -= 1
        upper_left_s += 2

    return valid_cells

def move_like_knight(starting_cell, fen, color):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    new_coords = [
        #Forward
        [1, -3, 2],#Right
        [-1, -2, 3],#Left
        
        #Backward
        [1, 2, -3],#Right
        [-1, 3, -2],#Left
        
        #Upper right diagonal
        [2, -3, 1],#Up
        [3, -2, -1],#Down
        
        #Bottom right diagonal
        [3, -1, -2],#Up
        [2, 1, -3],#Down
        
        #Upper left diagonal
        [-2, -1, 3],#Up
        [-3, 1, 2],#Down
        
        #Bottom left diagonal
        [-3, 2, 1],#Up
        [-2, 3, -1]#Down
    ]

    
    for j in range(len(new_coords)):
        target_cell = utils.get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)
        if color == 'black':
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.isupper()):
                valid_cells.append(target_cell)
        
        else:
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.islower()):
                valid_cells.append(target_cell)

    return valid_cells

def move_like_rook(starting_cell, fen, color):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)
    q = start_coords[0]
    r = start_coords[1]
    s = start_coords[2]

    valid_cells = []

    '''Upper Left'''
    upper_left_q = q - 1
    upper_left_s = s + 1

    moves = 1

    while upper_left_q >= -5 and upper_left_s <= 5:
        cell = utils.get_cell_with_coordinates(q - moves, r, s + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_left_q -= 1
        upper_left_s += 1

    '''Forward'''

    up_r = r - 1
    up_s = s + 1

    moves = 1

    while up_r >= -5 and up_s <= 5:
        cell = utils.get_cell_with_coordinates(q, r - moves, s + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        up_r -= 1
        up_s += 1

    '''Upper Right'''

    upper_right_q = q + 1
    upper_right_r = r - 1

    moves = 1

    while upper_right_q <= 5 and upper_right_r >= -5:
        cell = utils.get_cell_with_coordinates(q + moves, r - moves, s, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_right_q += 1
        upper_right_r -= 1

    '''Lower Right'''

    lower_right_q = q + 1
    lower_right_s = s - 1

    moves = 1

    while lower_right_q <= 5 and lower_right_s >= -5:
        cell = utils.get_cell_with_coordinates(q + moves, r, s - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_right_q += 1
        lower_right_s -= 1

    '''Bottom'''

    b_r = r + 1
    b_s = s - 1

    moves = 1

    while b_r <= 5 and b_s >= -5:
        cell = utils.get_cell_with_coordinates(q, r + moves, s - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        b_r += 1
        b_s -= 1

    '''Bottom left'''

    bottom_left_q = q - 1
    bottom_left_r = r + 1

    moves = 1

    while bottom_left_q >= -5 and bottom_left_r <= 5:
        cell = utils.get_cell_with_coordinates(q - moves, r + moves, s, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            if (color == 'white' and cells[cell].occupied_by.islower()) or (color == 'black' and cells[cell].occupied_by.isupper()):
                valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        bottom_left_q -= 1
        bottom_left_r += 1

    return valid_cells

def move_like_king(starting_cell, fen, color):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    new_coords = [
        [0, -1, 1],  #Forward
        [0, 1, -1],  #Backward
        [1, -1, 0],  #Upper right
        [1, 0, -1],  #Lower right
        [-1, 0, 1],  #Upper left
        [-1, 1, 0],  #Lower left
        [-1, -1, 2], #Upper left diagonal
        [1, -2, 1],  #Upper right diagonal
        [2, -1, -1], #Right diagonal
        [1, 1, -2],  #Lower right diagonal
        [-1, 2, -1], #Lower left diagonal
        [-2, 1, 1],  #Left diagonal
    ]

    
    for j in range(len(new_coords)):
        target_cell = utils.get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)
        if color == 'black':
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.isupper()):
                valid_cells.append(target_cell)
        
        else:
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.islower()):
                valid_cells.append(target_cell)

    return valid_cells

def move_like_queen(starting_cell, fen, color):
    valid_cells = []

    bishop_moves = move_like_bishop(starting_cell, fen, color)
    rook_moves = move_like_rook(starting_cell, fen, color)

    valid_cells = bishop_moves + rook_moves

    return valid_cells

"""
    Updated 'move like' functions to create dependency map (occupied cells should be opposite or friendly color)

    COME BACK TO THIS (I think I'm going to be trying to move pieces out of the way of a pawn that is 'attacking' even
    though it is simply moving forward and can't attack in that direction.  I could be wrong, experiment)

    There may be an issue here with the cells in front of the pawn not being in the attack map, but I think that's fair since the
    pawn can't 'attack' there, it simply can move there.  Keep an eye out for problemos
"""

def dependency_map_white_pawn(starting_cell, fen, prev_fen):
    cells = board_utils.initialize_board(fen)
    valid_cells = []

    #Starting coordinates
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    #Necessary for checking if it's still on the starting cell of a friendly-colored pawn (and eventually promotion)
    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    #Cell values for each...
    one_cell_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] - 1, start_coords[2] + 1, fen)
    two_cells_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] - 2, start_coords[2] + 2, fen)
    upper_left = utils.get_cell_with_coordinates(start_coords[0] - 1, start_coords[1], start_coords[2] + 1, fen)
    upper_right = utils.get_cell_with_coordinates(start_coords[0] + 1, start_coords[1] - 1, start_coords[2], fen)

    en_passant_target = get_two_cell_move_white_enpassant(prev_fen, fen)
    en_passant_target_cell = None
    en_passant_passed_pawn = None

    #If the cell exists and it's not occupied...
    if one_cell_forward != None and cells[one_cell_forward].occupied_by == None:
        valid_cells.append(one_cell_forward)

    if one_cell_forward != None and two_cells_forward != None and (cells[two_cells_forward].occupied_by == None) and (cells[one_cell_forward].occupied_by == None) and (string_form_coords in starting_white):
        valid_cells.append(two_cells_forward)

    #Since these cells could change attack map if it was occupied and is now not, or wasn't and now is, all I care
    #about is that the cell exists
    if upper_left != None:    
       valid_cells.append(upper_left)

    if upper_right != None:    
       valid_cells.append(upper_right)

    if (en_passant_target is not None) and (en_passant_target == upper_right or en_passant_target == upper_left):
        valid_cells.append(en_passant_target)
        en_passant_target_cell = en_passant_target or None
        en_passant_passed_pawn = en_passant_target + 11


    return (valid_cells, en_passant_target_cell, en_passant_passed_pawn)
def dependency_map_black_pawn(starting_cell, fen, prev_fen):
    cells = board_utils.initialize_board(fen)
    valid_cells = []
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    one_cell_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] + 1, start_coords[2] - 1, fen)
    two_cells_forward = utils.get_cell_with_coordinates(start_coords[0], start_coords[1] + 2, start_coords[2] - 2, fen)
    lower_left = utils.get_cell_with_coordinates(start_coords[0] - 1, start_coords[1] + 1, start_coords[2], fen)
    lower_right = utils.get_cell_with_coordinates(start_coords[0] + 1, start_coords[1], start_coords[2] - 1, fen)

    en_passant_target = get_two_cell_move_black_enpassant(prev_fen, fen)
    #en_passant_target_coords = utils.get_coordinates_from_cell(en_passant_target) if en_passant_target != None else None
    en_passant_target_cell = None
    en_passant_passed_pawn = None


    if one_cell_forward != None and cells[one_cell_forward].occupied_by == None:
        valid_cells.append(one_cell_forward)

    if one_cell_forward != None and two_cells_forward != None and (cells[two_cells_forward].occupied_by == None) and (cells[one_cell_forward].occupied_by == None) and (string_form_coords in starting_black):
        valid_cells.append(two_cells_forward)

    #Just gotta make sure the cell exists since any updated state in it could change attack map
    if lower_left != None:    
       valid_cells.append(lower_left)

    if lower_right != None:    
       valid_cells.append(lower_right)

    if (en_passant_target != None) and (en_passant_target == lower_left or en_passant_target == lower_right):
        valid_cells.append(en_passant_target)
        en_passant_target_cell = en_passant_target or None
        en_passant_passed_pawn = en_passant_target - 11
    

    return (valid_cells, en_passant_target_cell, en_passant_passed_pawn)

"""
    Just removed the constraint that a piece can't land on it's friendly color, since an update in this (occupied) cell
    changes the attack map

    True for the rest of the pieces
"""
def dependency_map_bishop(starting_cell, fen):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    '''Upper Right'''
    upper_right_q = start_coords[0] + 1
    upper_right_r = start_coords[1] - 2
    upper_right_s = start_coords[2] + 1

    moves = 1

    while upper_right_q <= 5 and upper_right_r >= -5 and upper_right_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] - (moves * 2), start_coords[2] + moves, fen)
        
        #If it's occupied, (we don't care by whom) append the cell and then prevent from moving to next cells.
        #An update in the blocked cells won't matter if we can't get past the initial blocker
        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_right_q += 1
        upper_right_r -= 2
        upper_right_s += 1

    '''Right'''
    right_q = start_coords[0] + 2
    right_r = start_coords[1] - 1
    right_s = start_coords[2] - 1

    moves = 1

    while right_q <= 5 and right_r >= -5 and right_s >= -5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + (moves * 2), start_coords[1] - moves, start_coords[2] - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        right_q += 2
        right_r -= 1
        right_s -= 1

    '''Lower right'''
    lower_right_q = start_coords[0] + 1
    lower_right_r = start_coords[1] + 1
    lower_right_s = start_coords[2] - 2

    moves = 1

    while lower_right_q <= 5 and lower_right_r <= 5 and lower_right_s >= -5:
        cell = utils.get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] + moves, start_coords[2] - (moves * 2), fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_right_q += 1
        lower_right_r += 1
        lower_right_s -= 2

    '''Lower left'''
    lower_left_q = start_coords[0] - 1
    lower_left_r = start_coords[1] + 2
    lower_left_s = start_coords[2] - 1

    moves = 1

    while lower_left_q >= -5 and lower_left_r <= 5 and lower_left_s >= -5:
        cell =  utils.get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] + (moves * 2), start_coords[2] - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_left_q -= 1
        lower_left_r += 2
        lower_left_s -= 1

    '''Left'''
    left_q = start_coords[0] - 2
    left_r = start_coords[1] + 1
    left_s = start_coords[2] + 1

    moves = 1

    while left_q >= -5 and left_r <= 5 and left_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] - (moves * 2), start_coords[1] + moves, start_coords[2] + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        left_q -= 2
        left_r += 1
        left_s += 1

    '''Upper left'''
    upper_left_q = start_coords[0] - 1
    upper_left_r = start_coords[1] - 1
    upper_left_s = start_coords[2] + 2

    moves = 1

    while upper_left_q >= -5 and upper_left_r >= -5 and upper_left_s <= 5:
        cell = utils.get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] - moves, start_coords[2] + (moves * 2), fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_left_q -= 1
        upper_left_r -= 1
        upper_left_s += 2

    return valid_cells
def dependency_map_knight(starting_cell, fen):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    new_coords = [
        #Forward
        [1, -3, 2],#Right
        [-1, -2, 3],#Left
        
        #Backward
        [1, 2, -3],#Right
        [-1, 3, -2],#Left
        
        #Upper right diagonal
        [2, -3, 1],#Up
        [3, -2, -1],#Down
        
        #Bottom right diagonal
        [3, -1, -2],#Up
        [2, 1, -3],#Down
        
        #Upper left diagonal
        [-2, -1, 3],#Up
        [-3, 1, 2],#Down
        
        #Bottom left diagonal
        [-3, 2, 1],#Up
        [-2, 3, -1]#Down
    ]

    
    for j in range(len(new_coords)):
        target_cell = utils.get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)

        if target_cell is not None and cells[target_cell] is not None:
            valid_cells.append(target_cell)

    return valid_cells
def dependency_map_rook(starting_cell, fen):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)
    q = start_coords[0]
    r = start_coords[1]
    s = start_coords[2]

    valid_cells = []

    '''Upper Left'''
    upper_left_q = q - 1
    upper_left_s = s + 1

    moves = 1

    while upper_left_q >= -5 and upper_left_s <= 5:
        cell = utils.get_cell_with_coordinates(q - moves, r, s + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_left_q -= 1
        upper_left_s += 1

    '''Forward'''

    up_r = r - 1
    up_s = s + 1

    moves = 1

    while up_r >= -5 and up_s <= 5:
        cell = utils.get_cell_with_coordinates(q, r - moves, s + moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        up_r -= 1
        up_s += 1

    '''Upper Right'''

    upper_right_q = q + 1
    upper_right_r = r - 1

    moves = 1

    while upper_right_q <= 5 and upper_right_r >= -5:
        cell = utils.get_cell_with_coordinates(q + moves, r - moves, s, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        upper_right_q += 1
        upper_right_r -= 1

    '''Lower Right'''

    lower_right_q = q + 1
    lower_right_s = s - 1

    moves = 1

    while lower_right_q <= 5 and lower_right_s >= -5:
        cell = utils.get_cell_with_coordinates(q + moves, r, s - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        lower_right_q += 1
        lower_right_s -= 1

    '''Bottom'''

    b_r = r + 1
    b_s = s - 1

    moves = 1

    while b_r <= 5 and b_s >= -5:
        cell = utils.get_cell_with_coordinates(q, r + moves, s - moves, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        b_r += 1
        b_s -= 1

    '''Bottom left'''

    bottom_left_q = q - 1
    bottom_left_r = r + 1

    moves = 1

    while bottom_left_q >= -5 and bottom_left_r <= 5:
        cell = utils.get_cell_with_coordinates(q - moves, r + moves, s, fen)

        if cell is not None and cells[cell].occupied_by is not None:
            valid_cells.append(cell)
            break

        valid_cells.append(cell)

        moves += 1
        bottom_left_q -= 1
        bottom_left_r += 1

    return valid_cells
def dependency_map_king(starting_cell, fen):
    cells = board_utils.initialize_board(fen)
    start_coords = utils.get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    new_coords = [
        [0, -1, 1],  #Forward
        [0, 1, -1],  #Backward
        [1, -1, 0],  #Upper right
        [1, 0, -1],  #Lower right
        [-1, 0, 1],  #Upper left
        [-1, 1, 0],  #Lower left
        [-1, -1, 2], #Upper left diagonal
        [1, -2, 1],  #Upper right diagonal
        [2, -1, -1], #Right diagonal
        [1, 1, -2],  #Lower right diagonal
        [-1, 2, -1], #Lower left diagonal
        [-2, 1, 1],  #Left diagonal
    ]

    
    for j in range(len(new_coords)):
        target_cell = utils.get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)

        if target_cell is not None and cells[target_cell] is not None:
            valid_cells.append(target_cell)

    return valid_cells
def dependency_map_queen(starting_cell, fen):
    valid_cells = []

    bishop_moves = dependency_map_bishop(starting_cell, fen)
    rook_moves = dependency_map_rook(starting_cell, fen)

    valid_cells = bishop_moves + rook_moves

    return valid_cells

"""
    Determine if a pawn moved two cells in the previous move to check for en passant logic
"""
def get_two_cell_move_black_enpassant(prev_fen, current_fen):

    #Used for checking if one pawn moved two cells in the last move
    previous_cells = board_utils.initialize_board(prev_fen)
    current_cells = board_utils.initialize_board(current_fen)

    en_passant_target_cell = None

    #Get every cell that a pawn existed on last move
    previous_pawn_cells = [previous_cells[cell].num for cell in previous_cells if previous_cells[cell].occupied_by == 'P']
    #And ever cell that a pawn exists on now
    current_pawn_cells = [current_cells[cell].num for cell in current_cells if current_cells[cell].occupied_by == 'P']

    #Look at each current cell and see if two cells 'behind' was occupied by a pawn last move
    for current_cell in current_pawn_cells:
        double_move_start = current_cell + 22

        if double_move_start in previous_pawn_cells and current_cells[double_move_start].occupied_by == None:
            en_passant_target_cell = double_move_start - 11
        

    #If so, the target cell for en passant is in between them
    return en_passant_target_cell
def get_two_cell_move_white_enpassant(prev_fen, current_fen):
    previous_cells = board_utils.initialize_board(prev_fen)
    current_cells = board_utils.initialize_board(current_fen)

    en_passant_target_cell = None

    previous_pawn_cells = [previous_cells[cell].num for cell in previous_cells if previous_cells[cell].occupied_by == 'p']
    current_pawn_cells = [current_cells[cell].num for cell in current_cells if current_cells[cell].occupied_by == 'p']

    #print("Prev: " + str(previous_pawn_cells))
    #print("Cur: " + str(current_pawn_cells))

    for current_cell in current_pawn_cells:
        double_move_start = current_cell - 22

        if double_move_start in previous_pawn_cells and current_cells[double_move_start].occupied_by == None:
            en_passant_target_cell = double_move_start + 11
        

    return en_passant_target_cell

"""
    Find all legal moves for any piece type (all legal moves for both knights, both bishops, all pawns, etc)
"""
def find_all_legal(fen, prev_fen, piece):

    cells = board_utils.initialize_board(fen)

    #Get every cell that contains each piece type
    white_pawn_cells = [cell for cell in cells if cells[cell].occupied_by == 'P']
    black_pawn_cells = [cell for cell in cells if cells[cell].occupied_by == 'p']
    white_knight_cells = [cell for cell in cells if cells[cell].occupied_by == 'N']
    black_knight_cells = [cell for cell in cells if cells[cell].occupied_by == 'n']
    white_bishop_cells = [cell for cell in cells if cells[cell].occupied_by == 'B']
    black_bishop_cells = [cell for cell in cells if cells[cell].occupied_by == 'b']
    white_rook_cells = [cell for cell in cells if cells[cell].occupied_by == 'R']
    black_rook_cells = [cell for cell in cells if cells[cell].occupied_by == 'r']
    white_queen_cells = [cell for cell in cells if cells[cell].occupied_by == 'Q']
    black_queen_cells = [cell for cell in cells if cells[cell].occupied_by == 'q']
    white_king_cells = [cell for cell in cells if cells[cell].occupied_by == 'K']
    black_king_cells = [cell for cell in cells if cells[cell].occupied_by == 'k']

    if piece == 'P':
        valid_moves = []

        #For every pawn on the board...
        for i in range(len(white_pawn_cells)):
            #Find where pawn 'i' can move to
            moves = move_like_white_pawn(cells[white_pawn_cells[i]].num, fen, prev_fen)[0]
            
            #Ensure that each move doesn't produce a check
            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, cells[white_pawn_cells[i]].num, move) == 'white'
            ]

        return valid_moves

    if piece == 'p':
        valid_moves = []

        for i in range(len(black_pawn_cells)):

            moves = move_like_black_pawn(cells[black_pawn_cells[i]].num, fen, prev_fen)[0]

            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, cells[black_pawn_cells[i]].num, move) == 'black'
            ]

        return valid_moves
    
    #Check both knights
    if piece == 'N' or piece == 'n':
        valid_moves = []
        #We only want the list of starting cells that hold the piece of the right color!
        cell_list = white_knight_cells if piece == 'N' else black_knight_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_knight(starting_cell, fen, 'white' if piece.isupper() else 'black')

            #Make sure we're not putting ourselves in check
            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'B' or piece == 'b':
        valid_moves = []
        cell_list = white_bishop_cells if piece == 'B' else black_bishop_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_bishop(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'R' or piece == 'r':
        valid_moves = []
        cell_list = white_rook_cells if piece == 'R' else black_rook_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_rook(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'Q' or piece == 'q':
        valid_moves = []
        cell_list = white_queen_cells if piece == 'Q' else black_queen_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_queen(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'K' or piece == 'k':
        valid_moves = []
        cell_list = white_king_cells if piece == 'K' else black_king_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_king(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not utils.simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves

"""
    Find all legal moves (considering check) for whatever piece is occupying a given cell
"""
def find_legal_from_cell(fen, prev_fen, cell):
    cells = board_utils.initialize_board(fen)
    piece = cells[cell].occupied_by

    if not piece:
        return []

    is_white = piece.isupper()

    if piece == 'P' or piece == 'p':
        # Get moves and en passant target cell if applicable
        move_data = move_like_white_pawn(cell, fen, prev_fen) if is_white else move_like_black_pawn(cell, fen, prev_fen)
        moves, en_passant_target, en_passant_occupy = move_data[0], move_data[1] if len(move_data) > 1 else None, move_data[2] if len(move_data) > 1 else None
        en_passant_flag = en_passant_target is not None

        # Filter moves to avoid placing own king in check
        legal_moves = [
            move for move in moves if utils.simulate_move(fen, cell, move) != ('white' if is_white else 'black')
        ]
        
        # Return legal moves with en passant data
        return legal_moves, en_passant_target, en_passant_occupy, en_passant_flag

    # Handle moves for non-pawn pieces
    elif piece == 'N' or piece == 'n':
        moves = move_like_knight(cell, fen, 'white' if is_white else 'black')
    elif piece == 'B' or piece == 'b':
        moves = move_like_bishop(cell, fen, 'white' if is_white else 'black')
    elif piece == 'R' or piece == 'r':
        moves = move_like_rook(cell, fen, 'white' if is_white else 'black')
    elif piece == 'Q' or piece == 'q':
        moves = move_like_queen(cell, fen, 'white' if is_white else 'black')
    elif piece == 'K' or piece == 'k':
        moves = move_like_king(cell, fen, 'white' if is_white else 'black')
    else:
        return None  # In case of an unrecognized piece

    # Filter moves to avoid placing own king in check
    legal_moves = [
        move for move in moves if utils.simulate_move(fen, cell, move) != ('white' if is_white else 'black')
    ]
    
    # Return only legal moves for non-pawn pieces
    return legal_moves
