from flask import Flask, request, jsonify, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
import board_utils
import brain
import copy
import random
import utils
import move_logic


app = Flask(__name__, static_folder='../static')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

attack_map = [{} for _ in range(91)]
dependency_map = {}

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
        moves = move_logic.move_like_white_pawn(starting_cell, fen_string, prev_fen)
        valid_moves = moves[0]
        en_passant_target_cell = moves[1]
        en_passant_passed_pawn = moves[2]

    #Black pawn
    elif piece == 'p':
        moves = move_logic.move_like_black_pawn(starting_cell, fen_string, prev_fen)
        valid_moves = moves[0]
        en_passant_target_cell = moves[1]
        en_passant_passed_pawn = moves[2]

    elif piece == 'b' or piece == 'B':
        valid_moves = move_logic.move_like_bishop(starting_cell, fen_string, color)

    elif piece == 'n' or piece == 'N':
        valid_moves = move_logic.move_like_knight(starting_cell, fen_string, color)

    elif piece == 'r' or piece == 'R':
        valid_moves = move_logic.move_like_rook(starting_cell, fen_string, color)

    elif piece == 'k' or piece == 'K':
        valid_moves = move_logic.move_like_king(starting_cell, fen_string, color)

    elif piece == 'q' or piece == 'Q':
        valid_moves = move_logic.move_like_queen(starting_cell, fen_string, color)

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
    fen = data['fen']
    prev_fen = data['prevFen']
    cells = board_utils.initialize_board(fen)

    # Get all black pieces currently on the board
    living_black_pieces = {char for char in fen if char.islower()}

    # Loop until a piece with a legal move is found
    while living_black_pieces:
        # Select a random piece type from remaining pieces
        selected_piece = random.choice(list(living_black_pieces))

        # Find all cells containing this piece type
        selected_piece_cells = [cell for cell in cells if cells[cell].occupied_by == selected_piece]

        # Select a random cell holding the selected piece
        starting_cell = random.choice(selected_piece_cells) if len(selected_piece_cells) > 1 else selected_piece_cells[0]

        # Retrieve legal moves for the selected piece (may include en passant data for pawns)
        legal_data = find_legal_from_cell(fen, prev_fen, starting_cell)

        # If a pawn, extract en passant data
        if isinstance(legal_data, tuple):
            legal_moves, en_passant_target, en_passant_occupy, en_passant_flag = legal_data
        else:
            legal_moves, en_passant_target, en_passant_occupy, en_passant_flag = legal_data, None, None, False

        # If this piece has a legal move, randomly choose one
        if legal_moves:
            target_cell = random.choice(legal_moves)
            
            # Return response with en passant info if applicable
            return jsonify({
                'startingCell': starting_cell,
                'targetCell': target_cell,
                'enPassant': en_passant_flag,
                'enPassantPawnCell': en_passant_occupy,
                'enPassantTarget': en_passant_target
            })

        # No legal moves for this piece, so remove it from consideration
        print(f"No legal moves for {selected_piece}, reselecting...")
        living_black_pieces.remove(selected_piece)

    # If no legal moves are found for any piece, return message indicating likely stalemate or checkmate
    return jsonify({'message': 'No legal moves available - likely checkmate or stalemate'})

def initalize_attack_map():
    pass


"""
    Determines if either king is in check in a given FEN

    returns 'white' if white king is in check, 'black' if black king is in check, and 'None' if there is no check present

"""
def is_check(fen, color):
    cells = board_utils.initialize_board(fen)
    white_king = None
    black_king = None

    #Find the cells that each king occupies
    for cell in cells:
        if cells[cell].occupied_by == 'k':
            black_king = cell

        if cells[cell].occupied_by == 'K':
            white_king = cell

    #Get coordinates for the kings
    white_king_coords = utils.get_coordinates_from_cell(white_king, fen)
    black_king_coords = utils.get_coordinates_from_cell(black_king, fen)

    #Checking check with pawns
    upper_left = utils.get_cell_with_coordinates(white_king_coords[0] - 1, white_king_coords[1], white_king_coords[2] + 1, fen)
    upper_right = utils.get_cell_with_coordinates(white_king_coords[0] + 1, white_king_coords[1] - 1, white_king_coords[2], fen)
    lower_left = utils.get_cell_with_coordinates(black_king_coords[0] - 1, black_king_coords[1] + 1, black_king_coords[2], fen)
    lower_right = utils.get_cell_with_coordinates(black_king_coords[0] + 1, black_king_coords[1], black_king_coords[2] - 1, fen)

    #Check white king for black encounters
    if color == 'white':
        #Does the white king encounter a black bishop or a queen if trying to move like a bishop?
        if any((cells[cell].occupied_by == 'b' or cells[cell].occupied_by == 'q') for cell in move_logic.move_like_bishop(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black rook or a queen if trying to move like a rook?
        if any((cells[cell].occupied_by == 'r' or cells[cell].occupied_by == 'q') for cell in move_logic.move_like_rook(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black knight if trying to move like a knight?
        if any(cells[cell].occupied_by == 'n' for cell in move_logic.move_like_knight(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encouter a black king when it tries to move like a king?
        if any(cells[cell].occupied_by == 'k' for cell in move_logic.move_like_king(white_king, fen, 'white')):
            return 'white'
        
        #Does the white king encounter a black pawn when it tries to capture like a pawn would?
        if any(cells[cell].occupied_by == 'p' for cell in [upper_left, upper_right] if cell is not None):
            return 'white'
        


    #Check black king for white encounters
    if color == 'black':
        if any((cells[cell].occupied_by == 'B' or cells[cell].occupied_by == 'Q') for cell in move_logic.move_like_bishop(black_king, fen, 'black')):
            return 'black'
        
        if any((cells[cell].occupied_by == 'R' or cells[cell].occupied_by == 'Q') for cell in move_logic.move_like_rook(black_king, fen, 'black')):
            return 'black'
        
        if any(cells[cell].occupied_by == 'N' for cell in move_logic.move_like_knight(black_king, fen, 'black')):
            return 'black'
        
        if any(cells[cell].occupied_by == 'K' for cell in move_logic.move_like_king(black_king, fen, 'black')):
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

    cells = board_utils.initialize_board(fen)
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
    new_fen = board_utils.board_to_fen(cells_copy)

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
            moves = move_logic.move_like_white_pawn(cells[white_pawn_cells[i]].num, fen, prev_fen)[0]
            
            #Ensure that each move doesn't produce a check
            valid_moves += [
                move for move in moves if not simulate_move(fen, cells[white_pawn_cells[i]].num, move) == 'white'
            ]

        return valid_moves

    if piece == 'p':
        valid_moves = []

        for i in range(len(black_pawn_cells)):

            moves = move_logic.move_like_black_pawn(cells[black_pawn_cells[i]].num, fen, prev_fen)[0]

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

            moves = move_logic.move_like_knight(starting_cell, fen, 'white' if piece.isupper() else 'black')

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

            moves = move_logic.move_like_bishop(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'R' or piece == 'r':
        valid_moves = []
        cell_list = white_rook_cells if piece == 'R' else black_rook_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_logic.move_like_rook(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'Q' or piece == 'q':
        valid_moves = []
        cell_list = white_queen_cells if piece == 'Q' else black_queen_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_logic.move_like_queen(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves
    
    if piece == 'K' or piece == 'k':
        valid_moves = []
        cell_list = white_king_cells if piece == 'K' else black_king_cells

        for i in range(len(cell_list)):
            starting_cell = cells[cell_list[i]].num

            moves = move_logic.move_like_king(starting_cell, fen, 'white' if piece.isupper() else 'black')

            valid_moves += [
                move for move in moves if not simulate_move(fen, starting_cell, move) == ('white' if piece.isupper() else 'black')
            ]

        return valid_moves

"""
    Find all legal moves (considering check) for whatever piece is occupying a given cell
"""
def find_legal_from_cell(fen, prev_fen, cell):
    cells = board_utils.initialize_board(fen)
    piece = cells[cell].occupied_by
    is_white = piece.isupper()

    if piece == 'P' or piece == 'p':
        # Get moves and en passant target cell if applicable
        move_data = move_logic.move_like_white_pawn(cell, fen, prev_fen) if is_white else move_logic.move_like_black_pawn(cell, fen, prev_fen)
        moves, en_passant_target, en_passant_occupy = move_data[0], move_data[1] if len(move_data) > 1 else None, move_data[2] if len(move_data) > 1 else None
        en_passant_flag = en_passant_target is not None

        # Filter moves to avoid placing own king in check
        legal_moves = [
            move for move in moves if simulate_move(fen, cell, move) != ('white' if is_white else 'black')
        ]
        
        # Return legal moves with en passant data
        return legal_moves, en_passant_target, en_passant_occupy, en_passant_flag

    # Handle moves for non-pawn pieces
    elif piece == 'N' or piece == 'n':
        moves = move_logic.move_like_knight(cell, fen, 'white' if is_white else 'black')
    elif piece == 'B' or piece == 'b':
        moves = move_logic.move_like_bishop(cell, fen, 'white' if is_white else 'black')
    elif piece == 'R' or piece == 'r':
        moves = move_logic.move_like_rook(cell, fen, 'white' if is_white else 'black')
    elif piece == 'Q' or piece == 'q':
        moves = move_logic.move_like_queen(cell, fen, 'white' if is_white else 'black')
    elif piece == 'K' or piece == 'k':
        moves = move_logic.move_like_king(cell, fen, 'white' if is_white else 'black')
    else:
        return None  # In case of an unrecognized piece

    # Filter moves to avoid placing own king in check
    legal_moves = [
        move for move in moves if simulate_move(fen, cell, move) != ('white' if is_white else 'black')
    ]
    
    # Return only legal moves for non-pawn pieces
    return legal_moves

if __name__ == '__main__':
    app.run(debug=True, port=8000)