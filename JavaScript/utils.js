
Point = (x, y) => {
    return {
        x: x,
        y: y
    }
}
pointInHexagon = (point, center, size) => {
    let sqrt3 = Math.sqrt(3)

    let dx = (point.x - center.x) / size
    let dy = (point.y - center.y) / size

    return dy > -sqrt3 / 2          &&
           dy < sqrt3 / 2           &&
           sqrt3 * dx + sqrt3 > dy  &&
           sqrt3 * dx - sqrt3 < dy  &&
           -sqrt3 * dx + sqrt3 > dy &&
           -sqrt3 * dx - sqrt3 < dy
}

dist = (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))
}

isLowercase = c => {
    return c == c.toLowerCase()
}
isUppercase = c => {
    return c == c.toUpperCase()
}