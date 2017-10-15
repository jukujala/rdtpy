import pandas as pd
import unittest
from rdtpy import rdt

""" Unit tests for the rdt function
"""


class TestRDT(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})

    def test_scalar(self):
        result = rdt(self.df, ', sum(x) ')
        self.assertEqual(result, 6)

    def test_df(self):
        df2 = rdt(self.df, ', .(xs=sum(x)), by="y"')
        df3 = pd.DataFrame({"y": ["a", "b", "c"], "xs": [1, 2, 3]})
        self.assertTrue(df2["xs"].tolist() == df3["xs"].tolist())
        self.assertTrue(df2["y"].tolist() == df3["y"].tolist())

    def test_new_column(self):
        df2 = rdt(self.df, ', xs := sum(x)')
        self.assertTrue(df2["xs"].tolist() == [6, 6, 6])

    def test_factors(self):
        # if column is converted to factor then y>"a" returns empty DF
        result = rdt(self.df, 'y>"a", sum(x)')
        self.assertEqual(result, 5)

    def test_types(self):
        with self.assertRaises(TypeError):
            rdt(self.df, 5)
        with self.assertRaises(TypeError):
            rdt(5, ", sum(x)")

    def test_expression_chaining(self):
        result = rdt(self.df,
            ', .(xs=sum(x)), by="y"',
            ', mean(xs)'
        )
        self.assertEqual(result, 2.0)

if __name__ == '__main__':
    unittest.main()
