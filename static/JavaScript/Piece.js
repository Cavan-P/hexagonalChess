class Piece {
    constructor(piece, x, y){
        this.piece = piece

        this.x = x
        this.y = y

        this.dragSize = 70
        this.landSize = 60
        this.size = this.landSize

        this.captured = false

        this.currentCell = null //Cell it's over

        this.dragging = false
    }

    findClosestCell(cells){
        let closestDist = 999999
        let closestCell
        for(let i = 0; i < cells.length; i++){
            let testDist = dist(cells[i].x, cells[i].y, this.x, this.y)
            if(testDist < closestDist){
                closestDist = testDist
                closestCell = cells[i]
            }
        }

        return closestCell
    }

    assignCurrentCell(cells){
        let closestCell = this.findClosestCell(cells)
        this.currentCell = closestCell
    }

    startDrag(){
        this.dragging = true
    }

    updateDrag(mouseX, mouseY){
        if(this.dragging){
            this.size = this.dragSize
            this.x = mouseX
            this.y = mouseY
        }
    }

    stopDrag(cells){
        this.dragging = false
        this.size = this.landSize
        
        this.assignCurrentCell(cells)
        this.x = this.currentCell.x
        this.y = this.currentCell.y
    }

    display(showOccupiedPieceCell){
        if(!this.captured){
            let img = document.getElementById("pieces")

            switch(this.piece){
                case 'p':
                    //black pawn
                    ctx.drawImage(img, 1000, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'P':
                    //white pawn
                    ctx.drawImage(img, 1000, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'r':
                    //black rook
                    ctx.drawImage(img, 800, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'R':
                    //white rook
                    ctx.drawImage(img, 800, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'n':
                    //black knight
                    ctx.drawImage(img, 600, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'N':
                    //white knight
                    ctx.drawImage(img, 600, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'b':
                    //black bishop
                    ctx.drawImage(img, 400, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'B':
                    //white bishop
                    ctx.drawImage(img, 400, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'q':
                    //black queen
                    ctx.drawImage(img, 200, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'Q':
                    //white queen
                    ctx.drawImage(img, 200, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'k':
                    //black king
                    ctx.drawImage(img, 0, 200, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
                case 'K':
                    //white king
                    ctx.drawImage(img, 0, 0, 200, 200, this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
                break;
            }
        }

        if(showOccupiedPieceCell){
            ctx.fillStyle = '#A00'
            ctx.font = '15px sans-serif'
            ctx.fillText(this.currentCell.num, this.x - cellSize / 2, this.y - cellSize / 2.8)
        }
    }
}