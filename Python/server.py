from flask import Flask, request, jsonify, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
import board_utils
import brain
import random
import utils
import move_logic
from pprint import pprint


app = Flask(__name__, static_folder='../static')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

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
            if not ((piece.isupper() and utils.simulate_move(fen_string, starting_cell, move) == 'white') or
            (piece.islower() and utils.simulate_move(fen_string, starting_cell, move) == 'black'))
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
    check = utils.is_check(fen, color)
    moves_exist = False

    pieces = ('p n b r q k' if color == 'black' else 'P N B R Q K').split()

    #Find all legal moves for each piece type
    #If there are no moves, it's either checkmate or stalemate
    for i in pieces:
        if move_logic.find_all_legal(fen, prev_fen, i):
            moves_exist = True
            break

    #Send back the color that is in check, and whether or not this color has any legal moves on the board
    return jsonify({'check': check, 'movesExist': moves_exist})

values = {
    'p': 1,
    'b': 3,
    'n': 3,
    'r': 5,
    'q': 9,
    'k': 9999
}

#List of every cell, holds what cell it can be reached by and what piece is occupying that cell
attack_map = [[] for _ in range(91)]

#List of every OCCUPIED cell, holds ALL cells it could theoretically reach if board is empty
dependency_map = {}


@app.route('/computer_move', methods=['POST'])
def computer_move():
    data = request.get_json()
    fen = data['fen']
    prev_fen = data['prevFen']
    cells = board_utils.initialize_board(fen)

    for cell in cells:
        #`cell` is only cell number
        moves_from_cell = move_logic.find_legal_from_cell(fen, prev_fen, cell)
        piece_on_cell = cells[cell].occupied_by
        #print(piece_on_cell)
        if isinstance(moves_from_cell, tuple):
            moves_from_cell = moves_from_cell[0]

        for move in moves_from_cell:
            attack_map[move].append({'piece': piece_on_cell, 'attacking_cell': cell})

    #pprint(attack_map)

    for c in cells:
        cell = cells[c]

        if not cell.occupied_by:
            continue

        encountered_piece = cell.occupied_by

        if encountered_piece == 'p':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_black_pawn(c, fen, prev_fen)[0]} #Pawn ones still return a tuple

        elif encountered_piece == 'P':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_white_pawn(c, fen, prev_fen)[0]}

        elif encountered_piece == 'N' or encountered_piece == 'n':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_knight(c, fen)}
        
        elif encountered_piece == 'B' or encountered_piece == 'b':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_bishop(c, fen)}

        elif encountered_piece == 'R' or encountered_piece == 'r':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_rook(c, fen)}

        elif encountered_piece == 'Q' or encountered_piece == 'q':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_queen(c, fen)}

        elif encountered_piece == 'K' or encountered_piece == 'k':
            dependency_map[c] = {'piece': encountered_piece, 'dependencies': move_logic.dependency_map_king(c, fen)}

    pprint(dependency_map)






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
        legal_data = move_logic.find_legal_from_cell(fen, prev_fen, starting_cell)

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


if __name__ == '__main__':
    app.run(debug=True, port=8000)