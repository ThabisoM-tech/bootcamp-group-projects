# Dictionary mapping each card rank (as a string) to its Blackjack point value.
# J/Q/K all count as 10. Ace starts as 11; hand_value() below knocks it down
# to 1 automatically whenever counting it as 11 would bust the hand.
RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}


def hand_value(cards):
    """Calculate the best possible total for a hand of cards.

    Adds up every card's value assuming Aces are worth 11, then, while
    the hand is over 21 and there's still an Ace being counted as 11,
    converts one Ace at a time down to 1 (i.e. subtracts 10) until the
    hand is 21 or under, or there are no more Aces left to soften.
    """
    total = sum(RANK_VALUES[card] for card in cards)  # sum every card at face value (Ace = 11)
    aces = cards.count("A")  # how many Aces are in the hand, in case we need to soften them
    while total > 21 and aces > 0:  # while we're busting AND still have an Ace we could soften
        total -= 10  # turn one Ace from 11 down to 1 (a difference of 10)
        aces -= 1  # that Ace has been used up, so it can't be softened again
    return total  # the best legal total for this hand


# The four actions that are only legal as the player's very first decision
# this turn (before any Hit has happened). Plain strings, not an Enum, so
# they compare directly and cleanly against whatever the caller/tests pass in.
FIRST_DECISION_ONLY = {"double", "split", "surrender", "insurance"}

# Every action name that exists at all. Used purely to catch typos/garbage
# action names early, with a clear error, before we even check legality.
ALL_ACTIONS = {"hit", "stand"} | FIRST_DECISION_ONLY


class State:
    """A single decision point in a player's turn.

    hand: tuple of card-rank strings, e.g. ("10", "6")
    dealer_upcard: the dealer's single visible card, e.g. "9"
    first_decision: True if the player hasn't hit yet this turn
    """

    def __init__(self, hand, dealer_upcard, first_decision):
        self.hand = tuple(hand)  # store as a tuple so a State's hand can't be mutated in place
        self.dealer_upcard = dealer_upcard  # dealer's visible card, needed for the Insurance rule
        self.first_decision = first_decision  # gates Double/Split/Surrender/Insurance

    def __repr__(self):
        # Makes failing test output and debugging readable, e.g.
        # State(hand=('10', '6'), dealer_upcard='9', first_decision=True)
        return (
            f"State(hand={self.hand!r}, "
            f"dealer_upcard={self.dealer_upcard!r}, "
            f"first_decision={self.first_decision!r})"
        )


def parse_state(text):
    """Turn a decision-point string like '10,6 | 9 | first' into a State.

    The string has three '|'-separated fields: the player's hand (comma
    separated ranks), the dealer's up card, and either 'first' or 'later'.
    """
    # Split on '|', then strip whitespace from each of the three fields.
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]

    # Split the hand field on ',' and strip whitespace from each rank.
    hand = [rank.strip() for rank in hand_str.split(",")]

    # Build and return the State. first_decision is True only when the
    # flag field is exactly the word "first".
    return State(
        hand=hand,
        dealer_upcard=dealer_upcard,
        first_decision=(flag == "first"),
    )


def generate_actions(state):
    """Return the set of legal action name strings at this decision point."""
    actions = {"hit", "stand"}  # Hit and Stand are legal at every decision point, no conditions

    if not state.first_decision:
        # Once the player has hit at least once, none of the "first decision
        # only" actions are available any more, so we can return early.
        return actions

    # From here on, we know this IS the first decision, so check each of
    # the four restricted actions individually.

    actions.add("double")  # Double Down: always allowed on the first decision
    actions.add("surrender")  # Surrender: always allowed on the first decision

    if len(state.hand) == 2 and state.hand[0] == state.hand[1]:
        # Split needs exactly two cards of the same rank (e.g. two 8s).
        actions.add("split")

    if state.dealer_upcard == "A":
        # Insurance is only offered when the dealer's up card is an Ace.
        actions.add("insurance")

    return actions


def _hand_result(hand):
    """Build the standard result dict for a single resulting hand.

    Every action's outcome is described the same way: the cards in the
    hand, its best total (via hand_value), and whether it's busted.
    This helper keeps that logic in one place instead of repeating it
    in every branch of apply_action.
    """
    total = hand_value(hand)  # compute the best total for this hand (Ace-aware)
    return {
        "hand": list(hand),  # cards as a plain list, e.g. ["10", "6", "K"]
        "total": total,  # the hand's numeric total
        "busted": total > 21,  # True if this hand has gone over 21
    }


def apply_action(state, action, next_card=None):
    """Apply `action` (a string) to `state` and return the outcome.

    Returns a single result dict (with "hand", "total", "busted") for
    every action except "split", which returns a TUPLE OF TWO result
    dicts -- one per new hand created by the split.

    `next_card` is the card drawn from the deck; it's required for "hit"
    and "double" (since both draw a card), and ignored for every other
    action.
    """
    if action not in ALL_ACTIONS:
        # Catches typos / unknown action names with a clear message,
        # separately from "legal at this decision point" below.
        raise ValueError(f"{action!r} is not a recognized action")

    if action not in generate_actions(state):
        # E.g. trying to Split a non-pair, or Double Down after already
        # having hit once this turn.
        raise ValueError(f"{action!r} is not legal at this decision point")

    if action == "hit":
        if next_card is None:
            raise ValueError("Hit requires a next_card")
        # Add the drawn card to the hand; turn ends only if it busts,
        # which is reflected in the returned "busted" flag.
        return _hand_result(state.hand + (next_card,))

    if action == "double":
        if next_card is None:
            raise ValueError("Double Down requires a next_card")
        # Exactly one more card, then the turn is over (standing is
        # implied by Double Down, so no extra "hit again" step here).
        return _hand_result(state.hand + (next_card,))

    if action == "stand":
        # No new cards; the hand is exactly what it already was.
        return _hand_result(state.hand)

    if action == "surrender":
        # Hand shape doesn't change; forfeiting half the bet is a
        # betting concern outside this project's scope.
        return _hand_result(state.hand)

    if action == "insurance":
        # Insurance is a side bet and doesn't touch the player's hand
        # at all, so the hand is returned unchanged.
        return _hand_result(state.hand)

    if action == "split":
        # A pair (guaranteed by generate_actions) becomes two separate
        # one-card hands, each built from one of the original two cards.
        first_card, second_card = state.hand
        return _hand_result((first_card,)), _hand_result((second_card,))

    # Should be unreachable: every string in ALL_ACTIONS is handled above.
    raise ValueError(f"Unhandled action: {action}")

# import unittest
# import blackjack


# class TestBlackjackActions(unittest.TestCase):
#     def test_hit_and_stand_always_legal(self):
#         state = blackjack.parse_state("10,6 | 9 | later")
#         actions = blackjack.generate_actions(state)
#         self.assertIn("hit", actions)
#         self.assertIn("stand", actions)
#         self.assertNotIn("double", actions)
#         self.assertNotIn("surrender", actions)

#     def test_double_and_surrender_only_on_first_decision(self):
#         state = blackjack.parse_state("10,6 | 9 | first")
#         actions = blackjack.generate_actions(state)
#         self.assertIn("double", actions)
#         self.assertIn("surrender", actions)
#         self.assertNotIn("split", actions)

#     def test_split_requires_matching_rank(self):
#         pair_state = blackjack.parse_state("8,8 | 5 | first")
#         self.assertIn("split", blackjack.generate_actions(pair_state))

#         mismatched_state = blackjack.parse_state("10,K | 5 | first")
#         self.assertNotIn("split", blackjack.generate_actions(mismatched_state))

#     def test_insurance_only_against_ace_upcard(self):
#         vs_ace = blackjack.parse_state("10,9 | A | first")
#         self.assertIn("insurance", blackjack.generate_actions(vs_ace))

#         vs_six = blackjack.parse_state("10,9 | 6 | first")
#         self.assertNotIn("insurance", blackjack.generate_actions(vs_six))

#     def test_apply_hit_can_bust(self):
#         state = blackjack.parse_state("10,6 | 9 | first")
#         new_state = blackjack.apply_action(state, "hit", next_card="K")
#         self.assertEqual(new_state["total"], 26)
#         self.assertTrue(new_state["busted"])

#     def test_apply_split_returns_two_hands(self):
#         state = blackjack.parse_state("8,8 | 5 | first")
#         hand_a, hand_b = blackjack.apply_action(state, "split")
#         self.assertEqual(hand_a["hand"], ["8"])
#         self.assertEqual(hand_b["hand"], ["8"])

#     def test_apply_stand_leaves_hand_unchanged(self):
#         state = blackjack.parse_state("10,6 | 9 | first")
#         new_state = blackjack.apply_action(state, "stand")
#         self.assertEqual(new_state["hand"], ["10", "6"])
#         self.assertEqual(new_state["total"], 16)

#     def test_apply_double_takes_exactly_one_card(self):
#         state = blackjack.parse_state("5,6 | 9 | first")
#         new_state = blackjack.apply_action(state, "double", next_card="9")
#         self.assertEqual(new_state["hand"], ["5", "6", "9"])
#         self.assertEqual(new_state["total"], 20)
#         self.assertFalse(new_state["busted"])

#     def test_apply_surrender_ends_turn_without_new_card(self):
#         # 10 + 6 = 16, same starting hand as the Stand test. Surrendering
#         # should NOT draw a card (unlike Hit/Double), so the hand must
#         # stay exactly ["10", "6"] -- two cards, not three. The
#         # "surrendered" flag is the one thing that distinguishes this
#         # from an ordinary Stand, so we check for it explicitly.
#         state = blackjack.parse_state("10,6 | 9 | first")
#         new_state = blackjack.apply_action(state, "surrender")
#         self.assertEqual(new_state["hand"], ["10", "6"])
#         self.assertTrue(new_state["surrendered"])

#     def test_apply_insurance_leaves_state_unchanged(self):
#         # Insurance is a side bet -- it shouldn't touch the hand at all.
#         # We compare new_state["total"] directly against the ORIGINAL
#         # state["total"] (rather than hardcoding a number) to prove
#         # nothing changed, whatever the starting total happens to be.
#         state = blackjack.parse_state("10,9 | A | first")
#         new_state = blackjack.apply_action(state, "insurance")
#         self.assertEqual(new_state["hand"], ["10", "9"])
#         self.assertEqual(new_state["total"], state["total"])    


# if __name__ == "__main__":
#     unittest.main()

 
