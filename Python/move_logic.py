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
