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


# Actions that are only legal as the very first decision of a turn.
FIRST_DECISION_ONLY = {
    Action.DOUBLE_DOWN,
    Action.SPLIT,
    Action.SURRENDER,
    Action.INSURANCE,
}


@dataclass(frozen=True)
class State:
    hand: tuple
    dealer_upcard: str
    first_decision: bool


def parse_state(text):
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]
    hand = [rank.strip() for rank in hand_str.split(",")]
    return State(
        hand=tuple(hand),
        dealer_upcard=dealer_upcard,
        first_decision=(flag == "first"),
    )


def generate_actions(state):
    actions = {Action.HIT, Action.STAND}

    if not state.first_decision:
        return actions

    actions.add(Action.DOUBLE_DOWN)
    actions.add(Action.SURRENDER)

    if len(state.hand) == 2 and state.hand[0] == state.hand[1]:
        actions.add(Action.SPLIT)

    if state.dealer_upcard == "A":
        actions.add(Action.INSURANCE)

    return actions


def apply_action(state, action, next_card=None):
    """Apply `action` to `state`.

    Returns the resulting hand (a tuple of cards) for every action
    except SPLIT, which returns a tuple of two hands.

    `next_card` is the card drawn from the deck; required for HIT and
    DOUBLE_DOWN, ignored otherwise.
    """
    if action not in generate_actions(state):
        raise ValueError(f"{action.value} is not legal at this decision point")

    if action == Action.HIT:
        if next_card is None:
            raise ValueError("Hit requires a next_card")
        return state.hand + (next_card,)

    if action == Action.DOUBLE_DOWN:
        if next_card is None:
            raise ValueError("Double Down requires a next_card")
        return state.hand + (next_card,)

    if action == Action.STAND:
        return state.hand

    if action == Action.SURRENDER:
        return state.hand

    if action == Action.INSURANCE:
        return state.hand

    if action == Action.SPLIT:
        first_card, second_card = state.hand
        return (first_card,), (second_card,)

    raise ValueError(f"Unhandled action: {action}")

