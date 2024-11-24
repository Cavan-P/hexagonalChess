from Cell import Cell

coordinates = [
    [0, -5, 5],
    [-1, -4, 5],
    [1, -5, 4],
    [-2, -3, 5],
    [0, -4, 4],
    [2, -5, 3],
    [-3, -2, 5],
    [-1, -3, 4],
    [1, -4, 3],
    [3, -5, 2],
    [-4, -1, 5],
    [-2, -2, 4],
    [0, -3, 3],
    [2, -4, 2],
    [4, -5, 1],
    [-5, 0, 5],
    [-3, -1, 4],
    [-1, -2, 3],
    [1, -3, 2],
    [3, -4, 1],
    [5, -5, 0],
    [-4, 0, 4],
    [-2, -1, 3],
    [0, -2, 2],
    [2, -3, 1],
    [4, -4, 0],
    [-5, 1, 4],
    [-3, 0, 3],
    [-1, -1, 2],
    [1, -2, 1],
    [3, -3, 0],
    [5, -4, -1],
    [-4, 1, 3],
    [-2, 0, 2],
    [0, -1, 1],
    [2, -2, 0],
    [4, -3, -1],
    [-5, 2, 3],
    [-3, 1, 2],
    [-1, 0, 1],
    [1, -1, 0],
    [3, -2, -1],
    [5, -3, -2],
    [-4, 2, 2],
    [-2, 1, 1],
    [0, 0, 0],
    [2, -1, -1],
    [4, -2, -2],
    [-5, 3, 2],
    [-3, 2, 1],
    [-1, 1, 0],
    [1, 0, -1],
    [3, -1, -2],
    [5, -2, -3],
    [-4, 3, 1],
    [-2, 2, 0],
    [0, 1, -1],
    [2, 0, -2],
    [4, -1, -3],
    [-5, 4, 1],
    [-3, 3, 0],
    [-1, 2, -1],
    [1, 1, -2],
    [3, 0, -3],
    [5, -1, -4],
    [-4, 4, 0],
    [-2, 3, -1],
    [0, 2, -2],
    [2, 1, -3],
    [4, 0, -4],
    [-5, 5, 0],
    [-3, 4, -1],
    [-1, 3, -2],
    [1, 2, -3],
    [3, 1, -4],
    [5, 0, -5],
    [-4, 5, -1],
    [-2, 4, -2],
    [0, 3, -3],
    [2, 2, -4],
    [4, 1, -5],
    [-3, 5, -2],
    [-1, 4, -3],
    [1, 3, -4],
    [3, 2, -5],
    [-2, 5, -3],
    [0, 4, -4],
    [2, 3, -5],
    [-1, 5, -4],
    [1, 4, -5],
    [0, 5, -5]
]

def initialize_board(fen):
    cells = {}
    skips = 0
    index = 0
    since_skip = 0

    for cell_number, coord in enumerate(coordinates):
        cells[cell_number] = Cell(cell_number, coord[0], coord[1], coord[2])

    for char in fen:
        if not char.isalpha():
            skips += int(char)
            continue

        index += skips
        cells[index + since_skip].occupied_by = char

        skips = 0
        since_skip += 1

    return cells

def board_to_fen(cells):
    fen = ''
    skips = 0

    for cell in cells:
        if cells[cell].occupied_by is not None:
            # If there are skipped empty cells, add the count to FEN
            if skips:
                fen += str(skips)
                skips = 0
            # Add the piece occupying this cell to FEN
            fen += cells[cell].occupied_by
        else:
            skips += 1
            # Limit skip count to 9 in FEN
            if skips > 9:
                fen += '9'
                skips = 1
    
    # Add any remaining skips at the end of the loop
    if skips:
        fen += str(skips)

    return fen