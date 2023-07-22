import unittest

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent))

from src.mercury_nn.tag_matching import parseCondensedTags, InvalidCondensedTagsException

class TestParseCondensedTags(unittest.TestCase):
    
    def test_successful_empty(self):
        self.assertEqual(parseCondensedTags(''), set())
        self.assertEqual(parseCondensedTags('{}'), set())
        self.assertEqual(parseCondensedTags('{{}}'), set())
        self.assertEqual(parseCondensedTags('{{{}}}'), set())
    
    def test_successful_composition(self):
        self.assertEqual(parseCondensedTags('{{a}}'), {'a'})
        self.assertEqual(parseCondensedTags('a'), {'a'})
        self.assertEqual(parseCondensedTags('a, b'), {'a', 'b'})
        self.assertEqual(parseCondensedTags('a, d::{b, c}'), {'a', 'd::b', 'd::c'})
        self.assertEqual(parseCondensedTags('a, d.{b, c}'), {'a', 'd', 'd::b', 'd::c'})
        self.assertEqual(parseCondensedTags(',,,'), set())
        self.assertEqual(parseCondensedTags('''{},
                                            , ,
                                            {}'''), set())
        self.assertEqual(parseCondensedTags('{, , , }'), set())
        self.assertEqual(parseCondensedTags('''
                                            {{a1.b1::{
                                                c1,
                                                {{dd1::ee1.{x, y}}},
                                                f1.g1}}}
                                            '''),
                         {'a1', 'a1::b1::c1', 'a1::b1::dd1::ee1', 'a1::b1::dd1::ee1::x', 'a1::b1::dd1::ee1::y', 'a1::b1::f1', 'a1::b1::f1::g1'})
        
        self.assertEqual(parseCondensedTags(
            '''
            a1.b1::{
                c1,
                dd1::ee1.{
                    z.{
                        u, v
                    },
                    x, y},
            },
            test
            '''
        ), {'a1', 'a1::b1::c1', 'a1::b1::dd1::ee1', 'a1::b1::dd1::ee1::z', 'a1::b1::dd1::ee1::z::u', 'a1::b1::dd1::ee1::z::v', 'a1::b1::dd1::ee1::x', 'a1::b1::dd1::ee1::y', 'test'})

        self.assertEqual(parseCondensedTags('{{{a}}}, {}, , , {{b}}, , , {{{}}}, {{{{{}}}}}, {c}, {{{d, e}}}'), {'a', 'b', 'c', 'd', 'e'})
    
    def test_raises(self):
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('{')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('}')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('::')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('.')
            
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('::a')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a::')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('.a')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a.')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a..b')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a::::b')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a::.b')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a.::b')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('a::b.')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('::a.b')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('{a, b}::')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('::{a, b}')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('{a, b}.')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('.{a, b}')
        
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('{a, b}}')
            
        with self.assertRaises(InvalidCondensedTagsException):
            parseCondensedTags('{{a, b}')

if __name__ == '__main__':
    unittest.main()