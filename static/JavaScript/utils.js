
Point = (x, y) => {
    return {
        x: x,
        y: y
    }
}
pointInHexagon = (point, center, size) => {
    let sqrt3 = Math.sqrt(3)

    let dx = (point.x - center.x) / size
    let dy = (point.y - center.y) / size

    return dy > -sqrt3 / 2          &&
           dy < sqrt3 / 2           &&
           sqrt3 * dx + sqrt3 > dy  &&
           sqrt3 * dx - sqrt3 < dy  &&
           -sqrt3 * dx + sqrt3 > dy &&
           -sqrt3 * dx - sqrt3 < dy
}

dist = (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))
}

isLowercase = c => {
    return c == c.toLowerCase()
}
isUppercase = c => {
    return c == c.toUpperCase()
}

const pieceCoordinates = {
    'K': { x: 0, y: 0 },    // White King
    'Q': { x: 200, y: 0 },  // White Queen
    'R': { x: 800, y: 0 },  // White Rook
    'B': { x: 400, y: 0 },  // White Bishop
    'N': { x: 600, y: 0 },  // White Knight
    'P': { x: 1000, y: 0 }, // White Pawn
    'k': { x: 0, y: 200 },   // Black King
    'q': { x: 200, y: 200 }, // Black Queen
    'r': { x: 800, y: 200 }, // Black Rook
    'b': { x: 400, y: 200 }, // Black Bishop
    'n': { x: 600, y: 200 }, // Black Knight
    'p': { x: 1000, y: 200 } // Black Pawn
}

function sortCapturedPieces() {
    const whiteOrder = ['P', 'N', 'B', 'R', 'Q']; // Order for white pieces
    const blackOrder = ['p', 'n', 'b', 'r', 'q']; // Order for black pieces

    const whiteCaptured = capturedPieces.filter(piece => piece === piece.toUpperCase());
    const blackCaptured = capturedPieces.filter(piece => piece === piece.toLowerCase());

    // Sort function
    function sortByOrder(pieces, order) {
        return pieces.sort((a, b) => order.indexOf(a) - order.indexOf(b));
    }

    return {
        white: sortByOrder(whiteCaptured, whiteOrder),
        black: sortByOrder(blackCaptured, blackOrder)
    };
}

function displayCapturedPieces(ctx) {
    let img = document.getElementById("pieces")

    const pieceSize = 30
    const offsetYBlack = window.innerHeight - 10 - pieceSize
    const offsetYWhite = 10
    const offsetX = 10
    
    

    const sortedPieces = sortCapturedPieces()

    sortedPieces.white.forEach((piece, index) => {
        const coords = pieceCoordinates[piece];
        if (coords) {
            let divisor = piece == 'P' ? 1.7 : 1
            ctx.drawImage(
                img,
                coords.x, coords.y,
                200, 200,
                offsetX + index * pieceSize, offsetYWhite,
                pieceSize, pieceSize
            )
        }
    })

    sortedPieces.black.forEach((piece, index) => {
        const coords = pieceCoordinates[piece];
        if (coords) {
            let divisor = piece == 'p' ? 1.7 : 1
            ctx.drawImage(
                img,
                coords.x, coords.y,
                200, 200,
                offsetX + index * pieceSize, offsetYBlack,
                pieceSize, pieceSize
            );
        }
    })

    

    //console.log(capturedPieces)
}
