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

    def test_apply_stand_leaves_hand_unchanged(self):
        state = blackjack.parse_state("10,6 | 9 | first")
        new_state = blackjack.apply_action(state, "stand")
        self.assertEqual(new_state["hand"], ["10", "6"])
        self.assertEqual(new_state["total"], 16)

    def test_apply_double_takes_exactly_one_card(self):
        state = blackjack.parse_state("5,6 | 9 | first")
        new_state = blackjack.apply_action(state, "double", next_card="9")
        self.assertEqual(new_state["hand"], ["5", "6", "9"])
        self.assertEqual(new_state["total"], 20)
        self.assertFalse(new_state["busted"])

    def test_apply_surrender_ends_turn_without_new_card(self):
        # 10 + 6 = 16, same starting hand as the Stand test. Surrendering
        # should NOT draw a card (unlike Hit/Double), so the hand must
        # stay exactly ["10", "6"] -- two cards, not three. The
        # "surrendered" flag is the one thing that distinguishes this
        # from an ordinary Stand, so we check for it explicitly.
        state = blackjack.parse_state("10,6 | 9 | first")
        new_state = blackjack.apply_action(state, "surrender")
        self.assertEqual(new_state["hand"], ["10", "6"])
        self.assertTrue(new_state["surrendered"])

    def test_apply_insurance_leaves_state_unchanged(self):
        # Insurance is a side bet -- it shouldn't touch the hand at all.
        # We compare new_state["total"] directly against the ORIGINAL
        # state["total"] (rather than hardcoding a number) to prove
        # nothing changed, whatever the starting total happens to be.
        state = blackjack.parse_state("10,9 | A | first")
        new_state = blackjack.apply_action(state, "insurance")
        self.assertEqual(new_state["hand"], ["10", "9"])
        self.assertEqual(new_state["total"], state["total"])    


if __name__ == "__main__":
    unittest.main()

 