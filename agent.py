import chess
import random
import time

# ============================================================
# CONSTANTS
# ============================================================

# Indexed by chess.piece_type (PAWN=1 .. KING=6). Index 0 unused.
PIECE_VALUES = (0, 100, 320, 330, 500, 900, 20000)

MATE_VALUE = 100000
MATE_THRESHOLD = MATE_VALUE - 1000

TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2
TT_MAX_ENTRIES = 400000

INF = 10 ** 9

# Move-ordering score tiers (must not overlap)
SCORE_TT         = 1 << 30
SCORE_CAPTURE    = 1 << 24
SCORE_PROMO      = 1 << 22
SCORE_KILLER1    = 1 << 20
SCORE_KILLER2    = 1 << 19
HISTORY_CAP      = 1 << 17
HISTORY_DECAY_AT = 1 << 20

# ---- Midgame PSTs (row 0 = rank 8) ----
PAWN_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
KNIGHT_PST = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]
BISHOP_PST = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]
ROOK_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0],
]
QUEEN_PST = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]
KING_PST = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

# ---- Endgame PSTs ----
PAWN_PST_END = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [20, 30, 40, 40, 40, 40, 30, 20],
    [30, 40, 50, 50, 50, 50, 40, 30],
    [40, 50, 60, 60, 60, 60, 50, 40],
    [50, 60, 70, 70, 70, 70, 60, 50],
    [60, 70, 80, 80, 80, 80, 70, 60],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
KING_PST_END = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]

def _flatten(pst):
    """PST given as 8x8 with row 0 = rank 8 -> flat 64 tuple indexed by square
    (sq 0 = a1, sq 63 = h8)."""
    flat = [0] * 64
    for sq in range(64):
        rank = sq >> 3          # 0 = rank 1
        file = sq & 7
        flat[sq] = pst[7 - rank][file]
    return tuple(flat)

_PST_ORDER = (PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST, QUEEN_PST, KING_PST)
_PST_ORDER_END = (PAWN_PST_END, KNIGHT_PST, BISHOP_PST, ROOK_PST, QUEEN_PST, KING_PST_END)

# Indexed by piece_type; index 0 is a placeholder.
PST_MID = (None,) + tuple(_flatten(p) for p in _PST_ORDER)
PST_END = (None,) + tuple(_flatten(p) for p in _PST_ORDER_END)


# ============================================================
# AGENT
# ============================================================

class Agent:
    MAX_PLY = 96

    def __init__(self):
        # TT: key -> (depth, score, flag, move)
        self.transposition_table = {}
        # killers[ply] = [move0, move1]
        self.killer_moves = [[None, None] for _ in range(self.MAX_PLY + 2)]
        # history[color][from*64+to]  (color: 1 = white, 0 = black)
        self.history_heuristic = [[0] * 4096, [0] * 4096]
        self.history_total = 0
        self.time_left = 90
        self.position_history = {}
        self.nodes_searched = 0
        self.stop = False
        self.deadline = 0.0

    # -----------------------------------------------------------------
    # POSITION HISTORY (threefold awareness across the real game)
    # -----------------------------------------------------------------

    def _repetition_key(self, board):
        return (board.board_fen() + " " + str(board.turn) + " "
                + str(board.castling_rights) + " " + str(board.ep_square))

    def record_position(self, board):
        k = self._repetition_key(board)
        self.position_history[k] = self.position_history.get(k, 0) + 1

    def repetition_count(self, board):
        return self.position_history.get(self._repetition_key(board), 0)

    # -----------------------------------------------------------------
    # ZOBRIST-LIKE KEY (all ints, C-level hash)
    # -----------------------------------------------------------------

    @staticmethod
    def _hash_key(board):
        # board.pawns/knights/etc. are combined across both colors, so
        # without occupied_co[WHITE] two positions differing only by
        # which color owns a type-matching square would collide.
        return hash((board.pawns, board.knights, board.bishops,
                     board.rooks, board.queens, board.kings,
                     board.occupied_co[chess.WHITE],
                     board.turn, board.castling_rights, board.ep_square))

    # -----------------------------------------------------------------
    # MATE SCORE NORMALIZATION FOR TT
    # -----------------------------------------------------------------

    def _tt_store_value(self, value, ply):
        if value > MATE_THRESHOLD:
            return value + ply
        if value < -MATE_THRESHOLD:
            return value - ply
        return value

    def _tt_retrieve_value(self, value, ply):
        if value > MATE_THRESHOLD:
            return value - ply
        if value < -MATE_THRESHOLD:
            return value + ply
        return value

    # -----------------------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------------------

    @staticmethod
    def _phase(board):
        """0 = full middlegame, 256 = deep endgame."""
        material = (board.rooks | board.queens
                    | board.knights | board.bishops).bit_count()
        phase = 256 - material * 32
        return 0 if phase < 0 else phase

    def evaluate(self, board):
        phase = self._phase(board)
        inv = 256 - phase
        values = PIECE_VALUES
        pst_mid = PST_MID
        pst_end = PST_END

        score = 0
        for sq, piece in board.piece_map().items():
            pt = piece.piece_type
            if piece.color:                 # White
                idx = sq
                mid = pst_mid[pt][idx]
                end = pst_end[pt][idx]
                score += values[pt] + ((mid * inv + end * phase) >> 8)
            else:                           # Black (mirror the square)
                idx = sq ^ 56
                mid = pst_mid[pt][idx]
                end = pst_end[pt][idx]
                score -= values[pt] + ((mid * inv + end * phase) >> 8)

        # Negamax convention: the leaf score must be from the perspective
        # of the side to move, not from White's. The loop above is
        # White-relative; flip it before returning.
        if not board.turn:
            score = -score
        # Tempo: the side to move always gets a small nudge.
        return score + 10

    # -----------------------------------------------------------------
    # MOVE ORDERING
    # -----------------------------------------------------------------

    def order_moves(self, board, moves, ply, tt_move=None):
        if ply < len(self.killer_moves):
            killers = self.killer_moves[ply]
        else:
            killers = (None, None)
        hist = self.history_heuristic[1 if board.turn else 0]
        values = PIECE_VALUES

        scores = {}
        for m in moves:
            if m == tt_move:
                s = SCORE_TT
            elif board.is_en_passant(m):
                s = SCORE_CAPTURE + values[chess.PAWN] * 16
            else:
                victim = board.piece_type_at(m.to_square)
                if victim is not None:
                    attacker = board.piece_type_at(m.from_square)
                    s = SCORE_CAPTURE + values[victim] * 16 - values[attacker]
                    if m.promotion:
                        s += values[m.promotion]
                elif m.promotion:
                    s = SCORE_PROMO + values[m.promotion]
                elif m == killers[0]:
                    s = SCORE_KILLER1
                elif m == killers[1]:
                    s = SCORE_KILLER2
                else:
                    s = hist[m.from_square * 64 + m.to_square]
            scores[m] = s

        return sorted(moves, key=scores.__getitem__, reverse=True)

    def _record_cutoff(self, move, is_capture, depth, ply, color):
        if is_capture:
            return
        if ply < len(self.killer_moves):
            k = self.killer_moves[ply]
            if k[0] != move:
                k[1] = k[0]
                k[0] = move
        h = self.history_heuristic[1 if color else 0]
        idx = move.from_square * 64 + move.to_square
        v = h[idx] + depth * depth
        h[idx] = v if v < HISTORY_CAP else HISTORY_CAP
        self.history_total += depth * depth
        if self.history_total > HISTORY_DECAY_AT:
            for row in self.history_heuristic:
                for i in range(4096):
                    row[i] >>= 1
            self.history_total >>= 1

    # -----------------------------------------------------------------
    # NULL-MOVE GUARD
    # -----------------------------------------------------------------

    @staticmethod
    def _has_non_pawn_material(board, color):
        occ = board.occupied_co[color]
        return bool((board.knights | board.bishops
                     | board.rooks | board.queens) & occ)

    # -----------------------------------------------------------------
    # MAIN SEARCH (negamax + PVS + null-move + LMR)
    # -----------------------------------------------------------------

    def search(self, board, depth, alpha, beta, ply, allow_null):
        if self.stop:
            return 0
        self.nodes_searched += 1
        if (self.nodes_searched & 31) == 0 and time.time() > self.deadline:
            self.stop = True
            return 0

        if board.is_checkmate():
            return -(MATE_VALUE - ply)
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        if depth <= 0:
            return self.quiescence(board, alpha, beta, ply, 0)

        key = self._hash_key(board)
        tt_move = None
        entry = self.transposition_table.get(key)
        if entry is not None:
            e_depth, e_score, e_flag, tt_move = entry
            if e_depth >= depth:
                s = self._tt_retrieve_value(e_score, ply)
                if e_flag == TT_EXACT:
                    return s
                if e_flag == TT_LOWERBOUND:
                    if s > alpha:
                        alpha = s
                elif s < beta:
                    beta = s
                if alpha >= beta:
                    return s

        alpha_orig = alpha
        beta_orig = beta
        in_check = board.is_check()

        # ---- Null-move pruning ----
        if (allow_null and depth >= 3 and not in_check
                and beta < MATE_THRESHOLD
                and self._has_non_pawn_material(board, board.turn)):
            R = 2 + depth // 6
            board.push(chess.Move.null())
            v = -self.search(board, depth - 1 - R, -beta, -beta + 1,
                             ply + 1, False)
            board.pop()
            if self.stop:
                return 0
            if v >= beta:
                return beta

        moves = self.order_moves(board, list(board.legal_moves), ply, tt_move)
        best_value = -INF
        best_move = moves[0]

        for i, move in enumerate(moves):
            is_capture = board.is_capture(move)
            board.push(move)

            if i == 0:
                value = -self.search(board, depth - 1, -beta, -alpha,
                                     ply + 1, True)
            else:
                reduction = 0
                if (depth >= 3 and i >= 4 and not is_capture
                        and move.promotion is None and not in_check):
                    r = 1 + (i >= 8) + (depth >= 6)
                    if board.is_check():
                        r = 0            # don't reduce checking moves
                    if r > depth - 2:
                        r = depth - 2
                    reduction = r

                value = -self.search(board, depth - 1 - reduction,
                                     -alpha - 1, -alpha, ply + 1, True)
                if reduction and value > alpha:
                    value = -self.search(board, depth - 1,
                                         -alpha - 1, -alpha, ply + 1, True)
                if alpha < value < beta:
                    value = -self.search(board, depth - 1,
                                         -beta, -alpha, ply + 1, True)

            board.pop()
            if self.stop:
                return 0

            if value > best_value:
                best_value = value
                best_move = move
            if value > alpha:
                alpha = value
            if alpha >= beta:
                self._record_cutoff(move, is_capture, depth, ply, board.turn)
                break

        # Bound flag
        if best_value <= alpha_orig:
            flag = TT_UPPERBOUND
        elif best_value >= beta_orig:
            flag = TT_LOWERBOUND
        else:
            flag = TT_EXACT

        if len(self.transposition_table) > TT_MAX_ENTRIES:
            self.transposition_table.clear()
        self.transposition_table[key] = (
            depth, self._tt_store_value(best_value, ply), flag, best_move)

        return best_value

    # -----------------------------------------------------------------
    # QUIESCENCE
    # -----------------------------------------------------------------

    def quiescence(self, board, alpha, beta, ply, qdepth):
        if self.stop:
            return 0
        self.nodes_searched += 1
        if (self.nodes_searched & 31) == 0 and time.time() > self.deadline:
            self.stop = True
            return 0

        if board.is_checkmate():
            return -(MATE_VALUE - ply)

        in_check = board.is_check()

        if in_check:
            stand = -INF
        else:
            stand = self.evaluate(board)
            if stand >= beta:
                return stand
            if stand > alpha:
                alpha = stand

        if qdepth >= 6:
            return stand if stand != -INF else self.evaluate(board)

        if in_check:
            moves = list(board.legal_moves)
        else:
            moves = [m for m in board.legal_moves
                     if board.is_capture(m) or m.promotion]

        if not moves:
            if in_check:
                return -(MATE_VALUE - ply)
            if board.is_stalemate():
                return 0
            return stand

        moves = self.order_moves(board, moves, min(ply, self.MAX_PLY), None)

        best = stand
        for move in moves:
            board.push(move)
            value = -self.quiescence(board, -beta, -alpha, ply + 1, qdepth + 1)
            board.pop()
            if self.stop:
                return 0
            if value > best:
                best = value
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break

        return best

    # -----------------------------------------------------------------
    # TIME MANAGEMENT (unchanged)
    # -----------------------------------------------------------------

    def compute_time_budget(self, time_left_ms, board):
        time_left = time_left_ms / 1000.0
        budget = min(3.5, time_left / 20)
        budget = min(budget, time_left - 0.5) if time_left > 0.5 else 0.05
        return max(budget, 0.05)

    # -----------------------------------------------------------------
    # ENTRY POINT
    # -----------------------------------------------------------------

    def get_move(self, fen: str, time_left_ms: int) -> str:
        board = chess.Board(fen)
        self.time_left = time_left_ms / 1000.0
        self.nodes_searched = 0
        self.stop = False
        self.record_position(board)

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Immediate mate
        for move in legal_moves:
            board.push(move)
            mated = board.is_checkmate()
            board.pop()
            if mated:
                return move.uci()

        time_budget = self.compute_time_budget(time_left_ms, board)
        start = time.time()
        self.deadline = start + time_budget

        root_key = self._hash_key(board)
        best_move = None
        prev_score = 0
        delta = 40

        for depth in range(1, 32):
            self.stop = False
            if depth >= 4:
                alpha = max(-INF, prev_score - delta)
                beta = min(INF, prev_score + delta)
            else:
                alpha, beta = -INF, INF

            while True:
                score = self.search(board, depth, alpha, beta, 0, True)
                if self.stop:
                    break
                if score <= alpha:
                    delta *= 2
                    alpha = max(-INF, prev_score - delta)
                    beta = min(INF, prev_score + delta)
                elif score >= beta:
                    delta *= 2
                    beta = min(INF, prev_score + delta)
                    alpha = max(-INF, prev_score - delta)
                else:
                    break
            if self.stop:
                break

            prev_score = score
            entry = self.transposition_table.get(root_key)
            if entry is not None and entry[3] is not None:
                best_move = entry[3]

            if abs(score) > MATE_THRESHOLD:
                break
            if time.time() - start > time_budget * 0.55:
                break

        if best_move is None:
            entry = self.transposition_table.get(root_key)
            if entry is not None and entry[3] is not None:
                best_move = entry[3]
        if best_move is None:
            best_move = random.choice(legal_moves)

        # Repetition avoidance when we're clearly ahead.
        # Negamax score is already from our perspective.
        """
        #Removed anti-repetiton logic, converts drawing situations into loseses when ahead, would rather take the draw.
        if prev_score > 50:
            board.push(best_move)
            would_repeat = self.repetition_count(board) >= 2
            board.pop()
            if would_repeat:
                alternatives = sorted(
                    (m for m in legal_moves if m != best_move),
                    key=lambda m: 0 if not board.is_capture(m) else 1,
                    reverse=True,
                )
                for alt in alternatives:
                    board.push(alt)
                    repeats = self.repetition_count(board) >= 2
                    board.pop()
                    if not repeats:
                        best_move = alt
                        break
        """

        # Record the position we're about to create (opponent to move), so
        # the next call's repetition check has this position's prior
        # occurrences to compare against. position_history covers every
        # position that has actually occurred in this game: our-turn
        # positions via the top-of-function record_position() call, and
        # opponent-turn positions via this one. Since turns strictly
        # alternate, every real position is one of these two categories.
        if best_move is not None:
            board.push(best_move)
            self.record_position(board)
            board.pop()

        return best_move.uci() if best_move else None


# ============================================================
# HARNESS ENTRY POINT
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