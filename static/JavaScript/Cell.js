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
            if(piece.currentCell == this){
                this.occupied = true
                this.occupiedBy = piece.piece
            }
        }
    }

    display(showCellNumbers, showCoords, showOccupiedBy) {
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
        if(this.occupied && showOccupiedCell){
            drawHexagon(this.x, this.y, cellSize, '#FF00005C', false)
        }
        if(this.landable){
            ctx.lineWidth = 5
            if(this.occupied){
                drawHexagon(this.x, this.y, cellSize, 'rgba(200, 0, 0, 0.8)', false)
            }
            else{
                drawHexagon(this.x, this.y, cellSize / 1.3, 'rgba(0, 100, 0, 0.4)', false)
            }
        }
    }
}