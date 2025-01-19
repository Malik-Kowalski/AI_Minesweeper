import pandas as pd
import os


class GameLogger:
    def __init__(self, filename="game_log.csv"):
        self.filename = filename
        self.game_id = self.get_last_game_id()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.isfile(self.filename):
            columns = ['GameID', 'Action', 'Row', 'Col', 'Result', 'Adjacent3x3']
            pd.DataFrame(columns=columns).to_csv(self.filename, index=False)

    def get_last_game_id(self):
        if os.path.isfile(self.filename):
            df = pd.read_csv(self.filename)
            if not df.empty:
                return df['GameID'].max()
        return 0

    def start_new_game(self):
        self.game_id += 1

    def _get_adjacent_3x3(self, game, row, col):
        adjacent_3x3 = []
        for r in range(row - 1, row + 2):
            row_data = []
            for c in range(col - 1, col + 2):
                if 0 <= r < game.rows and 0 <= c < game.cols:
                    if game.revealed[r][c]:
                        row_data.append(game.board[r][c])
                    elif game.flags[r][c]:
                        row_data.append('F')
                    else:
                        row_data.append(None)
                else:
                    row_data.append(-4)
            adjacent_3x3.append(row_data)
        return adjacent_3x3

    def log_move(self, action, row, col, result, game):
        adjacent_3x3 = self._get_adjacent_3x3(game, row, col)

        move_data = pd.DataFrame({
            'GameID': [self.game_id],
            'Action': [action],
            'Row': [row],
            'Col': [col],
            'Result': [result],
            'Adjacent3x3': [adjacent_3x3]
        })

        move_data.to_csv(self.filename, mode='a', header=False, index=False)
