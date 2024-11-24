const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth
canvas.height = window.innerHeight

ctx.textBaseline = "middle"
ctx.textAlign = "center"

/** Debug options */
//Cells
const showCoords = !true
const showCellNumbers = true
const showOccupiedBy = !true

//Pieces
const showOccupiedPieceCell = !true
const showOccupiedCell = !true

var turn = 0 //Even is white's move
const playerColor = 'white'
const computerColor = (playerColor == 'white') ? 'black' : 'white'

/** Cell radius (center to corner) */
const cellSize = 45

let cells = []
let pieces = []
let capturedPieces = []

var mouseX = 0
var mouseY = 0
var pressed = false

var populated = false
let FEN = 'bqknbnr2rp1b1p1p2p2p1p3pp4p993P4PP3P1P2P2P1P1B1PR2RNBNQKB'

//Force computer to en passant
//FEN = 'k93R5B1Q7NB94p91P5P9P89K'

//Queen doesn't have full range of motion - black king moved 8-7, queen now stops at 8
//FEN = '8k3N1p3Pp7ppp92Q3p1R3P4P4PN3P4PK1P1P1B1P3R5B'
//Another one - King moved 24-13, queen now stops at 24
//FEN = 'q3b1r5b1p4p1pp1k1R1rp2PP1P1n1PP4P9995B1P3RNB2KB'

var currentFenString = boardToFen()
var previousFenString = boardToFen()

var turn = 0

var checkFlag = false
var checkCell = null
var result = ''//'checkmate', 'stalemate', ''
var sendPiece = null
var landedLegal = false

const computer = new Computer(computerColor)
const player = new Player(playerColor)

document.onmousemove = event => {
    mouseX = event.clientX
    mouseY = event.clientY
}

document.onmousedown = event => {
    pressed = true
}

document.onmouseup = event => {
    pressed = false
}

init = _ => {
    
    ctx.fillStyle = '#FFF'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fill()

    ctx.strokeStyle = '#000'
    ctx.lineWidth = 7
    drawBoard(cellSize, 0, 1)
    drawBoard(cellSize, [
        '#D18B47FF',     /*  Dark cell    */
        '#E8AB6FFF',     /*  Middle cell  */
        '#FFCE9EFF'],    /*  Light cell   */
        false
    )

    if(!populated){
        populated = true
        populateBoard(FEN, cells)
        for(let piece of pieces) piece.assignCurrentCell(cells)
    }

    ctx.font = '20px sans-serif'
    ctx.fillStyle = '#000'
    ctx.fillText(`${turn % 2 ? 'Black' : 'White'}'s Move`, window.innerWidth - 100, 25)
    ctx.fillStyle = 'rgba(0, 0, 0, 0)'

    pieces = pieces.filter(p => !p.captured)

    //Display and update the cells
    for(let i = 0; i < cells.length; i++){
        cells[i].update(pieces)
        cells[i].display(showCellNumbers, showCoords, showOccupiedBy)
    }

    if(checkFlag){
        const checkCell = cells[cells.findIndex(c => c.occupiedBy == (checkFlag == 'white' ? 'K' : 'k'))]
        ctx.strokeStyle = 'rgba(200, 0, 0, 0.5)'
        ctx.lineWidth = 10
        drawHexagon(checkCell.x, checkCell.y, cellSize, '#00000000', true)

        if(result.length){
            console.log(result + "!")
        }
    }

    player.update(pieces, cells)

    if(computerColor == 'black' && turn % 2){
        computer.makeMove()
    }

    //Display pieces ON TOP OF all highlighting shennanigans
    for(let piece of pieces){
        piece.display(showOccupiedPieceCell)
    }

    for(let i = 0; i < pieces.length; i++){
        for(let j = i + 1; j < pieces.length; j++){
            if(pieces[i].currentCell == pieces[j].currentCell){
                const pieceToCapture = i < j ? pieces[i] : pieces[j]
                pieceToCapture.captured = true
                capturedPieces.push(pieceToCapture.piece)
                break
            }
        }
    }

    displayCapturedPieces(ctx)

    requestAnimationFrame(init)
}

requestAnimationFrame(init)