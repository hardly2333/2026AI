import unittest
from Convert_input import is_variable, split_args, parse_term, parse_atom_formula, parse_clause
from MGU import unify, apply_dict, unify_var, occurs_check
class TestMGU(unittest.TestCase):

    def test_unify(self):
        # a,a -> None
        self.assertEqual(unify('a', 'a', {}), {})
        # a,b -> None
        self.assertIsNone(unify('a', 'b', {}))
        # x,a -> {x: a}
        self.assertEqual(unify('x', 'a', {}), {'x': 'a'})
        # x,y -> {x: y} or {y: x}
        res = unify('x', 'y', {})
        self.assertTrue(res == {'x': 'y'} or res == {'y': 'x'})

    def test_unify_atoms(self):
        # P(x) , P(a) -> {x: a}
        atom1 = (False, 'P', ('x',))
        atom2 = (False, 'P', ('a',))
        self.assertEqual(unify(atom1, atom2, {}), {'x': 'a'})
        # P(x, b) , P(a, y) -> {x: a, y: b}
        atom3 = (False, 'P', ('x', 'b'))
        atom4 = (False, 'P', ('a', 'y'))
        self.assertEqual(unify(atom3, atom4, {}), {'x': 'a', 'y': 'b'})

    def test_MGU_example1(self):
        # ppt1 P(xx,a), P(b,yy) -> {xx: b, yy: a}
        atom1 = (False, 'P', ('xx', 'a'))
        atom2 = (False, 'P', ('b', 'yy'))
        expected = {'xx': 'b', 'yy': 'a'}
        self.assertEqual(unify(atom1, atom2, {}), expected)

    def test_MGU_example2(self):
        # ppt2 P(a,xx,f(g(yy))) , P(zz,f(zz),f(uu)) -> {zz: a, xx: f(a), uu: g(yy)}
        atom1 = (False, 'P', ('a', 'xx', ('f', (('g', ('yy',)),))))
        atom2 = (False, 'P', ('zz', ('f', ('zz',)), ('f', ('uu',))))
        res = unify(atom1, atom2, {})
        self.assertIsNotNone(res)
        self.assertEqual(res['zz'], 'a')
        self.assertEqual(res['xx'], ('f', ('a',)))
        self.assertEqual(res['uu'], ('g', ('yy',)))

    def test_occurs_check_fail(self):
        atom1 = 'x'
        atom2 = ('f', ('x',))
        self.assertIsNone(unify(atom1, atom2, {}))

    def test_composition(self):
        # {x:y} , y:a -> {x:a, y:a}
        sub = {'x': 'y'}
        res = unify('y', 'a', sub)
        self.assertEqual(res['x'], 'a')
        self.assertEqual(res['y'], 'a')

if __name__ == '__main__':
    unittest.main()