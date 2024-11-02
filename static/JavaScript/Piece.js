class Piece {
    constructor(piece, x, y){
        this.piece = piece

        this.x = x
        this.y = y

        this.captured = false

        this.occupyingCell = null //Cell it's over
        this.homeCell = null      //Cell it started on
        //this.prevHomeCell = null  //Backup home cell - `homeCell` updates immediately, `prevHomeCell` stores old home

        this.dragging = false
        this.over = false
        this.selected = false

        this.moveTime = 0
        this.timeSinceMove = 0
        this.justMoved = false

        this.validMoves = []
        this.enPassantCell = null
        this.passedPawnPassant = null

        this.landedLegalMove = false
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
        this.occupyingCell = this.findClosestCell(cells)
        cells[this.occupyingCell.num].occupied = true
        cells[this.occupyingCell.num].occupiedBy = this.piece
    }

    resetLandableCells(cells){
        cells.forEach(cell => cell.landable = false)
    }

    update(cells){

        this.over = false

        if(this.occupyingCell == null){
            this.assignCurrentCell(cells)
            this.homeCell = this.occupyingCell
            //this.prevHomeCell = this.homeCell
        }

        if(!this.captured){
            if(pointInHexagon(Point(mouseX, mouseY), Point(this.x, this.y), cellSize)){
                this.over = true
            }

            if(this.over && !this.dragging && !pressed){
                if(isUppercase(this.piece) && turn % 2 == 0){
                    drawHexagon(this.occupyingCell.x, this.occupyingCell.y, cellSize, '#000000AA', false)
                }
                if(isLowercase(this.piece) && turn % 2){
                    drawHexagon(this.occupyingCell.x, this.occupyingCell.y, cellSize, '#000000AA', false)
                }
                if(!turn) currentFenString = boardToFen()
            }

            if(this.over && this.dragging && !this.selected){
                this.selected = true
                
                this.sendData()
                //console.log("After sent data prev fen: ", previousFenString)
                //console.log("After sent data current fen: ", currentFenString)
            }

            if(this.over && this.dragging && this.selected){
                let targetCell = this.findClosestCell(cells)
                //Cell it came from
                drawHexagon(targetCell.x, targetCell.y, cellSize, 'rgba(0, 100, 0, 0.4)', false)
                //Cell it'll land on
                drawHexagon(this.occupyingCell.x, this.occupyingCell.y, cellSize, 'rgba(0, 200, 0, 0.4)', false)
                
                //previousFenString = currentFenString
                
                for(let cell of cells){
                    if(this.validMoves.includes(cell.num)){
                        cell.landable = true
                        //console.log(cell.num, cell.landable)
                    }
                }

                this.moveTime++
            }

            if(!this.dragging && !pressed){

                let targetCell = this.findClosestCell(cells)

                if(!this.validMoves.includes(targetCell.num)){
                    this.x = this.occupyingCell.x
                    this.y = this.occupyingCell.y

                    this.assignCurrentCell(cells)

                    this.landedLegalMove = false

                    //this.currentFenString = boardToFen()
                }
                else {
                    this.assignCurrentCell(cells)

                    this.x = this.occupyingCell.x
                    this.y = this.occupyingCell.y

                    this.landedLegalMove = true

                    if(this.enPassantCell && this.occupyingCell.num == this.enPassantCell){

                        cells[this.passedPawnPassant].occupied = false

                        //console.log(this.passedPawnPassant)
                        //let index = pieces.findIndex(piece => piece.occupyingCell.x == cells[this.passedPawnPassant].x && piece.occupyingCell.y == cells[this.passedPawnPassant].y)
                        //console.log("Index "+ index)

                        //pieces.splice(index, 1)
                        triggerPassant = true
                        deleteCell = this.passedPawnPassant
                        
                    }
                }

                this.resetLandableCells(cells)
                this.validMoves = []

                this.selected = false
                
                //Used for capture logic
                if(this.moveTime){
                    this.timeSinceMove++
                }
                if(this.timeSinceMove){
                    this.justMoved = true
                }
                if(this.timeSinceMove >= 3){
                    this.justMoved = false
                    this.moveTime = 0
                    this.timeSinceMove = 0
                    this.homeCell = this.occupyingCell

                    ////previousFenString = currentFenString
                    //currentFenString = boardToFen()
                }

                if(this.landedLegalMove){
                    previousFenString = currentFenString
                    currentFenString = boardToFen()

                    dropData.fen = currentFenString
                    dropData.piece = this.piece

                    this.checkDrop()

                    this.landedLegalMove = false

                    turn ++

                    //console.log("Prev: " + previousFenString)
                    //console.log("Curr: " + currentFenString)
                    //console.log(`${turn % 2 == 0 ? 'white\'s' : 'black\'s'} move`)
                }
            }
        }
    }

    sendData(){
        moveData.fen = currentFenString
        moveData.prevFen = previousFenString
        moveData.piece = this.piece
        moveData.startingCell = this.homeCell.num

        //console.log(moveData.fen, moveData.piece, moveData.startingCell)

        fetch('http://localhost:8000/find_legal_moves', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(moveData)
        })
        .then(response => response.json())
        .then(data => {
            if(data.moves.length > 0){
                //console.log("Piece can move to " + data.moves)
                
                //cells.forEach((cell, index) => cell.landable = data.moves.includes(index))
                this.validMoves = data.moves
                this.enPassantCell = data.enpassant[0]
                this.passedPawnPassant = data.enpassant[1]

                moveData = {}
            }
            else{
                console.log("Piece has no legal moves")
                moveData = {}
            }
        })
        .catch(error => {
            console.error(error)
        })
    }

    checkDrop(){
        fetch('http://localhost:8000/drop_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dropData)
        })
        .then(response => response.json())
        .then(data => {
            //console.log(data.check)
            if(data.check){
                checkedKing = data.check
            }
            else{
                checkedKing = null
            }

            whiteKingCell = cells.findIndex(cell => cell.occupiedBy == 'K')
            blackKingCell = cells.findIndex(cell => cell.occupiedBy == 'k')
        })
        .catch(error => {
            console.error(error)
        })
    }

    display(){
        if(!this.captured){
            let img = document.getElementById("pieces")

            switch(this.piece){
                case 'p':
                    //black pawn
                    ctx.drawImage(img, 1000, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'P':
                    //white pawn
                    ctx.drawImage(img, 1000, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'r':
                    //black rook
                    ctx.drawImage(img, 800, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'R':
                    //white rook
                    ctx.drawImage(img, 800, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'n':
                    //black knight
                    ctx.drawImage(img, 600, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'N':
                    //white knight
                    ctx.drawImage(img, 600, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'b':
                    //black bishop
                    ctx.drawImage(img, 400, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'B':
                    //white bishop
                    ctx.drawImage(img, 400, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'q':
                    //black queen
                    ctx.drawImage(img, 200, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'Q':
                    //white queen
                    ctx.drawImage(img, 200, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'k':
                    //black king
                    ctx.drawImage(img, 0, 200, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
                case 'K':
                    //white king
                    ctx.drawImage(img, 0, 0, 200, 200, this.x - sze / 2, this.y - sze / 2, sze, sze);
                break;
            }
        }

        if(showOccupiedPieceCell){
            ctx.fillStyle = '#A00'
            ctx.font = '15px sans-serif'
            ctx.fillText(this.occupyingCell.num, this.x - cellSize / 2, this.y - cellSize / 2.8)
        }
    }
}