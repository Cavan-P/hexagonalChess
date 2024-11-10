class Computer {
    constructor(color){
        this.color = color

        this.selectedCell = null
        this.targetCell = null

        this.enPassantTarget = null
        this.enPassantCell = null
    }

    async sendMoveRequest(){
        const data = {
            fen: currentFenString,
            prevFen: previousFenString
        }

        const response = await fetch('http://localhost:8000/computer_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        
        const responseData = await response.json()
        return responseData
    }

    async makeMove(){
        //Give the turn back to White so I only make a move one time
        turn++

        const data = await this.sendMoveRequest()

        console.log(data)

        if(data.message){
            console.log(data.message)
        }
        else {
            this.selectedCell = data.startingCell
            this.targetCell = data.targetCell
            this.enPassantTarget = data.enPassantTarget
            this.enPassantCell = data.enPassantPawnCell

            this.updateBoard()
        }
    }

    updateBoard(){
        let movedPiece = this.getPieceOnCell(this.selectedCell)

        pieces.splice(pieces.indexOf(movedPiece), 1); // Remove selected piece
        pieces.push(movedPiece); // Add it back at the end

        movedPiece.currentCell.occupied = false
        movedPiece.currentCell.occupiedBy = ''

        movedPiece.currentCell = cells[this.targetCell]
        movedPiece.x = movedPiece.currentCell.x
        movedPiece.y = movedPiece.currentCell.y
        cells[this.targetCell].occupied = true
        cells[this.targetCell].occupiedBy = movedPiece.piece

        if(this.enPassantTarget == this.targetCell){

            let deadPawn = pieces[pieces.findIndex(p => p.currentCell.num == this.enPassantCell)]

            deadPawn.captured = true
            capturedPieces.push(deadPawn.piece)

            cells[this.enPassantCell].occupied = false
            cells[this.enPassantCell].occupiedBy = ''
        }

        previousFenString = currentFenString
        currentFenString = boardToFen()

        //console.log("Computer previous: ", previousFenString)
        //console.log("Computer current: ", currentFenString)

        this.checkForCheck(movedPiece.piece)
        
    }

    getPieceOnCell(cell){
        return pieces[pieces.findIndex(p => p.currentCell.num == cell)]
    }

    checkForCheck(movedPiece){
        fetch('http://localhost:8000/drop_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fen: currentFenString,
                prevFen: previousFenString,
                piece: movedPiece
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