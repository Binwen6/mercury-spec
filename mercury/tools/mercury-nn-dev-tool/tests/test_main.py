import unittest

import sys
from typing import Tuple, List
from pathlib import Path
import os

import subprocess as sp

sys.path.append(str(Path(__file__).absolute().resolve().parent))

from config import Config


class TestValidateManifest(unittest.TestCase):
    
    @staticmethod
    def get_outputs(manifest_name: str) -> Tuple[str, str]:
        result = sp.run([
            'python',
            str(Config.mainPyExecutable),
            'validate-manifest',
            str(Config.manifestsRootDir.joinpath(f'manifest_{manifest_name}.xml'))
        ], capture_output=True)

        return result.stdout.decode(), result.stderr.decode()
    
    def test_valid(self):
        stdout, stderr = self.get_outputs('valid')
        
        self.assertEqual(stdout, f'Manifest is valid.{os.linesep}')
        self.assertEqual(stderr, '')
    
    def test_invalid_FileNotFound(self):
        stdout, stderr = self.get_outputs('not_found')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, f'File not found: {str(Config.manifestsRootDir.joinpath("manifest_not_found.xml"))}{os.linesep}')
    
    def test_invalid_InvalidXML(self):
        stdout, stderr = self.get_outputs('invalid_invalid_xml')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, f'Manifest is not a valid XML document!{os.linesep}')
    
    def test_invalid_invalid_syntax(self):
        stdout, stderr = self.get_outputs('invalid_invalid_syntax')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Syntactical valid usage violation detected at line 2: DICT_INVALID_CHILD_TAG

Description of valid usage:

    All child elements of a `dict` must be `named-field`s.
""")
    
    def test_invalid_FailedBaseModelFilterMatch(self):
        stdout, stderr = self.get_outputs('invalid_failed_base_model_filter_match')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Match failure detected when matching the manifest against the base model filter, at line 8 (base model filter), 4 (manifest): DICT_MISSING_KEY

Description of match failure:

    The element being compared is a `dict`, and its keys are not a super set of those of the corresponding `dict` in the filter.
""")
    
    def test_invalid_UnknownTags(self):
        stdout, stderr = self.get_outputs('invalid_unknown_tags')
        
        self.assertEqual(stdout, '')
        self.assertTrue(stderr ==
"""The following tags referenced in the manifest are unknown:

    koala
    koala::kangaroo
""" or
            stderr ==
"""The following tags referenced in the manifest are unknown:

    koala::kangaroo
    koala
""")
        
    def test_invalid_UnmatchedTagNoStack(self):
        stdout, stderr = self.get_outputs('invalid_unmatched_tag_no_stack')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Match failure detected when matching a tag present in the manifest (named "gt1::gt2::gt3") against the manifest.

The match failure named "NUMERIC_FAILED_COMPARISON" occurred at line 4 ("gt1::gt2::gt3"), 4 (manifest).

Description of the match failure "NUMERIC_FAILED_COMPARISON":

    The element being compared is a numeric type (e.g., int, float, etc.), and it does not satisfy the requirement specified in the corresponding filter element.
""")
    
    def test_invalid_UnmatchTag1Stack(self):
        stdout, stderr = self.get_outputs('invalid_unmatched_tag_1_stack')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Match failure detected when matching a tag present in the manifest (named "data-large") against the manifest.

The match failure named "NUMERIC_FAILED_COMPARISON" occurred at line 4 ("gt1::gt2::gt3"), 4 (manifest).

The tag named "gt1::gt2::gt3" was being matched because the following tag-inclusion relationship exists ("<a> -> <b>" means "tag <a> includes tag <b>"):

    (manifest) -> data-large -> gt1::gt2::gt3

Description of the match failure "NUMERIC_FAILED_COMPARISON":

    The element being compared is a numeric type (e.g., int, float, etc.), and it does not satisfy the requirement specified in the corresponding filter element.
""")
    
    def test_invalid_UnmatchTag2Stack(self):
        stdout, stderr = self.get_outputs('invalid_unmatched_tag_2_stack')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Match failure detected when matching a tag present in the manifest (named "large") against the manifest.

The match failure named "NUMERIC_FAILED_COMPARISON" occurred at line 4 ("gt1::gt2::gt3"), 4 (manifest).

The tag named "gt1::gt2::gt3" was being matched because the following tag-inclusion relationship exists ("<a> -> <b>" means "tag <a> includes tag <b>"):

    (manifest) -> large -> data-large -> gt1::gt2::gt3

Description of the match failure "NUMERIC_FAILED_COMPARISON":

    The element being compared is a numeric type (e.g., int, float, etc.), and it does not satisfy the requirement specified in the corresponding filter element.
""")


class TestValidateFilter(unittest.TestCase):
    
    @staticmethod
    def get_outputs(filter_name: str) -> Tuple[str, str]:
        result = sp.run([
            'python',
            str(Config.mainPyExecutable),
            'validate-filter',
            str(Config.filterCasesRootDir.joinpath(f'filter_{filter_name}.xml'))
        ], capture_output=True)

        return result.stdout.decode(), result.stderr.decode()
    
    def test_valid(self):
        stdout, stderr = self.get_outputs('valid')
        
        self.assertEqual(stdout, f'Filter is valid.{os.linesep}')
        self.assertEqual(stderr, '')
    
    def test_invalid_FileNotFound(self):
        stdout, stderr = self.get_outputs('unknown')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, f'File not found: {str(Config.filterCasesRootDir.joinpath("filter_unknown.xml"))}{os.linesep}')
    
    def test_invalid_InvalidXML(self):
        stdout, stderr = self.get_outputs('invalid_invalid_xml')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, f'Filter is not a valid XML document!{os.linesep}')
    
    def test_invalid_invalid_syntax(self):
        stdout, stderr = self.get_outputs('invalid_invalid_syntax')
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""Syntactical valid usage violation detected at line 10: INVALID_TAG

Description of valid usage:

    Tags used in filter XML must be valid, e.g., dict, list, etc.
""")
    
    def test_UnknownTags_OrdinaryFilter_Failure(self):
        stdout, stderr = self.get_outputs('unknown_tag_explicit_test_new')
        
        self.assertEqual(stdout, '')
        self.assertTrue(stderr ==
"""The following tags present in the filter are unknown:

    test
    new
""" or
            stderr ==
"""The following tags present in the filter are unknown:

    new
    test
""")
        
    def test_UnknownTags_TagFilter_Success(self):
        result = sp.run([
            'python',
            str(Config.mainPyExecutable),
            'validate-filter',
            '--tag_name',
            'test',
            str(Config.filterCasesRootDir.joinpath(f'filter_unknown_tag_explicit_test.xml'))
        ], capture_output=True)

        stdout, stderr = result.stdout.decode(), result.stderr.decode()
        
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, f'Filter is valid.{os.linesep}')
    
    def test_UnknownTags_TagFilter_Failure(self):
        result = sp.run([
            'python',
            str(Config.mainPyExecutable),
            'validate-filter',
            '--tag_name',
            'test',
            str(Config.filterCasesRootDir.joinpath(f'filter_unknown_tag_explicit_test_new.xml'))
        ], capture_output=True)

        stdout, stderr = result.stdout.decode(), result.stderr.decode()
        
        self.assertEqual(stdout, '')
        self.assertEqual(stderr,
"""The following tags present in the filter are unknown:

    new
""")


if __name__ == '__main__':
    unittest.main()
