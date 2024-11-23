# Gliński's Chess - Hexagonal chess variant

This is a project I've been wanting to get to work on for a while, 
and I've finally gotten around to sitting down and finishing it.

The visuals are all done with JavaScript, while I have a Python server
running the backend to process legal moves and the computer opponent.
When a piece is grabbed, information such as the FEN string (a custom
FEN-style syntax to compensate for the hexagonal grid) and selected piece
is sent to the backend, where legal moves are processed and then sent back
to the JavaScript side to be highlighted.

Check is actually functional, my methods of processing check are inefficient but enough for me to continue on with
the project, I'll come back to it and make this better later on.

Run the game with `python Python/server.py` from the main directory and visit http://localhost:8000 to play.

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
    - [ ] Offer in-game choice, currently is just queen

  - [X] Checkmate
  - [X] Stalemate
  - [X] Turn system
  - [X] Computer Opponent

- [ ] KNOWN BUGS
  - [X] Only legal move sends new FEN strings
  - [X] Computer playing en passant doesn't kill en passanted pawn
  - [X] Sometimes pieces don't have full range (Noticed queen, king, pawn)
  - [ ] Computer cannot play white
  - [X] prev FEN is not accurate - is the FEN string where previous piece was being dragged and therefore is not represented on the board
  - [ ] Capturing a pawn on one cell if it has a pawn right in front of it takes both

- [ ] Nice-to-have Visuals
  - [ ] En Passant cell highlights as if it's occupied
  - [ ] "Computer Thinking" text (or similar, moves evaluated, etc)
  - [ ] Highlight what piece the computer moved and where it came from


