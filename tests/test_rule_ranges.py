import unittest
from game import GameOfLife
from neighbor_utils import get_max_neighbors


class RuleRangeTests(unittest.TestCase):
    def test_hex_invalid_birth_removed(self):
        game = GameOfLife()
        game.shape = 'hexagon'
        # Set a single lifeform with an invalid rule
        game.lifeforms = game.lifeforms[:1]
        game.number_of_lifeforms = 1
        panel = game.settings_panel
        panel.lifeform_rules[1]['birth_rules'] = '2,6,8'
        panel.lifeform_rules[1]['survival_rules'] = '2,3'
        panel.apply_settings()
        lf = game.lifeforms[0]
        self.assertNotIn(8, lf.birth_rules)
        self.assertEqual(sorted(lf.birth_rules), [2, 6])

    def test_randomise_respects_max_n(self):
        for shape, tri_mode in [('hexagon', 'edge'), ('hexagon', 'edge+vertex'), ('triangle', 'edge'), ('triangle', 'edge+vertex'), ('square', 'edge')]:
            game = GameOfLife()
            game.shape = shape
            game.triangle_mode = tri_mode if shape == 'triangle' else 'edge'
            max_n = get_max_neighbors(shape, game.triangle_mode)
            game.randomise_lifeforms()
            for lf in game.lifeforms:
                self.assertTrue(all(0 <= v <= max_n for v in lf.birth_rules))
                self.assertTrue(all(0 <= v <= max_n for v in lf.survival_rules))


if __name__ == "__main__":
    unittest.main()
