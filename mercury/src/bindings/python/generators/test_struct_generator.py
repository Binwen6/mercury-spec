import unittest

from struct_generator import dash_separated_to_upper_camel_case

class TestStructGeneratorMethods(unittest.TestCase):
    
    def test_dash_separated_to_upper_camel_case(self):
        # case 1
        self.assertEqual(dash_separated_to_upper_camel_case('koalas-are-cute'), 'KoalasAreCute')
        # case 2
        self.assertEqual(dash_separated_to_upper_camel_case('kOalas-a2Re-3cute'), 'KOalasA2Re3cute')
        # case 3
        self.assertEqual(dash_separated_to_upper_camel_case('Koala'), 'Koala')

        # failures
        incorrect_exception_failure = Exception('Exception was not correctly raised!')

        exception = None
        
        # first letter cannot be number
        try:
            dash_separated_to_upper_camel_case('3')
            raise incorrect_exception_failure
        except Exception as e:
            exception = e
        
        self.assertNotEqual(exception, incorrect_exception_failure)

        # no empty words
        try:
            dash_separated_to_upper_camel_case('k-')
            raise incorrect_exception_failure
        except Exception as e:
            exception = e
        
        self.assertNotEqual(exception, incorrect_exception_failure)
        
        # no spaces / weird characters
        try:
            dash_separated_to_upper_camel_case('k o')
            raise incorrect_exception_failure
        except Exception as e:
            exception = e
        
        self.assertNotEqual(exception, incorrect_exception_failure)

if __name__ == '__main__':
    unittest.main()