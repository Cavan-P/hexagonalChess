import board_utils

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