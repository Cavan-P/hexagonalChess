class Player {
    constructor(color){
        this.color = color
        this.selectedPiece = null

        this.closestMouseCell = null

        this.legalMoves = []
        this.enPassant = []
    }

    update(pieces, cells){
        if(this.getPieceAt(cells, pieces, mouseX, mouseY)){
            document.body.style.cursor = 'grab'
        }
        else{
            document.body.style.cursor = 'default'
        }
        if(pressed){
            currentFenString = boardToFen()
            //console.log("Pressing in player!")
            if(!this.selectedPiece){
                this.selectedPiece = this.getPieceAt(cells, pieces, mouseX, mouseY)

                if(this.selectedPiece){
                    currentFenString = boardToFen()
                    if(!previousFenString.length) previousFenString = boardToFen()

                    this.getLegalMoves()
                    this.selectedPiece.startDrag()
                    pieces.splice(pieces.indexOf(this.selectedPiece), 1); // Remove selected piece
                    pieces.push(this.selectedPiece); // Add it back at the end
                }
            }
            else if(this.selectedPiece.dragging){
                document.body.style.cursor = 'grabbing'
                this.selectedPiece.updateDrag(mouseX, mouseY)

                this.closestMouseCell = this.getClosestCellToMouse(cells)

                drawHexagon(this.closestMouseCell.x, this.closestMouseCell.y, cellSize, '#000000AA', false)
                
            }
        }
        else if(this.selectedPiece){
            let potentialTarget = this.getClosestCellToMouse(cells)

            if(this.legalMoves.includes(potentialTarget.num)){
                sendPiece = this.selectedPiece

                if(potentialTarget.num == this.enPassant[0]){
                    let deadPawn = pieces[pieces.findIndex(p => p.currentCell.num == this.enPassant[1])]

                    deadPawn.captured = true
                    capturedPieces.push(deadPawn.piece)
                }

                this.selectedPiece.stopDrag(cells)

                previousFenString = currentFenString
                currentFenString = boardToFen()

                //console.log("Previous upon drop: ", previousFenString)
                //console.log("Current upon drop: ", currentFenString)

                this.checkForCheck()

                turn++
            }
            else {
                this.selectedPiece.dragging = false
                this.selectedPiece.size = this.selectedPiece.landSize
                this.selectedPiece.x = this.selectedPiece.currentCell.x
                this.selectedPiece.y = this.selectedPiece.currentCell.y
            }

            this.selectedPiece = null

            document.body.style.cursor = 'default'
            cells.forEach(c => c.landable = false)
        }
    }

    getClosestCellToMouse(cells){
        let closestDist = 999999
        let closestCell
        for(let i = 0; i < cells.length; i++){
            let testDist = dist(cells[i].x, cells[i].y, mouseX, mouseY)
            if(testDist < closestDist){
                closestDist = testDist
                closestCell = cells[i]
            }
        }

        return closestCell
    }

    getPieceAt(cells, pieces, x, y){
        let closestCell = cells.findIndex(cell => pointInHexagon(Point(x, y), Point(cell.x, cell.y), cellSize))
        
        let piece = pieces.findIndex(p => p.currentCell == cells[closestCell])

        return pieces[piece]
    }

    getLegalMoves(){
        fetch('http://localhost:8000/find_legal_moves', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fen: currentFenString,
                prevFen: previousFenString,
                piece: this.selectedPiece.piece,
                startingCell: this.selectedPiece.currentCell.num
            })
        })
        .then(response => response.json())
        .then(validMoves => {

            this.legalMoves = validMoves.moves
            this.enPassant = validMoves.enpassant
            cells.forEach(c => validMoves.moves.includes(c.num) ? c.landable = true : c.landable = false)
        })
    }

    checkForCheck(){
        fetch('http://localhost:8000/drop_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fen: currentFenString,
                prevFen: previousFenString,
                piece: sendPiece.piece
            })
        })
        .then(response => response.json())
        .then(data => {

            checkFlag = data.check
            result = data.movesExist ? '' : data.check ? 'checkmate' : 'stalemate'

            sendPiece = null
        })
    }

}