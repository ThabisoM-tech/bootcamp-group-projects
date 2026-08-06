from dataclasses import dataclass # Import the dataclass decorator to automatically generate special methods (like __init__) for data-storing classes
from enum import Enum # Import Enum to define a set of named, constant values for game actions

# Define a dictionary mapping string representations of card ranks to their integer values in Blackjack
RANK_VALUES = { # Start of dictionary definition for card values
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, # Number cards (2-10) are worth their face value
    "J": 10, "Q": 10, "K": 10, "A": 11, # Face cards (Jack, Queen, King) are worth 10, and Aces initially count as 11
} # End of dictionary definition

def hand_value(cards): # Define a function that calculates the total numerical value of a given hand of cards
    total = sum(RANK_VALUES[card] for card in cards) # Calculate the initial total by looking up each card in the RANK_VALUES dictionary and summing them
    aces = cards.count("A") # Count the total number of Aces present in the current hand
    while total > 21 and aces > 0: # Loop as long as the hand is busting (over 21) and there are still Aces that can be reduced
        total -= 10 # Reduce the hand's total value by 10 (effectively changing an Ace's value from 11 down to 1)
        aces -= 1 # Decrement the count of "soft" Aces remaining to process
    return total # Return the final, optimized total value of the hand


class Action(Enum): # Create an Enum class named Action to represent valid player moves
    HIT = "hit" # Define the HIT action (draw another card)
    STAND = "stand" # Define the STAND action (stop drawing cards)
    DOUBLE_DOWN = "double_down" # Define the DOUBLE_DOWN action (double bet, draw exactly one more card)
    SPLIT = "split" # Define the SPLIT action (split a pair into two separate hands)
    SURRENDER = "surrender" # Define the SURRENDER action (forfeit half the bet and end the hand)
    INSURANCE = "insurance" # Define the INSURANCE action (place a side bet when dealer shows an Ace)


# Actions that are only legal as the very first decision of a turn. # (Original comment retained)
FIRST_DECISION_ONLY = { # Define a set containing actions that can only be taken at the start of a hand
    Action.DOUBLE_DOWN, # Add the DOUBLE_DOWN action to the restricted set
    Action.SPLIT, # Add the SPLIT action to the restricted set
    Action.SURRENDER, # Add the SURRENDER action to the restricted set
    Action.INSURANCE, # Add the INSURANCE action to the restricted set
} # End of set definition


@dataclass(frozen=True) # Apply the dataclass decorator with frozen=True to make the State objects immutable (read-only)
class State: # Define the State class to represent the current game situation
    hand: tuple # Declare 'hand' as a tuple of strings representing the player's current cards
    dealer_upcard: str # Declare 'dealer_upcard' as a string representing the dealer's visible card
    first_decision: bool # Declare 'first_decision' as a boolean indicating if no actions have been taken yet


def parse_state(text): # Define a function to convert a formatted string into a State object
    hand_str, dealer_upcard, flag = [part.strip() for part in text.split("|")] # Split the input string by '|', remove whitespace, and unpack into three variables
    hand = [rank.strip() for rank in hand_str.split(",")] # Split the hand portion by commas, remove whitespace, and create a list of card strings
    return State( # Instantiate and return a new State object
        hand=tuple(hand), # Convert the list of cards into a tuple and assign it to the 'hand' attribute
        dealer_upcard=dealer_upcard, # Assign the parsed dealer card string to the 'dealer_upcard' attribute
        first_decision=(flag == "first"), # Evaluate if the flag string equals "first" and assign the resulting boolean to 'first_decision'
    ) # Close the State object instantiation


def generate_actions(state): # Define a function that returns a set of legally available actions for a given state
    actions = {Action.HIT, Action.STAND} # Initialize the set of available actions with HIT and STAND, which are almost always legal

    if not state.first_decision: # Check if the player has already made a move in this hand
        return actions # If it's not the first decision, return only the basic actions (Hit and Stand)

    actions.add(Action.DOUBLE_DOWN) # If it is the first decision, add DOUBLE_DOWN to the set of legal actions
    actions.add(Action.SURRENDER) # Also add SURRENDER to the set of legal actions

    if len(state.hand) == 2 and state.hand[0] == state.hand[1]: # Check if the hand contains exactly two cards and their ranks are identical
        actions.add(Action.SPLIT) # If the hand is a pair, add SPLIT to the set of legal actions

    if state.dealer_upcard == "A": # Check if the dealer's visible card is an Ace
        actions.add(Action.INSURANCE) # If the dealer shows an Ace, add INSURANCE to the set of legal actions

    return actions # Return the final calculated set of legal actions for this state


def apply_action(state, action, next_card=None): # Define a function to compute the result of taking a specific action
    """Apply `action` to `state`. # (Original docstring start)

    Returns the resulting hand (a tuple of cards) for every action # (Original docstring explanation)
    except SPLIT, which returns a tuple of two hands. # (Original docstring explanation)

    `next_card` is the card drawn from the deck; required for HIT and # (Original docstring explanation)
    DOUBLE_DOWN, ignored otherwise. # (Original docstring end)
    """ # Close docstring
    if action not in generate_actions(state): # Verify that the requested action is actually legal for the provided state
        raise ValueError(f"{action.value} is not legal at this decision point") # Raise an exception if the action is not in the legal actions set

    if action == Action.HIT: # Check if the player chose to HIT
        if next_card is None: # Ensure a new card was provided, since hitting requires drawing a card
            raise ValueError("Hit requires a next_card") # Raise an exception if the required next_card is missing
        return state.hand + (next_card,) # Create and return a new tuple combining the original hand with the newly drawn card

    if action == Action.DOUBLE_DOWN: # Check if the player chose to DOUBLE_DOWN
        if next_card is None: # Ensure a new card was provided, since doubling down requires drawing exactly one card
            raise ValueError("Double Down requires a next_card") # Raise an exception if the required next_card is missing
        return state.hand + (next_card,) # Create and return a new tuple combining the original hand with the final drawn card

    if action == Action.STAND: # Check if the player chose to STAND
        return state.hand # Return the current hand exactly as it is, since no new cards are drawn

    if action == Action.SURRENDER: # Check if the player chose to SURRENDER
        return state.hand # Return the current hand exactly as it is (hand ends here, bet logic is handled elsewhere)

    if action == Action.INSURANCE: # Check if the player chose to buy INSURANCE
        return state.hand # Return the current hand exactly as it is (side bet logic is handled elsewhere)

    if action == Action.SPLIT: # Check if the player chose to SPLIT their pair
        first_card, second_card = state.hand # Unpack the two identical cards from the current hand tuple into two separate variables
        return (first_card,), (second_card,) # Return a tuple containing two separate single-card tuples, representing the two new hands

    raise ValueError(f"Unhandled action: {action}") # Raise a fallback exception if an unrecognized action somehow passed previous checks
