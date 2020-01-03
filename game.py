#!/usr/bin/env python3
########################################################################
# Filename    : game.py
# Description : jeux Othello
#               source: http://dhconnelly.com/paip-python/docs/paip/othello.html#board
#               modifié pour être compatible python3 et orienté objet
# modification: 2019/12/10
########################################################################

import time, random

class Game:
    """We represent the board as a 100-element list, which includes each square on the board as well as the outside edge.
    Each consecutive sublist of ten elements represents a single row, and each list element stores a piece.

    An initial board contains four pieces in the center:
    
    ? ? ? ? ? ? ? ? ? ?    00 01 02 03 04 05 06 07 08 09
    ? . . . . . . . . ?    10 11 ...                  19
    ? . . . . . . . . ?    20 21 ...
    ? . . . . . . . . ?    30 
    ? . . . o @ . . . ?    40
    ? . . . @ o . . . ?    50
    ? . . . . . . . . ?    60
    ? . . . . . . . . ?    70 
    ? . . . . . . . . ?    80 81 ...                  89
    ? ? ? ? ? ? ? ? ? ?    90 91 ...                  99
    """
    def __init__(self):
        self.EMPTY, self.BLACK, self.WHITE, self.OUTER = '.', '@', 'o', '?'
        self.PLAYERS = {self.BLACK: 'Black', self.WHITE: 'White'}
        self.PIECES = (self.EMPTY, self.BLACK, self.WHITE, self.OUTER)
        self.UP, self.DOWN, self.LEFT, self.RIGHT = -10, 10, -1, 1
        self.UP_RIGHT, self.DOWN_RIGHT, self.DOWN_LEFT, self.UP_LEFT = -9, 11, 9, -11
        self.DIRECTIONS = (self.UP, self.UP_RIGHT, self.RIGHT, self.DOWN_RIGHT, self.DOWN, self.DOWN_LEFT, self.LEFT, self.UP_LEFT)
        self.valid_squares = self.squares()     #list of valid squares
        self.SQUARE_WEIGHTS = [                 #relative worth of each square on the board 
            0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
            0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
            0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
            0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
            0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
            0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
            0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
            0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
            0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
            0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
        ]
        self.MAX_VALUE = sum(map(abs, self.SQUARE_WEIGHTS))
        self.MIN_VALUE = -self.MAX_VALUE
        self.EMPTY_THRESOLD = 18 #threshold defining evaluation strategy: above = weigted score, less = final
        

    #List all the valid squares on the board.
    def squares(self):
        return [i for i in range(11, 89) if 1 <= (i % 10) <= 8]
    
    #Create a new board with the initial black and white positions filled.
    def initial_board(self):
        board = [self.OUTER] * 100
        for i in self.squares():
            board[i] = self.EMPTY
            board[44], board[45] = self.WHITE, self.BLACK
            board[54], board[55] = self.BLACK, self.WHITE
        return board    

    #calculates empty pices left on the board
    def empty_pieces(self, board):
        return len([p for p in board if p==self.EMPTY])
        
    #print board
    def print_board(self, board):
        rep = ''
        rep += '  %s\n' % ' '.join(map(str, range(1, 9)))
        for row in range(1, 9):
            begin, end = 10*row + 1, 10*row + 9
            rep += '%d %s\n' % (row, ' '.join(board[begin:end]))
        rep+='%s %d \n' % ('pieces left:', self.empty_pieces(board))
        return rep

    #Is move a square on the board?
    def is_valid(self, move):
        return isinstance(move, int) and move in self.valid_squares

    #check a move, must be in a valid square, and legal
    def check(self, move, player, board):
        return self.is_valid(move) and self.is_legal(move, player, board)

    #Get player's opponent piece
    def opponent(self, player):
        return self.BLACK if player is self.WHITE else self.WHITE

    #Find a square that forms a bracket with square for player in the given direction. Returns None if no such square exists.
    def find_bracket(self, square, player, board, direction):
        bracket = square + direction
        if board[bracket] == player:
            return None
        opp = self.opponent(player)
        while board[bracket] == opp:
            bracket += direction
        return None if board[bracket] in (self.OUTER, self.EMPTY) else bracket

    #Is this a legal move for the player?
    def is_legal(self,move, player, board):
        hasbracket = lambda direction: self.find_bracket(move, player, board, direction)
        return board[move] == self.EMPTY and any(map(hasbracket, self.DIRECTIONS))

    #Update the board to reflect the move by the specified player.
    def make_move(self, move, player, board):
        board[move] = player
        for d in self.DIRECTIONS:
            self.make_flips(move, player, board, d)
        return board

    #Flip pieces in the given direction as a result of the move by player.
    def make_flips(self, move, player, board, direction):
        bracket = self.find_bracket(move, player, board, direction)
        if not bracket:
            return
        square = move + direction
        while square != bracket:
            board[square] = player
            square += direction

    #Get a list of all legal moves for player.
    def legal_moves(self, player, board):
        return [sq for sq in self.valid_squares if self.is_legal(sq, player, board)]

    #Can player make any moves?
    def any_legal_move(self, player, board):
        return any(self.is_legal(sq, player, board) for sq in self.valid_squares)

    #Play a game of Othello and return the final board and score
    #Each round consists of:
    # + Get a move from the current player.
    # + Apply it to the board.
    # + Switch players. If the game is over, get the final score.
    def play_console(self, black_strategy, white_strategy):
        print('Starting a new game')
        board = self.initial_board()
        player = self.BLACK
        strategy = lambda who: black_strategy if who == self.BLACK else white_strategy
        while player is not None:
            print(self.print_board(board))
            move = self.get_move(strategy(player), player, board)
            self.make_move(move, player, board)
            if strategy(player) != self.human:
                print(self.PLAYERS[player], "plays", move)
            player = self.next_player(board, player)
        return board, self.score(self.BLACK, board)

    #Which player should move next? Returns None if no legal moves exist.
    def next_player(self, board, prev_player):
        opp = self.opponent(prev_player)
        if self.any_legal_move(opp, board):
            return opp
        elif self.any_legal_move(prev_player, board):
            return prev_player
        return None

    #Call strategy(player, board) to get a move.
    def get_move(self, strategy, player, board):
        copy = list(board) # copy the board to prevent cheating
        move = strategy(player, copy)
        if not self.is_valid(move) or not self.is_legal(move, player, board):
            raise IllegalMoveError(player, move, copy)
        return move

    #Compute player's score (number of player's pieces minus opponent's).
    def score(self, player, board):
        mine, theirs = 0, 0
        opp = self.opponent(player)
        for sq in self.valid_squares:
            piece = board[sq]
            if piece == player: mine += 1
            elif piece == opp: theirs += 1
        return mine - theirs

    #------------------------------------------------------------------
    #STRATEGIES
    #------------------------------------------------------------------

    #human strategy
    #-----------------------------------------------------------------
    def human(self, player, board):
        print('Your move?')
        while True:
            move = input('> ')
            if move and self.check(int(move), player, board):
                return int(move)
            elif move:
                print('Illegal move--try again.')

    #A strategy that always chooses a random legal move
    #----------------------------------------------------------------
    def random_strategy(self, player, board):  
        return random.choice(self.legal_moves(player, board))
        

    #strategy based on maximazing scores
    #evaluate function is either "weighted_score" or "final_value", depends on how many empty left pieces
    #----------------------------------------------------------------------------------------------------
    def maximizer(self):
        def strategy(player, board):
            if self.empty_pieces(board) > self.EMPTY_THRESOLD:
                evaluate = self.weighted_score
            else:
                evaluate = self.final_value
            def score_move(move):
                return evaluate(player, self.make_move(move, player, list(board)))
            return max(self.legal_moves(player, board), key=score_move)
        return strategy

    #score based on square weigths
    def weighted_score(self, player, board):
        opp = self.opponent(player)
        total = 0
        for sq in self.valid_squares:
            if board[sq] == player:
                total += self.SQUARE_WEIGHTS[sq]
            elif board[sq] == opp:
                total -= self.SQUARE_WEIGHTS[sq]
        return total
    
    #score based on players score
    def final_value(self, player, board):
        diff = self.score(player, board)
        if diff < 0:
            return self.MIN_VALUE
        elif diff > 0:
            return self.MAX_VALUE
        return diff

    #min-max alpha-beta recursive research
    #----------------------------------------------------------------
    def alphabeta(self, player, board, alpha, beta, depth, evaluate):
        if depth == 0:
            return evaluate(player, board), None
        def value(board, alpha, beta):
            return -self.alphabeta(self.opponent(player), board, -beta, -alpha, depth-1, evaluate)[0]
        moves = self.legal_moves(player, board)
        if not moves:
            if not self.any_legal_move(self.opponent(player), board):
                return self.final_value(player, board), None
            return value(board, alpha, beta), None
    
        best_move = moves[0]
        for move in moves:
            if alpha >= beta:
                break
            val = value(self.make_move(move, player, list(board)), alpha, beta)
            if val > alpha:
                alpha = val
                best_move = move
        return alpha, best_move

    def alphabeta_searcher(self, depth):
        def strategy(player, board):
            if self.empty_pieces(board) > self.EMPTY_THRESOLD:
                evaluate = self.weighted_score
            else:
                evaluate = self.final_value
            return self.alphabeta(player, board, self.MIN_VALUE, self.MAX_VALUE, depth, evaluate)[1]
        return strategy

