class Player {
    constructor(color){
        this.color = color
        this.selectedPiece = null

        this.closestMouseCell = null
    }

    update(pieces, cells){
        if(pressed){
            //console.log("Pressing in player!")
            if(!this.selectedPiece){
                this.selectedPiece = this.getPieceAt(cells, pieces, mouseX, mouseY)
                //console.log("Selected piece ", this.selectedPiece.piece)
                if(this.selectedPiece){
                    this.selectedPiece.startDrag()
                }
            }
            else if(this.selectedPiece.dragging){
                this.selectedPiece.updateDrag(mouseX, mouseY)

                this.closestMouseCell = this.getClosestCellToMouse(cells)

                drawHexagon(this.closestMouseCell.x, this.closestMouseCell.y, cellSize, '#000000AA', false)
                
            }
        }
        else if(this.selectedPiece){
            this.selectedPiece.stopDrag(cells)
            this.selectedPiece = null
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
}