"""Who moves first, chosen the folk way. No pygame, so it is easy to test.

Two players play oẳn tù tì (rock-paper-scissors): rock beats scissors,
scissors beat paper, paper beats rock, and the same hand is played again.
Three or four players first show a hand palm down or palm up at the same
time ("úp lá xòe"): whoever shows differently from the others drops out,
and an even split or everyone the same is played again. When two are left
they play oẳn tù tì. The winner moves first; play then goes round the board
in the usual order.
"""

import random

ROCK_PAPER_SCISSORS = ('rock', 'scissors', 'paper')
DOWN_UP = ('down', 'up')
_BEATS = {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}


def hands_for(contenders):
    """The hands to choose from in the next round."""
    return ROCK_PAPER_SCISSORS if len(contenders) == 2 else DOWN_UP


def settle(contenders, hands):
    """Play one round; `hands` maps each contender to the hand shown.

    Returns the contenders still in: one (who moves first), fewer than
    before, or all of them when the round must be played again.
    """
    contenders = list(contenders)
    if len(contenders) == 2:
        a, b = contenders
        if hands[a] == hands[b]:
            return contenders
        return [a] if _BEATS[hands[a]] == hands[b] else [b]
    down = [c for c in contenders if hands[c] == 'down']
    up = [c for c in contenders if hands[c] == 'up']
    if len(down) == len(up) or not down or not up:
        return contenders
    return down if len(down) > len(up) else up


def bot_hand(contenders, rng=random):
    return rng.choice(hands_for(contenders))
