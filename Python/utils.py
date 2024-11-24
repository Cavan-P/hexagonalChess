import board_utils
import move_logic
import copy

"""
    Get coordinate for specific cell number
"""

def get_coordinates_from_cell(num, fen):
    cells = board_utils.initialize_board(fen)

    return (cells[num].q, cells[num].r, cells[num].s) if cells[num] is not None else None

"""
    Testing that each cell is assigned the proper coordinates
"""
def get_cell_with_coordinates(q, r, s, fen):
    cells = board_utils.initialize_board(fen)

    for cell in range(len(cells)):
        if cells[cell].q == q and cells[cell].r == r and cells[cell].s == s:
           return cells[cell].num
        
    return None

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

def compare_fen(fen, prev_fen):
    old_board = board_utils.initialize_board(prev_fen)
    new_board = board_utils.initialize_board(fen)
    old_cell = None
    new_cell = None
    moved_piece = None

    for cell in old_board:
        prev_piece = old_board[cell].occupied_by
        curr_piece = new_board[cell].occupied_by

        if prev_piece is not None and curr_piece is None:
            old_cell = cell

        elif prev_piece is None and curr_piece is not None:
            new_cell = cell
            moved_piece = curr_piece

        elif prev_piece is not None and curr_piece is not None and prev_piece != curr_piece:
            new_cell = cell
            moved_piece = curr_piece

    return old_cell, new_cell, moved_piece

