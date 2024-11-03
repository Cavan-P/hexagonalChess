# Gliński's Chess - Hexagonal chess variant

This is a project I've been wanting to get to work on for a while, 
and I've finally gotten around to sitting down and finishing it.

The visuals are all done with JavaScript, while I have a Python server
running the backend to process legal moves and the computer opponent, eventually.
When a piece is grabbed, information such as the current FEN string (custom FEN
style syntax for the hexagonal board), the piece that's being selected, and the
cell that said piece is currently on.  I can use this information to reconstruct
the grid on the Python side, determine the piece's legal moves, and send a list of
valid cells back to the JS side, which in turn highlights the appropriate cells.

Check is actually functional, but at the moment there is no checkmate or stalemate.
My methods of processing check are inefficient but enough for me to continue on with
the project, I'll come back to it and make this better later on.

### TODO
- [X] Visuals
  - [X] Persistent check highlight
  - [X] Display captured pieces
  - [X] "Opponent's move" text

- [ ] Mechanics
  - [X] Legal moves
    - [X] En Passant
    - [X] Check (Make this more efficient tho)

  - [ ] Promotion

  - [X] Checkmate
  - [X] Stalemate
  - [X] Turn system
  - [ ] Computer Opponent

- [ ] KNOWN BUGS
  - [X] Only legal move sends new FEN strings
  - [ ] Computer playing en passant doesn't kill en passanted pawn
  - [ ] Sometimes sliding pieces don't have full range?


