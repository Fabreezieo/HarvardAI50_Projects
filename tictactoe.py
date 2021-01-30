"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

upDownDiagonal = [(0, 0), (1, 1), (2, 2)]
downUpDiagonal = [(2, 0), (1, 1), (0, 2)]


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    board = [x[y] for x in board for y in range(len(x))]
    if board.count(None) % 2 != 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                actions.append((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != None:
        raise NameError("Invalid Move")
    
    boardCopy = copy.deepcopy(board)

    boardCopy[action[0]][action[1]] = player(board)
    return boardCopy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if utility(board) == 1:
        return X
    elif utility(board) == -1:
        return O
    elif utility(board) == 0:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if [x[y] for x in board for y in range(len(x))].count(None) == 0:
        return True
    
    for row in board:
        if row == [X, X, X] or row == [O, O, O]:
            return True
    
    for row in [[row[x] for row in board] for x in range(3)]:
        if row == [X, X, X] or row == [O, O, O]:
            return True
    
    diagonal = []

    for (a, b) in upDownDiagonal:
        diagonal.append(board[a][b])
    if diagonal == [X, X, X] or diagonal == [O, O, O]:
        return True
    
    diagonal = []

    for (a, b) in downUpDiagonal:
        diagonal.append(board[a][b])
    if diagonal == [X, X, X] or diagonal == [O, O, O]:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    for row in board:
        if row == [X, X, X]:
            return 1
        elif row == [O, O, O]:
            return -1
    
    for row in [[row[x] for row in board] for x in range(3)]:
        if row == [X, X, X]:
            return 1
        elif row == [O, O, O]:
            return -1
    
    diagonal = []

    for (a, b) in upDownDiagonal:
        diagonal.append(board[a][b])
    if diagonal == [X, X, X]:
        return 1
    elif diagonal == [O, O, O]:
        return -1
    
    diagonal = []

    for (a, b) in downUpDiagonal:
        diagonal.append(board[a][b])
    if diagonal == [X, X, X]:
        return 1
    elif diagonal == [O, O, O]:
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """     
    if terminal(board):
        return None

    bestMove = ()

    if player(board) == X:
        if board == initial_state():
            return (0, 1)
        v = float('-inf')
        for action in actions(board):
            n = minValue(result(board, action), v)
            if n > v:
                v = n
                bestMove = action
        return bestMove
        
    elif player(board) == O:
        v = float('inf')
        for action in actions(board):
            m = maxValue(result(board, action), v)
            if m < v:
                v = m
                bestMove = action
        return bestMove
        

def maxValue(board, bestValue):
    if terminal(board):
        return utility(board)
    v = float('-inf')
    for action in actions(board):
        v = max(v, minValue(result(board, action), bestValue))
        if v > bestValue:
            return v
    return v


def minValue(board, bestValue):
    if terminal(board):
        return utility(board)
    v = float('inf')
    for action in actions(board):
        v = min(v, maxValue(result(board, action), bestValue))
        if v < bestValue:
            return v
    return v

        

