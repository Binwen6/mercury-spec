import unittest

from utils import validate_pytree

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


if __name__ == '__main__':
    unittest.main()
