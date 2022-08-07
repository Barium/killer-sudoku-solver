import unittest

import solver


class Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.cages = [
            (6,  [(5, 1)]),
            (7,  [(8, 4)]),
            (13, [(0, 0), (1, 0)]),
            (14, [(2, 0), (2, 1)]),
            (3,  [(0, 1), (1, 1)]),
            (4,  [(3, 0), (3, 1)]),
            (14, [(4, 0), (4, 1)]),
            (15, [(5, 0), (6, 0)]),
            (5,  [(7, 0), (8, 0)]),
            (8,  [(3, 2), (3, 3)]),
            (15, [(4, 2), (4, 3)]),
            (10, [(6, 2), (6, 3)]),
            (4,  [(1, 3), (2, 3)]),
            (16, [(2, 4), (2, 5)]),
            (13, [(3, 4), (3, 5)]),
            (7,  [(6, 4), (7, 4)]),
            (7,  [(6, 5), (7, 5)]),
            (9,  [(0, 8), (1, 8)]),
            (10, [(6, 7), (7, 7)]),
            (6,  [(6, 8), (7, 8)]),
            (17, [(8, 7), (8, 8)]),
            (15, [(0, 2), (1, 2), (2, 2)]),
            (18, [(8, 2), (7, 3), (8, 3)]),
            (15, [(4, 5), (5, 5), (4, 6)]),
            (12, [(2, 6), (2, 7), (1, 7)]),
            (14, [(3, 6), (3, 7), (4, 7)]),
            (16, [(5, 6), (5, 7), (5, 8)]),
            (18, [(2, 8), (3, 8), (4, 8)]),
            (25, [(6, 1), (7, 1), (8, 1), (7, 2)]),
            (10, [(5, 2), (5, 3), (5, 4), (4, 4)]),
            (17, [(0, 3), (0, 4), (1, 4), (1, 5)]),
            (15, [(8, 5), (8, 6), (7, 6), (6, 6)]),
            (27, [(0, 5), (0, 6), (0, 7), (1, 6)]),
        ]

        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 5, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 6, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 7, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        # Create look-up caches to speed up the process of finding cages and limiting the possible
        # values of each cell.
        self.cage_cache = []
        self.minmax_cache = []
        for y in range(9):
            cage_row = []
            minmax_row = []
            for x in range(9):
                cage_row.append(solver.find_cage_index(self.cages, x, y))
                minmax_row.append(solver.find_minmax_value(self.cages, x, y))
            self.cage_cache.append(cage_row)
            self.minmax_cache.append(minmax_row)

    def test_find_cage_index(self):
        self.assertEqual(21, solver.find_cage_index(self.cages, 1, 2))
        self.assertEqual(2, solver.find_cage_index(self.cages, 0, 0))
        self.assertEqual(6, solver.find_cage_index(self.cages, 4, 0))
        with self.assertRaises(AssertionError):
            solver.find_cage_index(self.cages, 9, 9)

    def test_is_same_cage(self):
        self.assertTrue(solver.is_same_cage(self.cages, 0, 0, 1, 0))
        self.assertFalse(solver.is_same_cage(self.cages, 5, 0, 4, 0))

    def test_find_taken_value(self):
        taken_values_1 = solver.find_taken_value(self.board, self.cages, self.cage_cache, 0, 0)
        self.assertListEqual(list(set(taken_values_1)), [1, 2, 3 ])
        taken_values_2 = solver.find_taken_value(self.board, self.cages, self.cage_cache, 0, 4)
        self.assertListEqual(list(set(taken_values_2)), [5])
        taken_values_3 = solver.find_taken_value(self.board, self.cages, self.cage_cache, 4, 0)
        self.assertListEqual(list(set(taken_values_3)), [1, 2, 3, 4, 5])
        taken_values_4 = solver.find_taken_value(self.board, self.cages, self.cage_cache, 8, 8)
        self.assertListEqual(list(set(taken_values_4)), [1, 2, 3, 4, 5, 6, 7, 8])

    def test_find_minmax_value(self):
        min_value, max_value = solver.find_minmax_value(self.cages, 0, 0)
        self.assertTupleEqual((min_value, max_value), (4, 9))

    def test_find_nonet_range(self):
        self.assertListEqual([0, 1, 2], [i for i in solver.find_nonet_range(0)])
        self.assertListEqual([0, 1, 2], [i for i in solver.find_nonet_range(1)])
        self.assertListEqual([0, 1, 2], [i for i in solver.find_nonet_range(2)])
        self.assertListEqual([3, 4, 5], [i for i in solver.find_nonet_range(3)])
        self.assertListEqual([3, 4, 5], [i for i in solver.find_nonet_range(4)])
        self.assertListEqual([3, 4, 5], [i for i in solver.find_nonet_range(5)])
        self.assertListEqual([6, 7, 8], [i for i in solver.find_nonet_range(6)])
        self.assertListEqual([6, 7, 8], [i for i in solver.find_nonet_range(7)])
        self.assertListEqual([6, 7, 8], [i for i in solver.find_nonet_range(8)])
        self.assertListEqual([6, 7, 8], [i for i in solver.find_nonet_range(800)])

    def test_find_next_cell(self):
        self.assertTupleEqual(solver.find_next_cell(self.board, 0, 1), (2, 1))
        self.assertTupleEqual(solver.find_next_cell(self.board, 0, 0), (1, 0))
        self.assertTupleEqual(solver.find_next_cell(self.board, 8, 8), (-1, -1))

    def test_validate_rows(self):
        self.assertTrue(solver.validate_rows(self.board))

    def test_validate_cols(self):
        self.assertTrue(solver.validate_cols(self.board))

    def test_validate_nonets(self):
        self.assertTrue(solver.validate_nonets(self.board))

    def test_validate_cages(self):
        self.assertTrue(solver.validate_cages(self.board, self.cages))

    def test_validate(self):
        self.assertTrue(solver.validate(self.board, self.cages))


if __name__ == '__main__':
    unittest.main()
