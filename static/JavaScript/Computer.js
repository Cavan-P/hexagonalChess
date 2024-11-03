class Computer {
    constructor(color){
        this.color = color
    }

    async playTurn(currentFen, prevFen) {
        try {
            const { startingCell, targetCell } = await this.getMove(currentFen, prevFen)

            this.makeMove(startingCell, targetCell)
        } catch (error) {
            console.error("Error in computer's turn: ", error)
        }
    }

    async getMove(currentFen, prevFen){
        const move = await sendMoveRequest(currentFen, prevFen)

        return move
    }

    makeMove(startingCell, targetCell){
        console.log(startingCell, targetCell)
        const movedPiece = this.getPieceOnCell(startingCell)

        const landingCell = cells[targetCell]

        if(landingCell.occupied){
            this.getPieceOnCell(landingCell.num).captured = true
            capturedPieces.push(this.getPieceOnCell(landingCell.num).piece)
        }

        /*movedPiece.x += smooth(movedPiece.x, landingCell.x, 2)
        movedPiece.y += smooth(movedPiece.y, landingCell.y, 2)

        if(Math.abs(landingCell.x - movedPiece.x) < 0.5 && Math.abs(landingCell.y - movedPiece.y) < 0.5){
            movedPiece.x = landingCell.x
            movedPiece.y = landingCell.y
        }*/

        movedPiece.x = landingCell.x
        movedPiece.y = landingCell.y

        movedPiece.occupyingCell = landingCell

        movedPiece.assignCurrentCell(cells)

        previousFenString = currentFenString
        currentFenString = boardToFen()

        dropData.fen = currentFenString
        dropData.prevFen = previousFenString
        dropData.piece = movedPiece.piece

        movedPiece.checkDrop()

        turn ++
        sentComputerMove = false
    }

    getPieceOnCell(cell){
        return pieces[pieces.findIndex(piece => piece.occupyingCell.num == cell)]
    }
}