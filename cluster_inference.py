class ClusterInference:
    def __init__(self, game):
        self.game = game

    def find_clusters(self):

        clusters = []
        visited = set()

        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if (row, col) not in visited and not self.game.revealed[row][col]:
                    cluster = self._build_cluster(row, col, visited)
                    if cluster:
                        clusters.append(cluster)
        return clusters

    def _build_cluster(self, row, col, visited):

        cluster = []
        queue = [(row, col)]
        while queue:
            r, c = queue.pop(0)
            if (r, c) in visited or self.game.revealed[r][c]:
                continue
            visited.add((r, c))
            cluster.append((r, c))

            neighbours = self.get_neighbours(r, c)
            for n_r, n_c in neighbours:
                if not self.game.revealed[n_r][n_c] and (n_r, n_c) not in visited:
                    queue.append((n_r, n_c))
        return cluster

    def get_neighbours(self, row, col):

        neighbours = []
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (r == row and c == col) or not self.is_valid(r, c):
                    continue
                neighbours.append((r, c))
        return neighbours

    def is_valid(self, row, col):

        return 0 <= row < self.game.rows and 0 <= col < self.game.cols

    def analyze_clusters(self):

        clusters = self.find_clusters()
        for cluster in clusters:
            for cell in cluster:
                safe_moves, flag_moves = self._analyze_cell(cell)
                if safe_moves:
                    return ('reveal', safe_moves[0][0], safe_moves[0][1])
                if flag_moves:
                    return ('flag', flag_moves[0][0], flag_moves[0][1])
        return None

    def _analyze_cell(self, cell):

        row, col = cell
        neighbours = self.get_neighbours(row, col)

        mine_count = sum(1 for r, c in neighbours if self.game.board[r][c] == -1)
        flagged_count = sum(1 for r, c in neighbours if self.game.flags[r][c])

        safe_moves = []
        flag_moves = []

        if flagged_count == mine_count:
            safe_moves = [(r, c) for r, c in neighbours if not self.game.revealed[r][c] and not self.game.flags[r][c]]
        elif len(neighbours) - flagged_count == mine_count:
            flag_moves = [(r, c) for r, c in neighbours if not self.game.revealed[r][c] and not self.game.flags[r][c]]

        return safe_moves, flag_moves
