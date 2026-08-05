from dataclasses import dataclass
from enum import Enum

RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}


def hand_value(cards):
    total = sum(RANK_VALUES[card] for card in cards)
    aces = cards.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE_DOWN = "double_down"
    SPLIT = "split"
    SURRENDER = "surrender"
    INSURANCE = "insurance"

# Actions that are only legal as the very first decision of a turn
FIRST_DECISION_ONLY = {
    Action.DOUBLE_DOWN,
    Action.SPLIT,
    Action.SURRENDER,
    Action.INSURANCE,
}


@dataclass(frozen = True)
class State:
    hand: tuple
    dealer_upcard; str
    first_decision: bool

def parse_state(text):
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]
    hand = [rank.strip() for rank in hand_str.split(",")]

    return ...


def generate_actions(state):
    raise NotImplementedError("This function is not implemented yet.")


def apply_action(state, action, next_card=None):
    raise NotImplementedError("This function is not implemented yet.")

    """
        KARABO
    """
