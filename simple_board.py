"""
simple_board.py

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, MAXSIZE

class SimpleGoBoard(object):

    def get_color(self, point):
        return self.board[point]

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        """
        board_copy = self.copy()
        # Try to play the move on a temporary copy of board
        # This prevents the board from being messed up by the move
        legal = board_copy.play_move(point, color)
        return legal

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)

    def reset(self, size):
        """
        Creates a start state, an empty board with the given size
        The board is stored as a one-dimensional array
        See GoBoardUtil.coord_to_point for explanations of the array encoding
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype = np.int32)
        self._initialize_empty_points(self.board) 
        self.winner = None

    def copy(self):
        b = SimpleGoBoard(self.size)
        b.winner = self.winner
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        return b

    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1
        
    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def is_eye(self, point, color):
        """
        Check if point is a simple eye for color
        """
        if not self._is_surrounded(point, color):
            return False
        # Eye-like shape. Check diagonals to detect false eye
        opp_color = GoBoardUtil.opponent(color)
        false_count = 0
        at_edge = 0
        for d in self._diag_neighbors(point):
            if self.board[d] == BORDER:
                at_edge = 1
            elif self.board[d] == opp_color:
                false_count += 1
        return false_count <= 1 - at_edge # 0 at edge, 1 in center
    
    def _is_surrounded(self, point, color):
        """
        check whether empty point is surrounded by stones of color.
        """
        for nb in self._neighbors(point):
            nb_color = self.board[nb]
            if nb_color != BORDER and nb_color != color:
                return False
        return True

    def _has_liberty(self, block):
        """
        Check if the given block has any liberty.
        block is a numpy boolean array
        """
        for stone in where1d(block):
            empty_nbs = self.neighbors_of_color(stone, EMPTY)
            if empty_nbs:
                return True
        return False

    def _block_of(self, stone):
        """
        Find the block of given stone
        Returns a board of boolean markers which are set for
        all the points in the block 
        """
        marker = np.full(self.maxpoint, False, dtype = bool)
        pointstack = [stone]
        color = self.get_color(stone)
        assert is_black_white(color)
        marker[stone] = True
        while pointstack:
            p = pointstack.pop()
            neighbors = self.neighbors_of_color(p, color)
            for nb in neighbors:
                if not marker[nb]:
                    marker[nb] = True
                    pointstack.append(nb)
        return marker

    def _detect_and_process_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        If yes, remove the stones.
        Returns True iff only a single tone was captured.
        This is used in play_move to check for possible ko
        """
        single_capture = None 
        opp_block = self._block_of(nb_point)
        if not self._has_liberty(opp_block):
            captures = list(where1d(opp_block))
            self.board[captures] = EMPTY
            if len(captures) == 1:
                single_capture = nb_point
        return single_capture

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            #self.ko_recapture = None
            self.current_player = GoBoardUtil.opponent(color)
            return True
        elif self.board[point] != EMPTY:
            return False
        #if point == self.ko_recapture:
            #return False
            
        # General case: deal with captures, suicide, and next ko point
        #oppColor = GoBoardUtil.opponent(color)
        #in_enemy_eye = self._is_surrounded(point, oppColor)
        self.board[point] = color
        #single_captures = []
        #neighbors = self._neighbors(point)
        #for nb in neighbors:
            #if self.board[nb] == oppColor:
                #single_capture = self._detect_and_process_capture(nb)
                #if single_capture != None:
                    #single_captures.append(single_capture)
        #block = self._block_of(point)
        #if not self._has_liberty(block): # undo suicide move
            #self.board[point] = EMPTY
            #return False
        #self.ko_recapture = None
        #if in_enemy_eye and len(single_captures) == 1:
            #self.ko_recapture = single_captures[0]
        
        #check vertical winner   
        count = -1
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location += 1
                else:
                    break
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location -= 1
                else:
                    break                
        if count >= 5:
            self.winner = color
            
        #check horizental winner
        count = -1
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location += (self.size+1)
                else:
                    break
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location -= (self.size+1)
                else:
                    break                
        if count >= 5:
            self.winner = color        
        #check diag from top left to down right
        count = -1
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location += (self.size+2)
                else:
                    break
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location -= (self.size+2)
                else:
                    break                
        if count >= 5:
            self.winner = color         
        
        #check diag from top right to down left
        count = -1
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location += self.size
                else:
                    break
        location = point
        for i in range(5):
            if location > 0 and location < len(self.board):
                if self.board[location] == color :
                    count += 1
                    location -= self.size
                else:
                    break                
        if count >= 5:
            self.winner = color            
        
        self.current_player = GoBoardUtil.opponent(color)
        return True

    def neighbors_of_color(self, point, color):
        """ List of neighbors of point of given color """
        nbc = []
        for nb in self._neighbors(point):
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc
        
    def _neighbors(self, point):
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point):
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1, 
                point - self.NS + 1, 
                point + self.NS - 1, 
                point + self.NS + 1]
