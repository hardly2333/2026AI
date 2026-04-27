import unittest
from Convert_input import is_variable, parse_atom_formula, load_kb

class TestConvertInput(unittest.TestCase):
    def test_is_variable(self):
        self.assertTrue(is_variable('x'))
        self.assertFalse(is_variable('aiaiaiai'))
        self.assertFalse(is_variable('a'))

    def test_parse_atom_formula(self):
        #test case 1: negative atom formula
        formula = "~P(x)"
        negative, predicate, args = parse_atom_formula(formula)
        self.assertTrue(negative)
        self.assertEqual(predicate, 'P')
        self.assertEqual(args, ('x',))

        #test case 2: muiltiple args
        formula = "Q(a,b,c)"
        negative, predicate, args = parse_atom_formula(formula)
        self.assertFalse(negative)
        self.assertEqual(predicate, 'Q')
        self.assertEqual(args, ('a', 'b', 'c',))

        #test case 3: func in args
        formula = "R(f(x),g(y,z))"
        negative, predicate, args = parse_atom_formula(formula)
        self.assertFalse(negative)
        self.assertEqual(predicate, 'R')
        self.assertEqual(args, (('f', ('x',)), ('g', ('y', 'z'))))

    def test_load_kb(self):
        clause_list = ["(P(x), ~Q(a),)", "(~R(f(x)), S(y,z),)"]
        kb = load_kb(clause_list)
        self.assertEqual(len(kb), 2)
        expected_c1 = (
            (False, 'P', ('x',)), 
            (True, 'Q', ('a',))
        )
        expected_c2 = (
            (True, 'R', (('f', ('x',)),)), 
            (False, 'S', ('y', 'z'))
        )
        self.assertIn(expected_c1, kb)
        self.assertIn(expected_c2, kb)
if __name__ == '__main__':
    unittest.main()