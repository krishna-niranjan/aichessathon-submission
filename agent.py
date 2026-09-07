import chess
import random
import time

# ============================================================
# CONSTANTS
# ============================================================

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Midgame PSTs
PAWN_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

KNIGHT_PST = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

BISHOP_PST = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

ROOK_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0]
]

QUEEN_PST = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

KING_PST = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

# Endgame PSTs
PAWN_PST_END = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [20, 30, 40, 40, 40, 40, 30, 20],
    [30, 40, 50, 50, 50, 50, 40, 30],
    [40, 50, 60, 60, 60, 60, 50, 40],
    [50, 60, 70, 70, 70, 70, 60, 50],
    [60, 70, 80, 80, 80, 80, 70, 60],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

KING_PST_END = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]
]

PST_MID = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
    chess.KING: KING_PST
}

PST_END = {
    chess.PAWN: PAWN_PST_END,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
    chess.KING: KING_PST_END
}

# ============================================================
# AGENT CLASS
# ============================================================

class Agent:
    def __init__(self):
        self.transposition_table = {}
        self.killer_moves = {}
        self.history_heuristic = {}
        self.time_left = 90

    # -----------------------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------------------

    def game_phase(self, board):
        """0.0 = opening/middlegame, 1.0 = endgame."""
        material = 0
        for piece_type in [chess.ROOK, chess.QUEEN, chess.KNIGHT, chess.BISHOP]:
            material += len(board.pieces(piece_type, chess.WHITE))
            material += len(board.pieces(piece_type, chess.BLACK))
        return min(1.0, material / 8.0)

    def pst_value(self, piece_type, square, color, phase):
        row = square // 8
        col = square % 8
        if color == chess.BLACK:
            row = 7 - row
        mid = PST_MID[piece_type][row][col]
        end = PST_END[piece_type][row][col]
        return int(mid * (1 - phase) + end * phase)

    def mobility(self, board, color):
        temp = board.copy()
        return len(list(temp.legal_moves)) // 2

    def evaluate(self, board):
        if board.is_checkmate():
            return -100000 if board.turn == chess.WHITE else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        phase = self.game_phase(board)
        score = 0

        for piece_type, value in PIECE_VALUES.items():
            for square in board.pieces(piece_type, chess.WHITE):
                score += value + self.pst_value(piece_type, square, chess.WHITE, phase)
            for square in board.pieces(piece_type, chess.BLACK):
                score -= value + self.pst_value(piece_type, square, chess.BLACK, phase)

        score += self.mobility(board, chess.WHITE) * 5
        score -= self.mobility(board, chess.BLACK) * 5

        if board.turn == chess.WHITE:
            score += 10
        else:
            score -= 10

                # Endgame king activity bonus
        if phase > 0.5:
            for color in [chess.WHITE, chess.BLACK]:
                king_square = board.king(color)
                if king_square:
                    center_dist = abs(chess.square_file(king_square) - 3.5) + abs(chess.square_rank(king_square) - 3.5)
                    bonus = (7 - center_dist) * 10 * phase
                    if color == chess.WHITE:
                        score += bonus
                    else:
                        score -= bonus
        return score

    # -----------------------------------------------------------------
    # MOVE ORDERING
    # -----------------------------------------------------------------

    def order_moves(self, board, moves):
        def move_score(move):
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score += 1000 + victim.piece_type - attacker.piece_type
                else:
                    score += 800
                if move.promotion:
                    score += 500
            if move in self.killer_moves:
                score += self.killer_moves[move]
            if move in self.history_heuristic:
                score += self.history_heuristic[move] // 10
            return score
        return sorted(moves, key=move_score, reverse=True)

    # -----------------------------------------------------------------
    # SEARCH
    # -----------------------------------------------------------------

    def search(self, board, depth, alpha, beta, maximizing, start_time, time_limit):
        if time.time() - start_time > time_limit*0.95:
            return self.evaluate(board), None

        if board.is_game_over():
            return self.evaluate(board), None

        if depth == 0:
            return self.quiescence(board, alpha, beta, maximizing, start_time, time_limit, 0), None

        key = board._transposition_key()
        if key in self.transposition_table:
            entry = self.transposition_table[key]
            if entry['depth'] >= depth:
                return entry['score'], entry.get('move', None)

        moves = self.order_moves(board, list(board.legal_moves))
        best_move = moves[0] if moves else None

        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                board.push(move)
                eval, _ = self.search(board, depth - 1, alpha, beta, False, start_time, time_limit)
                board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.killer_moves[move] = self.killer_moves.get(move, 0) + depth
                    break
            self.transposition_table[key] = {'depth': depth, 'score': max_eval, 'move': best_move}
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval, _ = self.search(board, depth - 1, alpha, beta, True, start_time, time_limit)
                board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    self.killer_moves[move] = self.killer_moves.get(move, 0) + depth
                    break
            self.transposition_table[key] = {'depth': depth, 'score': min_eval, 'move': best_move}
            return min_eval, best_move

    def quiescence(self, board, alpha, beta, maximizing, start_time, time_limit, depth=0):
    #Search only captures until position is quiet.
        # Time check
        if time.time() - start_time > time_limit:
            return self.evaluate(board)
        
        # Limit quiescence depth to avoid slowdowns
        if depth > 4:
            return self.evaluate(board)

        # Static evaluation
        stand_pat = self.evaluate(board)

        # Alpha-beta pruning
        if maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        tactical_moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or board.gives_check(move):
                tactical_moves.append(move)
        if not tactical_moves:
            return stand_pat
        tactical_moves = self.order_moves(board, tactical_moves)

        # Search captures
        if maximizing:
            max_eval = -float('inf')
            for move in tactical_moves:
                board.push(move)
                eval = self.quiescence(board, alpha, beta, False, start_time, time_limit, depth + 1)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in tactical_moves:
                board.push(move)
                eval = self.quiescence(board, alpha, beta, True, start_time, time_limit, depth + 1)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval    
    # -----------------------------------------------------------------
    # MOVE FUNCTION
    # -----------------------------------------------------------------

    def get_move(self, fen: str, time_left_ms: int) -> str:
        """Harness calls this."""
        board = chess.Board(fen)
        self.time_left = time_left_ms / 1000

        start_time = time.time()
        time_per_move = min(5.0, self.time_left / 20)

        best_move = None

        for depth in range(1, 10):
            _, move = self.search(
                board,
                depth,
                -float('inf'),
                float('inf'),
                board.turn == chess.WHITE,
                start_time,
                time_per_move
            )
            if move is not None:
                best_move = move
            if time.time() - start_time > time_per_move * 0.8:
                break

        if best_move is None:
            legal_moves = list(board.legal_moves)
            if legal_moves:
                best_move = random.choice(legal_moves)

        return best_move.uci() if best_move else None

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    agent = Agent()
    board = chess.Board()
    print(agent.get_move(board.fen(), 90000))

# Harness entry point
_agent = None

def get_move(fen: str, time_left_ms: int) -> str:
    global _agent
    if _agent is None:
        _agent = Agent()
    return _agent.get_move(fen, time_left_ms)