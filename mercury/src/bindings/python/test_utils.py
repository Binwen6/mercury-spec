import unittest

from utils import validate_pytree, tree_map, StructureInvalidException

class TestValidatePytree(unittest.TestCase):

    def test_valid_pytree(self):
        pytree = {
            'name': 'Alice',
            'age': 25,
            'address': {
                'street': '1234 Elm St',
                'city': 'Sample City'
            },
            'scores': [90, 85, 95]
        }

        template = {
            'name': str,
            'age': int,
            'address': {
                'street': str,
                'city': str
            },
            'scores': [int, int, int]
        }

        result = validate_pytree(pytree, template, isinstance)
        self.assertTrue(result)
    
    def test_valid_pytree_custom_predicate(self):
        pytree = {
            'name': 2,
            'age': 25,
            'address': {
                'street': 4,
                'city': 3
            },
            'scores': [91, 85, 95]
        }

        template = {
            'name': 0,
            'age': 1,
            'address': {
                'street': 0,
                'city': 1
            },
            'scores': [1, 1, 1]
        }

        result = validate_pytree(pytree, template, lambda x, y: x % 2 == y)
        self.assertTrue(result)
    
    def test_invalid_pytree_custom_predicate(self):
        pytree = {
            'name': 2,
            'age': 25,
            'address': {
                'street': 4,
                'city': 3
            },
            'scores': [91, 85, 95]
        }

        template = {
            'name': 0,
            'age': 1,
            'address': {
                'street': 0,
                'city': 0
            },
            'scores': [1, 1, 1]
        }

        result = validate_pytree(pytree, template, lambda x, y: x % 2 == y)
        self.assertFalse(result)

    def test_missing_key(self):
        pytree = {
            'name': 'Bob',
            'address': {
                'street': '5678 Oak St',
                'city': 'Sample City'
            },
            'scores': [90, 85, 95]
        }

        template = {
            'name': str,
            'age': int,
            'address': {
                'street': str,
                'city': str
            },
            'scores': [int, int, int],
            'email': str
        }

        result = validate_pytree(pytree, template, isinstance)
        self.assertFalse(result)

    def test_incorrect_type(self):
        pytree = {
            'name': 'Alice',
            'age': 25,
            'address': {
                'street': '1234 Elm St',
                'city': 'Sample City'
            },
            'scores': [90, 85, 'A']
        }

        template = {
            'name': str,
            'age': int,
            'address': {
                'street': str,
                'city': str
            },
            'scores': [int, int, int]
        }

        result = validate_pytree(pytree, template, isinstance)
        self.assertFalse(result)

    def test_different_structures(self):
        pytree = {
            'name': 'Alice',
            'age': 25,
            'address': {
                'street': '1234 Elm St',
                'city': 'Sample City'
            },
            'scores': [90, 85, 95]
        }

        template = {
            'name': str,
            'age': int,
            'address': {
                'street': str,
                'city': str
            },
        }

        result = validate_pytree(pytree, template, isinstance)
        self.assertTrue(result)

    def test_terminal_template(self):
        pytree = [1]
        template = [int]

        result = validate_pytree(pytree, template, isinstance)
        self.assertTrue(result)

    def test_empty_pytree(self):
        pytree = {}
        template = {
            'name': str,
            'age': int
        }

        result = validate_pytree(pytree, template, isinstance)
        self.assertFalse(result)

    def test_empty_template(self):
        pytree = {
            'name': 'Alice',
            'age': 25
        }
        template = {}

        result = validate_pytree(pytree, template, isinstance)
        self.assertTrue(result)

def square(x, y, z):
    return x ** 2 + y ** 2 + z ** 2

class TestTreeMap(unittest.TestCase):
    def test_single_pytrees(self):
        pytrees = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = tree_map(pytrees, square)
        self.assertEqual(result, [66, 93, 126])
    
    def test_nested_pytrees(self):
        pytrees = [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
            [[9, 10], [11, 12]]
        ]
        result = tree_map(pytrees, square)
        self.assertEqual(result, [[107, 140], [179, 224]])
    
    def test_mixed_pytrees(self):
        pytrees = [[
            [1, 2, 3],
            {'a': [4, 5, 6], 'b': [7, 8, 9]},
            ((10, 11, 12),)
        ]]
        result = tree_map(pytrees, lambda x: x ** 2)
        self.assertEqual(result, [[1, 4, 9], {'a': [16, 25, 36], 'b': [49, 64, 81]}, ((100, 121, 144),)])
    
    def test_different_structures_tuple(self):
        pytrees = [
            [1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10]
        ]
        with self.assertRaises(StructureInvalidException):
            tree_map(pytrees, square)

    def test_different_structures_dict(self):
        pytrees = [
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 4, 'b': 5, 'd': 6},
            {'a': 8, 'b': 9, 'c': 10}
        ]
        with self.assertRaises(StructureInvalidException):
            tree_map(pytrees, square)
    
    def test_first_pytree_not_terminal(self):
        pytrees = [
            [[1, 2, 3], [4, 5, 6]],
            [7, 8, 9],
            [10, 11, 12]
        ]
        with self.assertRaises(StructureInvalidException):
            tree_map(pytrees, square)


if __name__ == '__main__':
    unittest.main()
