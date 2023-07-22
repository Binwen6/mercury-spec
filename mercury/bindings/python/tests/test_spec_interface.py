import unittest
from typing import Any, Set

import os
import sys

sys.path.append('..')

from src.mercury_nn.specification.interface import (
    filterXMLfromArgs, FilterMatchFailureType, FilterSyntaxInvalidityType, ManifestSyntaxInvalidityType
)
from src.mercury_nn.specification.load_filter_match_failure_specs import loadFilterMatchFailureSpecs
from src.mercury_nn.specification.load_valid_usages import loadValidUsage
from src.mercury_nn.config import Config


class TestSpecificationConsistency(unittest.TestCase):
    @staticmethod
    def _get_attributes(cls: type) -> Set[Any]:
        return {getattr(cls, key) for key in dir(cls) if not (key.startswith('__') and key.endswith('__'))}

    def test_MatchFailuresConsistency(self):
        failure_specs = loadFilterMatchFailureSpecs(Config.filterMatchFailureSpecsFile)
        self.assertEqual({value.name for value in failure_specs.values()},
                         self._get_attributes(FilterMatchFailureType))

    def test_FilterValidUsageConsistency(self):
        valid_usages = loadValidUsage(Config.filterSyntaxValidUsageFile)
        self.assertEqual({value.name for value in valid_usages.values()},
                         self._get_attributes(FilterSyntaxInvalidityType))
    
    def test_ManifestValidUsageConsistency(self):
        valid_usages = loadValidUsage(Config.manifestSyntaxValidUsageFile)
        self.assertEqual({value.name for value in valid_usages.values()},
                         self._get_attributes(ManifestSyntaxInvalidityType))


class TestFilterXMLfromArgs(unittest.TestCase):
    
    def test_modelClass(self):
        expected_string = """
<dict filter="all">
    <named-field name="header">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"/>
            </named-field>
            <named-field name="class">
                <string filter="equals">chat-completion</string>
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
    <named-field name="capabilities">
        <dict filter="none"/>
    </named-field>
    <named-field name="callSpecs">
        <dict filter="all">
            <named-field name="callScheme">
                <string filter="none"/>
            </named-field>
            <named-field name="input">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="output">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="properties">
        <dict filter="none"/>
    </named-field>
</dict>
"""

        self.assertEqual(filterXMLfromArgs(modelType='chat-completion'), expected_string)

    def test_callScheme(self):
        expected_string = """
<dict filter="all">
    <named-field name="header">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"/>
            </named-field>
            <named-field name="class">
                <string filter="none"/>
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
    <named-field name="capabilities">
        <dict filter="none"/>
    </named-field>
    <named-field name="callSpecs">
        <dict filter="all">
            <named-field name="callScheme">
                <string filter="equals">image-classification</string>
            </named-field>
            <named-field name="input">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="output">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="properties">
        <dict filter="none"/>
    </named-field>
</dict>
"""

        self.assertEqual(filterXMLfromArgs(callScheme='image-classification'), expected_string)

    def test_capabilities(self):
        expected_string = f"""
<dict filter="all">
    <named-field name="header">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"/>
            </named-field>
            <named-field name="class">
                <string filter="none"/>
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
    <named-field name="capabilities">
        <dict filter="all"><named-field name="question-answering"><string filter="none"/></named-field><named-field name="math"><string filter="none"/></named-field></dict>
    </named-field>
    <named-field name="callSpecs">
        <dict filter="all">
            <named-field name="callScheme">
                <string filter="none"/>
            </named-field>
            <named-field name="input">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="output">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="properties">
        <dict filter="none"/>
    </named-field>
</dict>
"""
        
        self.assertEqual(filterXMLfromArgs(capabilities=('question-answering', 'math')), expected_string)

    def test_all_combined(self):
        expected_string = f"""
<dict filter="all">
    <named-field name="header">
        <dict filter="all">
            <named-field name="name">
                <string filter="none"/>
            </named-field>
            <named-field name="class">
                <string filter="equals">chat-completion</string>
            </named-field>
            <named-field name="description">
                <string filter="none"/>
            </named-field>
        </dict>
    </named-field>
    <named-field name="capabilities">
        <dict filter="all"><named-field name="question-answering"><string filter="none"/></named-field><named-field name="math"><string filter="none"/></named-field></dict>
    </named-field>
    <named-field name="callSpecs">
        <dict filter="all">
            <named-field name="callScheme">
                <string filter="equals">image-classification</string>
            </named-field>
            <named-field name="input">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="output">
                <dict filter="all">
                    <named-field name="type">
                        <type-declaration filter="none"/>
                    </named-field>
                    <named-field name="description">
                        <string filter="none"/>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="properties">
        <dict filter="none"/>
    </named-field>
</dict>
"""
        
        self.assertEqual(filterXMLfromArgs(modelType='chat-completion', callScheme='image-classification', capabilities=('question-answering', 'math')), expected_string)


if __name__ == '__main__':
    unittest.main()