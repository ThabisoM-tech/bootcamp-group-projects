import unittest
import blackjack

class TestBlackjackActions(unittest.TestCase):
    def test_hit_and_stand_always_legal(self):
        state = blackjack.parse_state("10,6 | 9 | later")
        actions = blackjack.generate_actions(state)
        self.assertIn("hit", actions)
        self.assertIn("stand", actions)
        self.assertNotIn("double", actions)
        self.assertNotIn("surrender", actions)

    def test_double_and_surrender_only_on_first_decision(self):
        state = blackjack.parse_state("10,6 | 9 | first")
        actions = blackjack.generate_actions(state)
        self.assertIn("double", actions)
        self.assertIn("surrender", actions)
        self.assertNotIn("split", actions)

    def test_split_requires_matching_rank(self):
        pair_state = blackjack.parse_state("8,8 | 5 | first")
        self.assertIn("split", blackjack.generate_actions(pair_state))

        mismatched_state = blackjack.parse_state("10,K | 5 | first")
        self.assertNotIn("split", blackjack.generate_actions(mismatched_state))

    def test_insurance_only_against_ace_upcard(self):
        vs_ace = blackjack.parse_state("10,9 | A | first")
        self.assertIn("insurance", blackjack.generate_actions(vs_ace))

        vs_six = blackjack.parse_state("10,9 | 6 | first")
        self.assertNotIn("insurance", blackjack.generate_actions(vs_six))

    def test_apply_hit_can_bust(self):
        state = blackjack.parse_state("10,6 | 9 | first")
        new_state = blackjack.apply_action(state, "hit", next_card="K")
        self.assertEqual(new_state["total"], 26)
        self.assertTrue(new_state["busted"])

    def test_apply_split_returns_two_hands(self):
        state = blackjack.parse_state("8,8 | 5 | first")
        hand_a, hand_b = blackjack.apply_action(state, "split")
        self.assertEqual(hand_a["hand"], ["8"])
        self.assertEqual(hand_b["hand"], ["8"])
        
if __name__ == "__main__":
    unittest.main()

 
