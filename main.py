import pygame, sys



class Piece(object):
    def __init__(self, colour):
        """movementDirection is an int that shows y direction piece moves in
        colour is a string, must be either 'black' or 'white'"""
        if colour == "white":
            self._direction = 1
        else:
            self._direction = -1
        self._colour = colour
        self._kinged = False
        self._owner = None

    def getDirection(self):
        return self._direction

    def getColour(self):
        """returns colour which is a string"""
        return self._colour

    def getKinged(self):
        return self._kinged

    def setKinged(self):
        self._kinged = True

    def getOwner(self):
        return self._owner

    def setOwner(self, player):
        """player is a player object"""
        self._owner = player


class Player(object):
    def __init__(self, name):
        self._pieces = []
        self._name = name

    def addPiece(self, piece):
        """piece is a piece object"""
        piece.setOwner(self)
        self._pieces.append(piece)

    def removePiece(self, piece):
        """piece is a piece object"""
        self._pieces.remove(piece)

    def getPieces(self):
        return self._pieces.copy()

    def getName(self):
        return self._name

class Board(object):
    def __init__(self):
        self._board = [[None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None]]

    def getBoard(self):
        """returns copy of board, so can not be editted"""
        return self._board.copy()

    def removePiece(self, x, y):
        """x and y are ints representing coords"""
        self._board[y][x] = None

    def addPiece(self, x, y, piece):
        """x and y are ints, piece is a piece object"""
        self._board[y][x] = piece

    def getPiece(self, x, y):
        return self._board[y][x]

    def movePiece(self, oldx, oldy, newx, newy):
        """Moves a piece"""
        piece = self.getPiece(oldx,oldy)
        self.removePiece(oldx, oldy)
        self.addPiece(newx, newy, piece)

    def createKing(self, x, y):
        piece = self.getPiece(x, y)
        if piece != None:
            piece.setKinged()

    def resetBoard(self):
        self._board = [[None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None]]


class Game(object):
    """Game object must first be initialised, then game loop can be ran"""
    def __init__(self):
        pygame.init()
        self._board = Board()
        self.renderer = Renderer()
        self._player1 = Player("White")
        self._player2 = Player("Black")
        self._whosTurn = self._player1
        self._selected = (None, None)  #Will be this when nothing selected
        self._piecesWithMoves = []     #Will contain pieces the player can move on their turn
        self._selectedForced = False   #Used for combo taking
        self._winner = None
        self._endGame = False


    def _setUpPlayer1(self):
        for piece in self._player1.getPieces():
            self._player1.removePiece(piece)
        coords = ((0,0),(0,2),(0,4),(0,6),
                  (1,1),(1,3),(1,5),(1,7),
                  (2,0),(2,2),(2,4),(2,6))
        for coord in coords:
            piece = Piece("white")
            self._player1.addPiece(piece)
            self._board.addPiece(coord[1], coord[0], piece)
       

    def _setUpPlayer2(self):
        for piece in self._player2.getPieces():
            self._player2.removePiece(piece)
        coords = ((5,1),(5,3),(5,5),(5,7),
                  (6,0),(6,2),(6,4),(6,6),
                  (7,1),(7,3),(7,5),(7,7))
        for coord in coords:
            piece = Piece("black")
            self._player2.addPiece(piece)
            self._board.addPiece(coord[1], coord[0], piece)


    def _swapTurn(self):
        if self._whosTurn == self._player1:
            self._whosTurn = self._player2
        else:
            self._whosTurn = self._player1


    def _setSelected(self, xBoard, yBoard):
        """Sets selected tile, selected is a tuple"""      
        self._selected = (xBoard, yBoard)
        
            

    def _getSelected(self):
        return self._selected

    def _deselect(self):
        """Resets selection"""
        self._setSelected(None,None)
        self._selectedForced = False

    def _isSelected(self):
        """Checks if nothing is selected"""
        if self._getSelected() == (None, None):
            return False
        else:
            return True


    def _getHoveredSquare(self):
        """returns the coordinates of the square on screen the mouse is hovering over"""
        mousePos = pygame.mouse.get_pos()
        tilesize = self.renderer.getTilesize()
        return (mousePos[0]//tilesize, mousePos[1]//tilesize)


    def _checkOnBoard(self, xScreen, yScreen):
        """xScreen and yScreen are coords of on screen box
           returns True if this box is on the game board"""
        if yScreen < 3 or yScreen > 10 or xScreen > 7 or xScreen < 0:
            return False
        else:
            return True


    def _checkPossibleMovesWithDirection(self, xBoard, yBoard, yDirection):
        """The only purpose of this is to be used in the _checkPossibleMoves function
           so I dont have to type it twice for kinged pieces"""
        currentPiece = self._board.getPiece(xBoard, yBoard)
        if currentPiece == None:
            return None
        availableMoves = []
        yScreen = yBoard + 3
        xScreen = xBoard
        if self._checkOnBoard(xScreen - 1, yScreen + yDirection):              #Do checks for forward+left
            leftPiece = self._board.getPiece(xBoard - 1, yBoard + yDirection)
            if leftPiece == None:
                availableMoves.append((xBoard - 1, yBoard + yDirection, False))
            elif leftPiece.getOwner() != currentPiece.getOwner():           #Forward left is occupied by oppenent
                if self._checkOnBoard(xScreen - 2, yScreen + (yDirection*2)):
                    if self._board.getPiece(xBoard - 2, yBoard + (yDirection*2)) == None:
                        availableMoves.append((xBoard - 2, yBoard + (yDirection*2), True))
        
        if self._checkOnBoard(xScreen + 1, yScreen + yDirection):              #Do checks for forward+right
            rightPiece = self._board.getPiece(xBoard + 1, yBoard + yDirection)
            if rightPiece == None:
                availableMoves.append((xBoard + 1, yBoard + yDirection, False))
            elif rightPiece.getOwner() != currentPiece.getOwner():           #Forward right is occupied by opponent
                if self._checkOnBoard(xScreen + 2, yScreen + (yDirection*2)):
                    if self._board.getPiece(xBoard + 2, yBoard + (yDirection*2)) == None:
                        availableMoves.append((xBoard + 2, yBoard + (yDirection*2), True))

        return availableMoves


    def _checkPossibleMoves(self, xBoard, yBoard):
        """Returns a list of tuples which contain coords of possible moves of a
        piece positioned at input coords, tuple will also have 3rd bool value
        which says if piece was jumped over"""
        currentPiece = self._board.getPiece(xBoard, yBoard)
        if currentPiece == None:
            return []
        direction = currentPiece.getDirection()
        availableMoves = self._checkPossibleMovesWithDirection(xBoard, yBoard, direction)
        if currentPiece.getKinged():
            extraMoves = self._checkPossibleMovesWithDirection(xBoard, yBoard, -direction)
            for move in extraMoves:
                availableMoves.append(move)
        #Remove moves where piece not taken if possible to take one
        canTake = False
        for move in availableMoves:
            if move[2] == True:
                canTake = True
                break
        if canTake:
            availableMovesCopy = availableMoves.copy()
            for move in availableMovesCopy:
                if move[2] != True :
                    availableMoves.remove(move)
        return availableMoves


    def _checkActualMoves(self, xBoard, yBoard):
        """Used to see what moves a player can take with a piece"""
        currentPiece = self._board.getPiece(xBoard, yBoard)
        if currentPiece == None:
            return []
        if currentPiece not in self._piecesWithMoves:
            return []
        else:
            return self._checkPossibleMoves(xBoard, yBoard)
                  
        
    def _highlightPieceCheck(self, xScreen, yScreen):
        """
    returns coords of piece that needs to be highlighted
    returns None if no piece needs to be highlighted
    xScreen and yScreen are coords of on screen box not board coords,
    opposite for xBoard and yBoard"""
        if self._isSelected():
            return None
        if not self._checkOnBoard(xScreen, yScreen):
            return None
        yBoard = yScreen-3
        xBoard = xScreen
        occupied = self._board.getPiece(xBoard, yBoard)
        if occupied == None:
            return None
        elif occupied.getOwner() != self._whosTurn:
            return None
        else:
            return (xBoard, yBoard)


    def _movePiece(self, xBoardOrig, yBoardOrig, xBoardAfter, yBoardAfter, taking):
        """taking is a bool that says if a piece is being taken in this move"""
        if not taking:
            self._board.movePiece(xBoardOrig, yBoardOrig, xBoardAfter, yBoardAfter)
            self._createKings()
            self._startNewTurn()
        elif taking:
            if xBoardAfter < xBoardOrig:
                xSkew = -1
            else:
                xSkew = 1
            if yBoardAfter < yBoardOrig:
                ySkew = -1
            else:
                ySkew = 1
            toRemovePiece = self._board.getPiece(xBoardOrig+xSkew, yBoardOrig+ySkew)
            toRemovePiece.getOwner().removePiece(toRemovePiece)
            self._board.removePiece(xBoardOrig+xSkew,yBoardOrig+ySkew)
            self._board.movePiece(xBoardOrig, yBoardOrig, xBoardAfter, yBoardAfter)
            self._createKings()
            newAvailable = self._checkPossibleMoves(xBoardAfter, yBoardAfter)
            if newAvailable == [] or newAvailable[0][2] == False:
                self._startNewTurn()
            else:
                self._setSelected(xBoardAfter, yBoardAfter)
                self._selectedForced = True
        

    def _onLMB(self):
        """Triggered when LMB is clicked"""
        xScreen, yScreen = self._getHoveredSquare()
        if not self._checkOnBoard(xScreen, yScreen):       #Trigger if not on board         
            return None
        yBoard = yScreen - 3
        xBoard = xScreen
        if self._winner != None:    #Trigger if someone has won
            if xScreen in (2,3) and yScreen == 7:
                self._initialise()
            elif xScreen in (2,3) and yScreen == 8:
                self._closeGame()
        if self._isSelected():                             #Trigger if piece is selected
            selectedCoords = self._getSelected()
            possibleMoves = self._checkActualMoves(selectedCoords[0], selectedCoords[1])
            if (xBoard, yBoard, True) in possibleMoves:   #Trigger if coord available and taking
                self._movePiece(selectedCoords[0], selectedCoords[1], xBoard, yBoard, True)
                return None
            elif (xBoard, yBoard, False) in possibleMoves: #Trigger if available and not taking
                self._movePiece(selectedCoords[0], selectedCoords[1], xBoard, yBoard, False)
                return None
            else:         #Trigger if not in possible moves
                if not self._selectedForced:
                    self._setSelected(None,None)
                else:
                    return None
        occupied = self._board.getPiece(xBoard, yBoard)
        if occupied == None:                               #Trigger if square empty
            return None
        if occupied.getOwner() != self._whosTurn:          #Trigger if piece belongs to opposing player
            return None
        self._setSelected(xBoard, yBoard)

            
    def _createKings(self):
        """Scans top and bottom rows for opponent pieces and creates them"""
        for i in range(8):
            if self._board.getPiece(i,0) != None:
                if self._board.getPiece(i,0).getDirection() == -1:
                    self._board.createKing(i, 0)
            if self._board.getPiece(i,7) != None:
                if self._board.getPiece(i,7).getDirection() == 1:
                    self._board.createKing(i, 7)


    def _findMoveablePieces(self, player):
        """Player is player object, returns list of moveavble pieces"""
        canTake = False
        moveablePieces = []
        for y in range(8):
            for x in range(8):
                occupying = self._board.getPiece(x, y)
                if occupying != None:
                    if occupying.getOwner() == player:
                        availableMoves = self._checkPossibleMoves(x,y)
                        if not canTake:
                            if availableMoves != []:
                                if availableMoves[0][2] == False:
                                    moveablePieces.append(occupying)
                                elif availableMoves[0][2] == True:
                                    canTake = True
                                    moveablePieces = []
                                    moveablePieces.append(occupying)
                        elif canTake:
                            if  availableMoves != []:
                                if availableMoves[0][2] == True:
                                    moveablePieces.append(occupying)
        return moveablePieces


    def _closeGame(self):
        """Closes the game"""
        pygame.quit()
        sys.exit()


    def _setUpTurn(self):
        moveablePieces = self._findMoveablePieces(self._whosTurn)
        self._piecesWithMoves = moveablePieces
        if self._piecesWithMoves == []:
            if self._whosTurn == self._player1:
                self._winner = self._player2
            elif self._whosTurn == self._player2:
                self._winner = self._player1
             

    def _startNewTurn(self):
        """This swaps the players and sets up values for a new turn"""
        self._deselect()
        self._swapTurn()
        self._setUpTurn()


    def _initialise(self):
        self._board.resetBoard()
        self._whosTurn = self._player1
        self._selected = (None, None) 
        self._piecesWithMoves = []     
        self._selectedForced = False
        self._winner = None
        self._endGame = False
        self._setUpPlayer1()
        self._setUpPlayer2()
        self._setUpTurn()
                 

    def _gameloop(self):
        while not self._endGame:
            #Set up variables for renderer
            hoveredSquare = self._getHoveredSquare()
            highlightedPieceCoords = self._highlightPieceCheck(hoveredSquare[0],hoveredSquare[1])
            if self._isSelected():
                selectedCoords = self._getSelected()
                availableMovesForSelected = self._checkActualMoves(selectedCoords[0], selectedCoords[1])
            else:
                selectedCoords = None
                availableMovesForSelected = None     
            self.renderer.renderGame(self._board, self._player1, self._player2, highlightedPieceCoords, selectedCoords, availableMovesForSelected, self._winner)
            #Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._closeGame()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._onLMB()
            

    def main(self):
        self._initialise()
        self._gameloop()



class Renderer(object):
    def __init__(self):
        """Sets up some contants, some can be changed for configuration"""
        self._tilesize = 60  #Can be editted
        self._boardwidth = 8
        self._boardheight = 14
        self.highlightThickness = 10  #Can be editted
        self._surface = pygame.display.set_mode((self._boardwidth*self._tilesize,self._boardheight*self._tilesize))
        pygame.display.set_caption("Checkers")
        self.WHITE = (255,255,255)   
        self.BLACK = (0,0,0)   
        self.BEIGE = (245,245,220)  
        self.BROWN = (210,105,30)    
        self.GREEN = (0,255,0)     
        self.YELLOW = (255, 255, 0)
        self.CRIMSON = (220, 20, 60)
        self.BLUE = (0, 0, 255)


    def getTilesize(self):
        return self._tilesize

        
    def _renderBackground(self, backColour, tile1Colour, tile2Colour):
        """All parameters are tuples of 3 ints representing RGB values"""
        self._surface.fill(backColour)
        for row in range(3,11):
            for column in range(0,8):
                if row % 2 == 1:
                    if column % 2 == 0:
                        colour = tile2Colour
                    else:
                        colour = tile1Colour
                else:
                    if column % 2 == 0:
                        colour = tile1Colour
                    else:
                        colour = tile2Colour                 
                pygame.draw.rect(self._surface, colour, (column*self._tilesize, row*self._tilesize, self._tilesize, self._tilesize))


    def _renderPieces(self, board, whiteColour, blackColour, kingColour):
        """board is Board object whiteColour is colour of 'white' pieces, blackColour is colour of opposing
           kingColour is colour of king marker"""
        rowOffset = 3
        midpoint = self._tilesize // 2
        radius = self._tilesize // 2   
        for row in range(8):
            for column in range(8):
                piece = board.getPiece(column, row)
                if piece != None:
                    if piece.getColour() == "white":
                        colour = whiteColour
                    else:
                        colour = blackColour
                    yPosition = ((row + rowOffset) * self._tilesize) + midpoint
                    xPosition = (column * self._tilesize) + midpoint
                    pygame.draw.circle(self._surface, colour, (xPosition, yPosition), radius)
                    if piece.getKinged():
                        pygame.draw.circle(self._surface, kingColour, (xPosition, yPosition), radius//2)
                        


    def _renderHighlighted(self, highlightedPieceCoords, width, highlightColour):
        """coords are on board box coords, width is int representing thickness of highlight circle"""
        if highlightedPieceCoords == None:
            return None
        yScreen = highlightedPieceCoords[1] + 3
        xScreen = highlightedPieceCoords[0]
        midpoint = self._tilesize//2
        radius = self._tilesize//2
        yPosition = yScreen*self._tilesize + midpoint
        xPosition = xScreen*self._tilesize + midpoint
        pygame.draw.circle(self._surface, highlightColour, (xPosition, yPosition), radius, width)


    def _renderSelected(self, selectedPieceCoords, width, selectedColour):
        if selectedPieceCoords == None:
            return None
        yBoard = selectedPieceCoords[1]
        xBoard = selectedPieceCoords[0]
        yScreen = yBoard + 3
        xScreen = xBoard
        midpoint = self._tilesize // 2
        radius = self._tilesize // 2
        yPosition = yScreen*self._tilesize + midpoint
        xPosition = xScreen*self._tilesize + midpoint
        pygame.draw.circle(self._surface, selectedColour, (xPosition, yPosition), radius, width)


    def _renderAvailableSquares(self, availableSquareCoords, squareColour):
        """availableSquareCoords is a list of tuples of coordinates, squareColour
        is colour squares will be highlighted"""
        if availableSquareCoords == None:
            return None
        for coord in availableSquareCoords:
            xPosition = coord[0] * self._tilesize
            yPosition = (coord[1]+3) * self._tilesize 
            pygame.draw.rect(self._surface, squareColour, (xPosition, yPosition, self._tilesize, self._tilesize))


    def _renderDeadPieces(self, whitePlayer, blackPlayer, whiteColour, blackColour):
        deadWhitePieces = 12 - len(whitePlayer.getPieces())
        deadBlackPieces = 12 - len(blackPlayer.getPieces())
        midpoint = self._tilesize // 2
        radius = self._tilesize // 2
        deadBlackCoords = ((0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(0,1),(1,1),(2,1),(3,1))
        deadWhiteCoords = ((0,13),(1,13),(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(0,12),(1,12),(2,12),(3,12))
        for i in range(deadWhitePieces):
            coord = deadWhiteCoords[i]
            xPosition = (coord[0] * self._tilesize) + midpoint
            yPosition = (coord[1] * self._tilesize) + midpoint
            pygame.draw.circle(self._surface, whiteColour, (xPosition, yPosition), radius)
        for i in range(deadBlackPieces):
            coord = deadBlackCoords[i]
            xPosition = (coord[0] * self._tilesize) + midpoint
            yPosition = (coord[1] * self._tilesize) + midpoint
            pygame.draw.circle(self._surface, blackColour, (xPosition, yPosition), radius)


    def _renderWinningScreen(self, winner, textColour, buttonColour):
        if winner == None:
            return None
        winnerName = winner.getName()
        fontFile = pygame.font.get_default_font()
        fontObj = pygame.font.Font(fontFile, 40)
        textWinner = winnerName + " Wins!"
        textWinnerSurface = fontObj.render(textWinner, True, textColour)
        self._surface.blit(textWinnerSurface, (2 * self._tilesize, 3 * self._tilesize))
        textRestartSurface = fontObj.render("Restart?", True, textColour, buttonColour)
        self._surface.blit(textRestartSurface, (2 * self._tilesize, 7 * self._tilesize))
        textQuitSurface = fontObj.render("Quit!", True, textColour, buttonColour)
        self._surface.blit(textQuitSurface, (2 * self._tilesize, 8 * self._tilesize))
                
                                       
    def renderGame(self, board, whitePlayer, blackPlayer, highlightedPieceCoords, selectedPieceCoords, availableSquareCoords, winner):
        """Board is a board object"""
        self._renderBackground(self.GREEN, self.BEIGE, self.BROWN)
        self._renderPieces(board, self.WHITE, self.BLACK, self.YELLOW)
        self._renderHighlighted(highlightedPieceCoords, self.highlightThickness, self.YELLOW)
        self._renderSelected(selectedPieceCoords, 0, self.CRIMSON)
        self._renderAvailableSquares(availableSquareCoords, self.CRIMSON)
        self._renderDeadPieces(whitePlayer, blackPlayer, self.WHITE, self.BLACK)
        self._renderWinningScreen(winner, self.BLUE, self.YELLOW)
        pygame.display.update()


if __name__ == "__main__":      
    game = Game()
    game.main()
        
