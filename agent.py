import chess
import chess.polyglot
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

MATE_VALUE = 100000
TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2

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
        # killer_moves[ply] = [move1, move2]  (2-slot, keyed by ply from root)
        self.killer_moves = {}
        # history_heuristic[(from_square, to_square)] = score
        self.history_heuristic = {}
        self.time_left = 90
        # position_history[board_fen_no_clocks] = occurrence count, tracked
        # across real moves of THIS game (the process stays alive between
        # moves per the docs, so this persists correctly across get_move calls).
        self.position_history = {}
        self.nodes_searched = 0

    # -----------------------------------------------------------------
    # POSITION HISTORY (for repetition awareness across the real game)
    # -----------------------------------------------------------------

    def _repetition_key(self, board):
        # board_fen() excludes halfmove clock / fullmove number, which is
        # what threefold repetition compares on.
        return board.board_fen() + " " + str(board.turn) + " " + str(board.castling_rights) + " " + str(board.ep_square)

    def record_position(self, board):
        key = self._repetition_key(board)
        self.position_history[key] = self.position_history.get(key, 0) + 1

    def repetition_count(self, board):
        key = self._repetition_key(board)
        return self.position_history.get(key, 0)

    # -----------------------------------------------------------------
    # MATE SCORE / TT NORMALIZATION
    # -----------------------------------------------------------------

    MATE_THRESHOLD = MATE_VALUE - 1000

    def _tt_store_value(self, value, ply):
        """Convert a mate score from 'distance-from-root' (path-dependent)
        to 'distance-from-this-node' (path-independent) before caching it,
        so a later lookup of the same position via a different path length
        doesn't get a stale, wrong mate distance."""
        if value > self.MATE_THRESHOLD:
            return value + ply
        if value < -self.MATE_THRESHOLD:
            return value - ply
        return value

    def _tt_retrieve_value(self, value, ply):
        """Inverse of _tt_store_value: re-localize a cached mate score to
        the actual ply at which it's being used this time."""
        if value > self.MATE_THRESHOLD:
            return value - ply
        if value < -self.MATE_THRESHOLD:
            return value + ply
        return value

    # -----------------------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------------------

    def game_phase(self, board):
        """0.0 = opening/middlegame, 1.0 = endgame."""
        material = 0
        for piece_type in (chess.ROOK, chess.QUEEN, chess.KNIGHT, chess.BISHOP):
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

    def mobility_count(self, board, color):
        """
        Color-aware mobility. Temporarily flips whose turn it is to count
        that side's move count, then restores the real turn.
        Uses pseudo-legal moves (cheap) rather than fully-legal moves
        (expensive, requires check-legality filtering) as a fast
        approximation of mobility -- exact legality of every move isn't
        needed for a mobility heuristic.
        NOTE: this hack can be slightly inaccurate around en passant
        rights and check state immediately after flipping turn; it's a
        cheap approximation, not used for legality anywhere.
        """
        original_turn = board.turn
        try:
            board.turn = color
            count = sum(1 for _ in board.generate_pseudo_legal_moves())
        finally:
            board.turn = original_turn
        return count

    def evaluate(self, board):
        # Non-mate terminal conditions
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        phase = self.game_phase(board)
        score = 0

        # Single pass over the piece map: material + PST + attacked-piece
        # penalty combined, instead of three separate full-board scans.
        piece_map = board.piece_map()
        for square, piece in piece_map.items():
            value = PIECE_VALUES[piece.piece_type]
            pst = self.pst_value(piece.piece_type, square, piece.color, phase)
            contribution = value + pst

            if piece.piece_type != chess.KING and board.is_attacked_by(not piece.color, square):
                contribution -= 50

            if piece.color == chess.WHITE:
                score += contribution
            else:
                score -= contribution

        score += self.mobility_count(board, chess.WHITE) * 5
        score -= self.mobility_count(board, chess.BLACK) * 5

        score += 10 if board.turn == chess.WHITE else -10

        # Endgame king activity bonus
        if phase > 0.5:
            for color in (chess.WHITE, chess.BLACK):
                king_square = board.king(color)
                if king_square is not None:
                    center_dist = abs(chess.square_file(king_square) - 3.5) + abs(chess.square_rank(king_square) - 3.5)
                    bonus = (7 - center_dist) * 10 * phase
                    score += bonus if color == chess.WHITE else -bonus

        return score

    # -----------------------------------------------------------------
    # MOVE ORDERING
    # -----------------------------------------------------------------

    def order_moves(self, board, moves, ply):
        killers = self.killer_moves.get(ply, [])

        def move_score(move):
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score += 10000 + PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type] // 100
                else:
                    score += 8000  # en passant: no piece on to_square
                if move.promotion:
                    score += 5000
            else:
                if move in killers:
                    # killer slot 0 ranks above slot 1
                    score += 3000 if killers[0] == move else 2500
                key = (move.from_square, move.to_square)
                score += self.history_heuristic.get(key, 0)
            return score

        return sorted(moves, key=move_score, reverse=True)

    def _record_cutoff(self, board, move, depth, ply):
        """Update killer moves / history heuristic on a beta cutoff.
        Only for non-capture moves, per standard practice -- captures are
        already ranked highly by MVV-LVA and don't need this bookkeeping."""
        if board.is_capture(move):
            return
        slots = self.killer_moves.setdefault(ply, [None, None])
        if slots[0] != move:
            slots[1] = slots[0]
            slots[0] = move
        key = (move.from_square, move.to_square)
        self.history_heuristic[key] = self.history_heuristic.get(key, 0) + depth * depth

    # -----------------------------------------------------------------
    # SEARCH
    # -----------------------------------------------------------------

    def search(self, board, depth, alpha, beta, maximizing, start_time, time_limit, ply=0):
        self.nodes_searched += 1
        # Batched every 128 nodes: every-node checking (a prior version)
        # added real per-call overhead across the whole search; every-1024
        # (the original) allowed too much overshoot before a check fired.
        # 128 is a middle ground -- cheap, and bounds worst-case overshoot
        # to a small, safe slice of the budget.
        if self.nodes_searched % 128 == 0 and time.time() - start_time > time_limit * 0.9:
            return self.evaluate(board), None

        if board.is_checkmate():
            # Ply-adjusted mate score: a mate found closer to the root
            # scores higher in magnitude than one found further away, so
            # the search prefers the fastest mate / slowest loss.
            mate_score = MATE_VALUE - ply
            return (-mate_score if maximizing else mate_score), None

        if board.is_stalemate() or board.is_insufficient_material():
            return 0, None

        if depth == 0:
            return self.quiescence(board, alpha, beta, maximizing, start_time, time_limit, 0), None

        alpha_orig = alpha
        beta_orig = beta

        key = chess.polyglot.zobrist_hash(board)
        tt_entry = self.transposition_table.get(key)
        if tt_entry is not None and tt_entry['depth'] >= depth:
            stored_score = self._tt_retrieve_value(tt_entry['score'], ply)
            if tt_entry['flag'] == TT_EXACT:
                return stored_score, tt_entry.get('move')
            elif tt_entry['flag'] == TT_LOWERBOUND:
                alpha = max(alpha, stored_score)
            elif tt_entry['flag'] == TT_UPPERBOUND:
                beta = min(beta, stored_score)
            if alpha >= beta:
                return stored_score, tt_entry.get('move')

        moves = self.order_moves(board, list(board.legal_moves), ply)
        best_move = moves[0] if moves else None

        if maximizing:
            value = -float('inf')
            for move in moves:
                board.push(move)
                eval_score, _ = self.search(board, depth - 1, alpha, beta, False, start_time, time_limit, ply + 1)
                board.pop()
                if eval_score > value:
                    value = eval_score
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    self._record_cutoff(board, move, depth, ply)
                    break
        else:
            value = float('inf')
            for move in moves:
                board.push(move)
                eval_score, _ = self.search(board, depth - 1, alpha, beta, True, start_time, time_limit, ply + 1)
                board.pop()
                if eval_score < value:
                    value = eval_score
                    best_move = move
                beta = min(beta, value)
                if alpha >= beta:
                    self._record_cutoff(board, move, depth, ply)
                    break

        # Determine bound type for TT storage
        if value <= alpha_orig:
            flag = TT_UPPERBOUND
        elif value >= beta_orig:
            flag = TT_LOWERBOUND
        else:
            flag = TT_EXACT
        stored_value = self._tt_store_value(value, ply)
        self.transposition_table[key] = {'depth': depth, 'score': stored_value, 'move': best_move, 'flag': flag}

        return value, best_move

    def see_capture_is_good(self, board, move):
        """Very lightweight static-exchange filter: keep a capture unless
        the victim is worth clearly less than the attacker AND the
        destination square is defended by the opponent (i.e. we'd likely
        just be handing back more material than we win). This is a cheap
        approximation, not a full SEE implementation."""
        if not board.is_capture(move):
            return True
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if not victim or not attacker:
            return True  # en passant or other edge case, keep it simple
        if PIECE_VALUES[victim.piece_type] >= PIECE_VALUES[attacker.piece_type]:
            return True
        # Attacker is worth more than victim -- only keep if destination
        # square isn't defended by the opponent after the capture.
        board.push(move)
        defended = board.is_attacked_by(not attacker.color, move.to_square)
        board.pop()
        return not defended

    def quiescence(self, board, alpha, beta, maximizing, start_time, time_limit, depth=0):
        self.nodes_searched += 1
        if self.nodes_searched % 128 == 0 and time.time() - start_time > time_limit * 0.9:
            return self.evaluate(board)

        if board.is_checkmate():
            mate_score = MATE_VALUE - (100 - depth)  # deep in quiescence, treat as "far" mate
            return -mate_score if maximizing else mate_score

        if depth > 4:
            return self.evaluate(board)

        stand_pat = self.evaluate(board)

        if abs(stand_pat) > MATE_VALUE - 1000:
            return stand_pat

        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        tactical_moves = []
        for move in board.legal_moves:
            if board.is_capture(move):
                if self.see_capture_is_good(board, move):
                    tactical_moves.append(move)
            elif board.gives_check(move):
                tactical_moves.append(move)

        if not tactical_moves:
            return stand_pat

        tactical_moves = self.order_moves(board, tactical_moves, ply=1000 + depth)

        if maximizing:
            value = -float('inf')
            for move in tactical_moves:
                board.push(move)
                eval_score = self.quiescence(board, alpha, beta, False, start_time, time_limit, depth + 1)
                board.pop()
                value = max(value, eval_score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('inf')
            for move in tactical_moves:
                board.push(move)
                eval_score = self.quiescence(board, alpha, beta, True, start_time, time_limit, depth + 1)
                board.pop()
                value = min(value, eval_score)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    # -----------------------------------------------------------------
    # TIME MANAGEMENT
    # -----------------------------------------------------------------

    def compute_time_budget(self, time_left_ms, board):
        """Reverted to the original flat allocation after the adaptive
        version tested weaker in practice. Simple and predictable:
        flat 5s/move whenever there's 100s+ on the clock, tapering
        down as time_left shrinks."""
        time_left = time_left_ms / 1000.0
        budget = min(5.0, time_left / 20)
        budget = min(budget, time_left - 0.5) if time_left > 0.5 else 0.05
        budget = max(budget, 0.05)
        return budget

    # -----------------------------------------------------------------
    # MOVE FUNCTION
    # -----------------------------------------------------------------

    def get_move(self, fen: str, time_left_ms: int) -> str:
        """Harness calls this."""
        board = chess.Board(fen)
        self.time_left = time_left_ms / 1000
        self.nodes_searched = 0
        self.record_position(board)

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Fast path: take an immediate mate if one exists.
        for move in legal_moves:
            board.push(move)
            is_mate = board.is_checkmate()
            board.pop()
            if is_mate:
                return move.uci()

        time_budget = self.compute_time_budget(time_left_ms, board)
        start_time = time.time()

        best_move = None
        current_eval = 0

        for depth in range(1, 9):
            score, move = self.search(
                board,
                depth,
                -float('inf'),
                float('inf'),
                board.turn == chess.WHITE,
                start_time,
                time_budget,
                ply=0
            )
            elapsed = time.time() - start_time
            if move is not None and elapsed <= time_budget:
                best_move = move
                current_eval = score
            if elapsed > time_budget * 0.8:
                break

        if best_move is None:
            best_move = random.choice(legal_moves)
        else:
            # Repetition awareness: among moves the search considered
            # roughly equally good, avoid repeating a position for the
            # third time if we're ahead, since that would hand the
            # opponent an auto-drawn game we could otherwise be winning.
            # (Deliberately conservative: only overrides the search's
            # choice, never forces a search from scratch.)
            we_are_white = board.turn == chess.WHITE
            we_are_ahead = current_eval > 50 if we_are_white else current_eval < -50
            if we_are_ahead:
                board.push(best_move)
                would_repeat = self.repetition_count(board) >= 2
                board.pop()
                if would_repeat:
                    alternatives = [m for m in legal_moves if m != best_move]
                    for alt in sorted(alternatives, key=lambda m: 0 if not board.is_capture(m) else 1, reverse=True):
                        board.push(alt)
                        alt_repeats = self.repetition_count(board) >= 2
                        board.pop()
                        if not alt_repeats:
                            best_move = alt
                            break

        return best_move.uci() if best_move else None


# ============================================================
# MAIN / HARNESS ENTRY POINT
# ============================================================

if __name__ == "__main__":
    agent = Agent()
    board = chess.Board()
    print(agent.get_move(board.fen(), 90000))

_agent = None

def get_move(fen: str, time_left_ms: int) -> str:
    global _agent
    if _agent is None:
        _agent = Agent()
    return _agent.get_move(fen, time_left_ms)