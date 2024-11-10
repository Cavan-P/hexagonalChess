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

        turn ++
        sentComputerMove = false
    }

    getPieceOnCell(cell){
        return pieces[pieces.findIndex(piece => piece.occupyingCell.num == cell)]
    }
}