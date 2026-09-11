### My AIChessathon submission

A complete chess engine written in Python for the AI chessathon.

## Overview
The agent is a single file (agent.py) that exposes one function:

```python
def get_move(fen: str, time_left_ms: int) -> str:
    return "e2e4"  # UCI move string
```
It receives the current position as a FEN string and the remaining clock time in milliseconds, and returns a legal move in UCI format.

## Search
Runs an iterative-deepening negamax search with the following additions:
- Alpha-beta pruning with principal variation search
- Transposition table keyed on a hash of the position, storing depth, score, bound flag (exact / lower / upper), and best move. Mate scores are stored ply-adjusted to keep them consistent across transpositions.
- Null-move pruning at depths ≥ 3, guarded against positions where the side to move has no non-pawn material and skipped when in check
- Late move reductions (LMR) for quiet moves after the first four, with re-search at full depth if a reduced search raises alpha
- Quiescence search at leaf nodes: searches all captures and promotions, and all legal moves when in check, to a depth limit of 6
- Aspiration windows during iterative deepening, widening on fail-high/fail-low
- Time management that allocates a per-move budget from the remaining clock, with a hard deadline checked every 32 nodes 

## Evaluation 
The evaluation is a hand-crafted static function, computed from the side to move's perspective.
- Material using standard piece values (pawn 100, knight 320, bishop 330, rook 500, queen 900, king 20000)
- Piece-square tables, interpolated between midgame and endgame sets based on remaining material. The phase value runs from 0 (full middlegame) to 256 (deep endgame), and each square's bonus is a linear blend of its midgame and endgame values.
- Tempo bonus of +10 for the side to move
Material and PST terms are accumulated from White's perspective, then flipped if Black is to move. This is the single most error-prone part of the code, and it is deliberately kept simple.

## Move Ordering
Moves are ordered before search using a tiered scoring scheme:
- Transposition table move (highest priority)
- Captures, scored by MVV-LVA (victim × 16 − attacker)
- Promotions
- Killer moves (two per ply)
- History heuristic, keyed by (color, from_square, to_square)
Killer moves and history are updated on beta cutoffs, with history decayed periodically to prevent overflow.

## Draw and Repetition Handling
The engine tracks position history across the real game so it can identify threefold repetitions. There is no anti-draw mechanic. An earlier version attempted to avoid repetitions when the engine was ahead, but it converted winning positions into losses by picking suboptimal non-repeating alternatives. It has been removed. The engine will accept a draw in a drawn position and will not fight to avoid a repetition that the search evaluates as correct. Position history is still recorded for bookkeeping, but no decision in the engine reads it.