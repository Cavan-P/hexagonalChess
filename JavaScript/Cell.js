class Cell {
    constructor(x, y, num, q, r, s){
        this.x = x
        this.y = y
        
        this.num = num

        this.q = q
        this.r = r
        this.s = s

        this.occupied = false
        this.occupiedBy = ''

        this.landable = false
    }

    update(pieces){
        this.occupied = false
        this.occupiedBy = ''

        for(let piece of pieces){
            if(!piece.dragging && piece.x == this.x && piece.y == this.y){
                this.occupied = true
                this.occupiedBy = piece.piece
            }
        }
    }

    display(showCellNumbers, showCoords) {
        if(showCellNumbers){
            ctx.fillStyle = '#000'
            ctx.font = '20px sans-serif'
            ctx.fillText(this.num, this.x, this.y)
        }
        if(showCoords){
            ctx.font = '13px sans-serif'

            ctx.fillStyle = 'rgba(0, 100, 0, 1)'
            ctx.fillText(this.q, this.x, this.y - (cellSize / 1.4))

            ctx.fillStyle = 'rgba(0, 0, 200, 1)'
            ctx.fillText(this.r, this.x + (cellSize / 1.8), this.y + (cellSize / 2.8))

            ctx.fillStyle = 'rgba(255, 20, 147, 1)'
            ctx.fillText(this.s, this.x - (cellSize / 1.8), this.y + (cellSize / 2.8))
        }
        if(showOccupiedBy){
            ctx.fillStyle = '#000'
            ctx.font = '10px sans-serif'
            ctx.fillText(this.occupiedBy, this.x, this.y + cellSize / 1.6)
        }
        /*if(this.occupied){
            drawHexagon(this.x, this.y, cellSize, '#FF00005C', false)
        }*/
        if(this.landable){
            if(this.occupiedBy == 'k' || this.occupiedBy == 'K'){
                drawHexagon(this.x, this.y, cellSize, 'rgba(200, 0, 0, 0.4)', false)
            }
            else {
                drawHexagon(this.x, this.y, cellSize, 'rgba(0, 0, 0, 0)', true)
            }
        }
    }
}