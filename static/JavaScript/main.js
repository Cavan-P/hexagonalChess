const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth
canvas.height = window.innerHeight

ctx.textBaseline = "middle"
ctx.textAlign = "center"

/** Debug options */
const showCoords = true
const showCellNumbers = !true
const showOccupiedBy = !true

const showOccupiedPieceCell = !true

var turn = 0 //Even is white's move

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
const FEN = 'bqknbnr2rp1b1p1p2p2p1p3pp4p993P4PP3P1P2P2P1P1B1PR2RNBNQKB'

var moveData = {}
var currentFenString = boardToFen()
var previousFenString = boardToFen()
let isPieceSelected = false
var triggerPassant = false
var deleteCell = null

var triggerCheck = false
var checkCell = null

var turn = 0

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
        console.log("Triggering passant")
        pieces = pieces.filter(piece => piece.occupyingCell.num != deleteCell)
        triggerPassant = false
        deleteCell = null
    }

    if(triggerCheck){
        drawHexagon(cells[checkCell].x, cells[checkCell].y, cellSize, 'rgba(200, 0, 0, 0.4)', false)
    }

    //console.log(capturedPieces)

    requestAnimationFrame(init)
}

requestAnimationFrame(init)