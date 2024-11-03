const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth
canvas.height = window.innerHeight

ctx.textBaseline = "middle"
ctx.textAlign = "center"

/** Debug options */
const showCoords = !true
const showCellNumbers = true
const showOccupiedBy = true

const showOccupiedPieceCell = true
const showOccupiedCell = true

var turn = 0 //Even is white's move
const computerColor = 'black'

/** Cell radius (center to corner) */
const cellSize = 45

let cells = []
let pieces = []
let capturedPieces = []

var mouseX = 0
var mouseY = 0
var pressed = false

var sze = 60
var populated = false
let FEN = 'bqknbnr2rp1b1p1p2p2p1p3pp4p993P4PP3P1P2P2P1P1B1PR2RNBNQKB'

//Force computer to en passant
//FEN = 'k93R5B1Q7NB94p91P5P9P89K'

//Queen doesn't have full range of motion - black king moved 8-7, queen now stops at 8
FEN = '8k3N1p3Pp7ppp92Q3p1R3P4P4PN3P4PK1P1P1B1P3R5B'
//Another one - King moved 24-13, queen now stops at 24
//FEN = 'q3b1r5b1p4p1pp1k1R1rp2PP1P1n1PP4P9995B1P3RNB2KB'

var moveData = {}
var dropData = {}
var currentFenString = boardToFen()
var previousFenString = boardToFen()
let isPieceSelected = false
var triggerPassant = false
var deleteCell = null

var triggerCheck = false
var checkedKing = null
var whiteKingCell = null
var blackKingCell = null

var noMovesFound = false

var turn = 0

var sentComputerMove = false
const computer = new Computer(computerColor)

document.onmousemove = event => {
    mouseX = event.clientX
    mouseY = event.clientY

    pieces.sort((a, b) => (a.dragging > b.dragging) ? 1 : -1)

    for(let piece of pieces){
        if(piece.dragging){
            piece.x = mouseX
            piece.y = mouseY
        }
    }
}

document.onmousedown = event => {
    pressed = true

    for(let piece of pieces){
        if(!(turn % 2)){
            if(piece.over && isUppercase(piece.piece)) piece.dragging = true, isPieceSelected = true
        }
        else {
            if(piece.over && isLowercase(piece.piece)) piece.dragging = true, isPieceSelected = true
        }
    }
}

document.onmouseup = event => {
    pressed = false

    for(let piece of pieces){
        if(piece.dragging){
            piece.dragging = false
            isPieceSelected = false
        }
    }
}

init = _ => {

    ctx.fillStyle = '#FFF'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fill()

    triggerCheck = false
    checkCell = null

    ctx.strokeStyle = '#000'
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
        
    }

    ctx.font = '20px sans-serif'
    ctx.fillStyle = '#000'
    ctx.fillText(`${turn % 2 ? 'Black' : 'White'}'s Move`, window.innerWidth - 100, 25)
    ctx.fillStyle = 'rgba(0, 0, 0, 0)'

    //If it's black's move
    if(((turn % 2 && computerColor == 'black') || (turn % 2 == 0 && computerColor == 'white')) && !sentComputerMove){
        sentComputerMove = true
        computer.playTurn(currentFenString, previousFenString)
    }

    if(checkedKing){
        checkCell = checkedKing == 'white' ? whiteKingCell : blackKingCell
        ctx.strokeStyle = 'rgba(200, 0, 0, 0.5)'
        drawHexagon(cells[checkCell].x, cells[checkCell].y, cellSize, 'rgba(0, 0, 0, 0)', true)
    }

    if(checkedKing && noMovesFound){
        console.log("Checkmate!")
    }
    if(!checkedKing && noMovesFound){
        console.log("Stalemate!")
    }

    pieces = pieces.filter(p => !p.captured)

    for(let i = 0; i < cells.length; i++){
        cells[i].update(pieces)
        cells[i].display(showCellNumbers, showCoords)
    }
    
    for(let i = 0; i < pieces.length; i++){
        pieces[i].update(cells)
        pieces[i].display()
    }

    for(let p1 of pieces){
        for(let p2 of pieces){
            if(p1 == p2 || p2.captured) continue

            if(p1.justMoved && p1.findClosestCell(cells) == p2.findClosestCell(cells)){
                p2.captured = true
                capturedPieces.push(p2.piece)
                
                
                break
            }
        }
    }

    if(triggerPassant){
        //console.log("Triggering passant")
        capturedPieces.push(cells[deleteCell].occupiedBy == 'p' ? 'p' : 'P')
        pieces = pieces.filter(piece => piece.occupyingCell.num != deleteCell)
        triggerPassant = false
        deleteCell = null
    }

    displayCapturedPieces(ctx)

    //console.log(capturedPieces)

    requestAnimationFrame(init)
}

requestAnimationFrame(init)