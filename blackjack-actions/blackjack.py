# RANK_VALUES: how much each card is worth.
# J/Q/K all count as 10, and Ace is stored as 11 here (hand_value below
# knocks it down to 1 whenever counting it as 11 would bust the hand).
RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10, "A": 11,
}


def hand_value(cards):  
    # Add up every card assuming each Ace is worth 11 .
    total = sum(RANK_VALUES[card] for card in cards)
    aces = cards.count("A")
    # If that puts us over 21, re-count Aces as 1 instead of 11, one at a
    # time, until we're back at or under 21 (or we've run out of Aces to
    # downgrade). Each downgrade removes exactly 10 from the total
    # (11 - 1 = 10).
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def parse_state(text):
    # A decision point looks like "10,6 | 9 | first":
    #   - hand_str    -> "10,6"   (the player's cards, comma-separated)
    #   - dealer_upcard -> "9"    (the dealer's single visible card)
    #   - flag        -> "first" or "later" (has the player already hit?)
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")]
    hand = [rank.strip() for rank in hand_str.split(",")]

    # We return a dict (not a plain tuple) so every field has a name.
    # This same shape is used everywhere in the game: it's what
    # parse_state hands out, what apply_action hands back, and what
    # generate_actions reads from. Keeping one consistent shape means
    # every function can be trusted to receive/return the same thing.
    #
    #   hand          -> list of card ranks still in hand, e.g. ["10", "6"]
    #   dealer_upcard -> the dealer's visible card, e.g. "9"
    #   first         -> True if no action has been taken yet this turn
    #   total         -> the hand's current blackjack value
    #   busted        -> True if that value is over 21
    return {
        "hand": hand,
        "dealer_upcard": dealer_upcard,
        "first": flag == "first",
        "total": hand_value(hand),
        "busted": hand_value(hand) > 21,
    }


def generate_actions(state):
  raise NotImplementedError("This function is not implemented yet.")
        



def apply_action(state, action, next_card=None):   
 raise NotImplementedError("This function is not implemented yet.")
    