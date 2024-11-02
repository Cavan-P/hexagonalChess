drawHexagon = (x, y, s, col, stroke) => {

    ctx.fillStyle = col

    ctx.beginPath()
    for (var i = 0; i < 6; i++) {
        const angle = 2 * Math.PI / 6 * i
        ctx.lineTo(x + s * Math.cos(angle), y + s * Math.sin(angle))
    }
    ctx.closePath()
    
    if(stroke) ctx.lineWidth = 5, ctx.stroke()

    
    ctx.fill()
}

getHexagonPoints = (x, y, s) => {
    let vertices = []

    for (var i = 0; i < 6; i++) {
        const angleRad = (60 * i) * Math.PI / 180
        const x_i = x + s * Math.cos(angleRad)
        const y_i = y + s * Math.sin(angleRad)

        vertices.push(Point(x_i, y_i))
    }

    return vertices
}