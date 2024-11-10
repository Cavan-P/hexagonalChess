from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import moveLogic
import copy
import random

app = Flask(__name__, static_folder='../static')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

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

@app.route('/find_legal_moves', methods=['POST'])
def find_legal_moves():
    move_data = request.json

    #Data that is sent from JS side
    fen_string = move_data['fen']
    prev_fen = move_data['prevFen']
    piece = move_data['piece']
    starting_cell = move_data['startingCell']

    #Current list of valid cell NUMBERS that the selected piece can move to
    valid_moves = []

    en_passant_target_cell = None #What cell will the pawn moving en passant land on
    en_passant_passed_pawn = None #What cell is the pawn being catpured currently on
    
    #Specify color of the piece being moved
    if piece.isupper():
        color = 'white'
    if piece.islower():
        color = 'black'

    #White pawn
    if piece == 'P':
        moves = move_like_white_pawn(starting_cell, fen_string, prev_fen)
        valid_moves = moves[0]
        en_passant_target_cell = moves[1]
        en_passant_passed_pawn = moves[2]

    #Black pawn
    elif piece == 'p':
        moves = move_like_black_pawn(starting_cell, fen_string, prev_fen)
        valid_moves = moves[0]
        en_passant_target_cell = moves[1]
        en_passant_passed_pawn = moves[2]

    elif piece == 'b' or piece == 'B':
        valid_moves = move_like_bishop(starting_cell, fen_string, color)

    elif piece == 'n' or piece == 'N':
        valid_moves = move_like_knight(starting_cell, fen_string, color)

    elif piece == 'r' or piece == 'R':
        valid_moves = move_like_rook(starting_cell, fen_string, color)

    elif piece == 'k' or piece == 'K':
        valid_moves = move_like_king(starting_cell, fen_string, color)

    elif piece == 'q' or piece == 'Q':
        valid_moves = move_like_queen(starting_cell, fen_string, color)

    #print(en_passant_target_cell, en_passant_passed_pawn)

    possible_moves = valid_moves


    #simulate_move returns the color of the side that's in check, False if no checks exist
    #This line ensures valid_moves only include moves that don't put the pieces' own color in check
    valid_moves = [
        move for move in possible_moves 
            if not ((piece.isupper() and simulate_move(fen_string, starting_cell, move) == 'white') or
            (piece.islower() and simulate_move(fen_string, starting_cell, move) == 'black'))
    ]

    #print("Found valid moves: " + str(valid_moves))
    #print("Found legal moves for piece: " + str(find_all_legal(fen_string, prev_fen, piece)))
    
    #Send back list of valid moves, and any necessary en passant information if it's applicable
    return jsonify({"moves": valid_moves, "enpassant": [en_passant_target_cell, en_passant_passed_pawn]})
    

@app.route('/drop_check', methods=['POST'])
def drop_check():
    data = request.get_json()

    #Data that is sent to verify if a chosen move is check
    fen = data['fen']
    prev_fen = data['prevFen']
    piece = data['piece']

    #Backwards piece color, because we're checking if the move made is opponent check
    color = 'black' if piece.isupper() else 'white'

    #'white' if white king is in check, 'black' if black is, and 'None' if there is no check on the board
    check = is_check(fen, color)
    moves_exist = False

    pieces = ('p n b r q k' if color == 'black' else 'P N B R Q K').split()

    #Find all legal moves for each piece type
    #If there are no moves, it's either checkmate or stalemate
    for i in pieces:
        if find_all_legal(fen, prev_fen, i):
            moves_exist = True
            break

    #Send back the color that is in check, and whether or not this color has any legal moves on the board
    return jsonify({'check': check, 'movesExist': moves_exist})


@app.route('/computer_move', methods=['POST'])
def computer_move():
    data = request.get_json()

    #Data sent from JS to get the computer's selected move
    fen = data['fen']
    prev_fen = data['prevFen']
    cells = moveLogic.initialize_board(fen)

    #What pieces does the computer still have on the board?
    living_black_pieces = {char for char in fen if char.islower()}

    #While there's still something left...
    while living_black_pieces:
        #Select random available piece type
        selected_piece = random.choice(list(living_black_pieces))

        #Get all cells that hold this piece
        selected_piece_cells = [cell for cell in cells if cells[cell].occupied_by == selected_piece]

        #Select a cell holding selected piece
        starting_cell = random.choice(selected_piece_cells) if len(selected_piece_cells) > 1 else selected_piece_cells[0]

        #Get all legal moves for this piece
        legal_cells = find_legal_from_cell(fen, prev_fen, starting_cell)

        #If this piece has a legal move, pick one of them, and send back the selected starting cell and selected target cell
        if legal_cells:
            target_cell = random.choice(legal_cells)
            return jsonify({'startingCell': starting_cell, 'targetCell': target_cell})
        
        #If there are no legal moves for the initial selected piece, remove that piece type from the list and try again
        print(f"No legal moves for {selected_piece}, reselecting...")
        living_black_pieces.remove(selected_piece)

    #No legal moves have been found
    return jsonify({'message': 'No legal moves available - likely checkmate or stalemate'})


"""
    Validate the moves for pawns - left separate due to en passant shennanigans
"""
def move_like_white_pawn(starting_cell, fen, prev_fen):
    cells = moveLogic.initialize_board(fen)
    valid_cells = []

    #Starting coordinates
    start_coords = get_coordinates_from_cell(starting_cell, fen)

    #Necessary for checking if it's still on the starting cell of a friendly-colored pawn (and eventually promotion)
    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    #Cell values for each...
    one_cell_forward = get_cell_with_coordinates(start_coords[0], start_coords[1] - 1, start_coords[2] + 1, fen)
    two_cells_forward = get_cell_with_coordinates(start_coords[0], start_coords[1] - 2, start_coords[2] + 2, fen)
    upper_left = get_cell_with_coordinates(start_coords[0] - 1, start_coords[1], start_coords[2] + 1, fen)
    upper_right = get_cell_with_coordinates(start_coords[0] + 1, start_coords[1] - 1, start_coords[2], fen)

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
    cells = moveLogic.initialize_board(fen)
    valid_cells = []
    start_coords = get_coordinates_from_cell(starting_cell, fen)

    string_form_coords = str(start_coords[0]) + " " + str(start_coords[1]) + " " + str(start_coords[2])

    one_cell_forward = get_cell_with_coordinates(start_coords[0], start_coords[1] + 1, start_coords[2] - 1, fen)
    two_cells_forward = get_cell_with_coordinates(start_coords[0], start_coords[1] + 2, start_coords[2] - 2, fen)
    lower_left = get_cell_with_coordinates(start_coords[0] - 1, start_coords[1] + 1, start_coords[2], fen)
    lower_right = get_cell_with_coordinates(start_coords[0] + 1, start_coords[1], start_coords[2] - 1, fen)

    en_passant_target = get_two_cell_move_black_enpassant(prev_fen, fen)
    #en_passant_target_coords = get_coordinates_from_cell(en_passant_target) if en_passant_target != None else None
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
    cells = moveLogic.initialize_board(fen)
    start_coords = get_coordinates_from_cell(starting_cell, fen)

    valid_cells = []

    '''Upper Right'''
    upper_right_q = start_coords[0] + 1
    upper_right_r = start_coords[1] - 2
    upper_right_s = start_coords[2] + 1

    moves = 1

    while upper_right_q <= 5 and upper_right_r >= -5 and upper_right_s <= 5:
        cell = get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] - (moves * 2), start_coords[2] + moves, fen)
        
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
        cell = get_cell_with_coordinates(start_coords[0] + (moves * 2), start_coords[1] - moves, start_coords[2] - moves, fen)

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
        cell = get_cell_with_coordinates(start_coords[0] + moves, start_coords[1] + moves, start_coords[2] - (moves * 2), fen)

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
        cell =  get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] + (moves * 2), start_coords[2] - moves, fen)

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
        cell = get_cell_with_coordinates(start_coords[0] - (moves * 2), start_coords[1] + moves, start_coords[2] + moves, fen)

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
        cell = get_cell_with_coordinates(start_coords[0] - moves, start_coords[1] - moves, start_coords[2] + (moves * 2), fen)

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
    cells = moveLogic.initialize_board(fen)
    start_coords = get_coordinates_from_cell(starting_cell, fen)

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
        target_cell = get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)
        if color == 'black':
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.isupper()):
                valid_cells.append(target_cell)
        
        else:
            if target_cell is not None and cells[target_cell] is not None and (cells[target_cell].occupied_by is None or cells[target_cell].occupied_by.islower()):
                valid_cells.append(target_cell)

    return valid_cells

def move_like_rook(starting_cell, fen, color):
    cells = moveLogic.initialize_board(fen)
    start_coords = get_coordinates_from_cell(starting_cell, fen)
    q = start_coords[0]
    r = start_coords[1]
    s = start_coords[2]

    valid_cells = []

    '''Upper Left'''
    upper_left_q = q - 1
    upper_left_s = s + 1

    moves = 1

    while upper_left_q >= -5 and upper_left_s <= 5:
        cell = get_cell_with_coordinates(q - moves, r, s + moves, fen)

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
        cell = get_cell_with_coordinates(q, r - moves, s + moves, fen)

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
        cell = get_cell_with_coordinates(q + moves, r - moves, s, fen)

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
        cell = get_cell_with_coordinates(q + moves, r, s - moves, fen)

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
        cell = get_cell_with_coordinates(q, r + moves, s - moves, fen)

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
        cell = get_cell_with_coordinates(q - moves, r + moves, s, fen)

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
    cells = moveLogic.initialize_board(fen)
    start_coords = get_coordinates_from_cell(starting_cell, fen)

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
        target_cell = get_cell_with_coordinates(start_coords[0] + new_coords[j][0], start_coords[1] + new_coords[j][1], start_coords[2] + new_coords[j][2], fen)
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
    Get coordinate for specific cell number
"""

def get_coordinates_from_cell(num, fen):
    cells = moveLogic.initialize_board(fen)

    return (cells[num].q, cells[num].r, cells[num].s) if cells[num] is not None else None

"""
    Testing that each cell is assigned the proper coordinates
"""
def get_cell_with_coordinates(q, r, s, fen):
    cells = moveLogic.initialize_board(fen)

    for cell in range(len(cells)):
        if cells[cell].q == q and cells[cell].r == r and cells[cell].s == s:
           return cells[cell].num
        
    return None

def get_two_cell_move_black_enpassant(prev_fen, current_fen):

    #Used for checking if one pawn moved two cells in the last move
    previous_cells = moveLogic.initialize_board(prev_fen)
    current_cells = moveLogic.initialize_board(current_fen)

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
    previous_cells = moveLogic.initialize_board(prev_fen)
    current_cells = moveLogic.initialize_board(current_fen)

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
    Determines if either king is in check in a given FEN

    returns 'white' if white king is in check, 'black' if black king is in check, and 'None' if there is no check present

"""
def is_check(fen, color):
    cells = moveLogic.initialize_board(fen)
    white_king = None
    black_king = None

    #Find the cells that each king occupies
    for cell in cells:
        if cells[cell].occupied_by == 'k':
            black_king = cell

        if cells[cell].occupied_by == 'K':
            white_king = cell

    #Get coordinates for the kings
    white_king_coords = get_coordinates_from_cell(white_king, fen)
    black_king_coords = get_coordinates_from_cell(black_king, fen)

    #Checking check with pawns
    upper_left = get_cell_with_coordinates(white_king_coords[0] - 1, white_king_coords[1], white_king_coords[2] + 1, fen)
    upper_right = get_cell_with_coordinates(white_king_coords[0] + 1, white_king_coords[1] - 1, white_king_coords[2], fen)
    lower_left = get_cell_with_coordinates(black_king_coords[0] - 1, black_king_coords[1] + 1, black_king_coords[2], fen)
    lower_right = get_cell_with_coordinates(black_king_coords[0] + 1, black_king_coords[1], black_king_coords[2] - 1, fen)

    #Check white king for black encounters
    if color == 'white':
        #Does the white king encounter a black bishop or a queen if trying to move like a bishop?
        if any((cells[cell].occupied_by == 'b' or cells[cell].occupied_by == 'q') for cell in move_like_bishop(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black rook or a queen if trying to move like a rook?
        if any((cells[cell].occupied_by == 'r' or cells[cell].occupied_by == 'q') for cell in move_like_rook(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black knight if trying to move like a knight?
        if any(cells[cell].occupied_by == 'n' for cell in move_like_knight(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encouter a black king when it tries to move like a king?
        if any(cells[cell].occupied_by == 'k' for cell in move_like_king(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black pawn when it tries to capture like a pawn would?
        if any(cells[cell].occupied_by == 'p' for cell in [upper_left, upper_right] if cell is not None):
            return 'white'
        


    #Check black king for white encounters
    if color == 'black':
        if any((cells[cell].occupied_by == 'B' or cells[cell].occupied_by == 'Q') for cell in move_like_bishop(black_king, fen, 'black')):
            return 'black'
        
        if any((cells[cell].occupied_by == 'R' or cells[cell].occupied_by == 'Q') for cell in move_like_rook(black_king, fen, 'black')):
            return 'black'
        
        if any(cells[cell].occupied_by == 'N' for cell in move_like_knight(black_king, fen, 'black')):
            return 'black'
        
        if any(cells[cell].occupied_by == 'K' for cell in move_like_king(black_king, fen, 'black')):
            return 'black'
        
        if any(cells[cell].occupied_by == 'P' for cell in [lower_left, lower_right] if cell is not None):
            return 'black'
    
    #If no piece encounters exist, there is no check
    return None

"""
    Simulate a move, see if a check exists

    Returns color of check, false is there is no check
"""
def simulate_move(fen, start_cell, target_cell):

    cells = moveLogic.initialize_board(fen)
    cells_copy = copy.deepcopy(cells)

    #If the target cell contains a king, there's no need to simulate the move.  Kings cannot be captured
    if cells_copy[target_cell].occupied_by == 'k':
        return 'black'
    if cells_copy[target_cell].occupied_by == 'K':
        return 'white'

    #What piece is being simulated?
    piece = cells_copy[start_cell].occupied_by

    #Remove the piece from its starting cell, put it on its target cell
    cells_copy[start_cell].occupied_by = None
    cells_copy[target_cell].occupied_by = piece

    #Get the FEN string for the simulated position
    new_fen = moveLogic.board_to_fen(cells_copy)

    #If we moved a black piece, see if we put ourselves in check
    if piece.islower():
        if is_check(new_fen, 'black') == 'black':
            return 'black'
    
    #Same for white piece
    else:
        if is_check(new_fen, 'white') == 'white':
            return 'white'

    #Otherwise, there's no check present
    return False

"""
    Find all legal moves for any piece type (all legal moves for both knights, both bishops, all pawns, etc)
"""
def find_all_legal(fen, prev_fen, piece):

    cells = moveLogic.initialize_board(fen)

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
                move for move in moves if not simulate_move(fen, cells[white_pawn_cells[i]].num, move) == 'white'
            ]

        return valid_moves

    if piece == 'p':
        valid_moves = []

        for i in range(len(black_pawn_cells)):

            moves = move_like_black_pawn(cells[black_pawn_cells[i]].num, fen, prev_fen)[0]

            valid_moves += [
                move for move in moves if not simulate_move(fen, cells[black_pawn_cells[i]].num, move) == 'black'
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
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'B' or piece == 'b':
        valid_moves = []
        cell_list = white_bishop_cells if piece == 'B' else black_bishop_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_bishop(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'R' or piece == 'r':
        valid_moves = []
        cell_list = white_rook_cells if piece == 'R' else black_rook_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_rook(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'Q' or piece == 'q':
        valid_moves = []
        cell_list = white_queen_cells if piece == 'Q' else black_queen_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_queen(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'K' or piece == 'k':
        valid_moves = []
        cell_list = white_king_cells if piece == 'K' else black_king_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_like_king(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves

"""
    Find all legal moves (considering check) for whatever piece is occupying a given cell
"""
def find_legal_from_cell(fen, prev_fen, cell):
    cells = moveLogic.initialize_board(fen)

    piece = cells[cell].occupied_by

    if piece == 'P' or piece == 'p':
        moves = move_like_white_pawn(cell, fen, prev_fen)[0] if piece.isupper() else move_like_black_pawn(cell, fen, prev_fen)[0]

        print('pawn', moves)

        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]
    
    elif piece == 'N' or piece == 'n':
        moves = move_like_knight(cell, fen, 'white' if piece.isupper() else 'black')

        print('knight', moves)

        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]
    
    elif piece == 'B' or piece == 'b':
        moves = move_like_bishop(cell, fen, 'white' if piece.isupper() else 'black')
        print('bishop', moves)
        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]
    
    elif piece == 'R' or piece == 'r':
        moves = move_like_rook(cell, fen, 'white' if piece.isupper() else 'black')
        print('rook', moves)
        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]
    
    elif piece == 'Q' or piece == 'q':
        moves = move_like_queen(cell, fen, 'white' if piece.isupper() else 'black')
        print('queen', moves)
        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]
    
    elif piece == 'K' or piece == 'k':
        moves = move_like_king(cell, fen, 'white' if piece.isupper() else 'black')
        print('king', moves)
        return [
            move for move in moves if not simulate_move(fen, cell, move) == ('white' if piece.isupper() else 'black')
        ]




if __name__ == '__main__':
    app.run(debug=True, port=8000)