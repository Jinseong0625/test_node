# omok_game.py
class OmokGame:
    def __init__(self, board_size):
        self.board_size = board_size
        self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
        self.current_turn = 'X'  # 'X' 또는 'O'
        self.winner = None

    def print_board(self):
        for row in self.board:
            print('|'.join(row))
            print('-' * (self.board_size * 2 - 1))

    def make_move(self, row, col):
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_turn
            if self.check_winner(row, col):
                self.winner = self.current_turn
            else:
                self.switch_turn()
            return True
        return False

    def switch_turn(self):
        self.current_turn = 'O' if self.current_turn == 'X' else 'X'

    def check_winner(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1 + self.count_in_direction(row, col, dr, dc) + self.count_in_direction(row, col, -dr, -dc)
            if count >= 5:
                return True
        return False

    def count_in_direction(self, row, col, dr, dc):
        count = 0
        while 0 <= row + dr < self.board_size and 0 <= col + dc < self.board_size and \
                self.board[row + dr][col + dc] == self.current_turn:
            count += 1
            row += dr
            col += dc
        return count
