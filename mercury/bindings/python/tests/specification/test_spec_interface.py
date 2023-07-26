import unittest
from typing import Any, Set

import sys

from lxml import etree as ET

from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent.parent))

from src.mercury_nn.specification.interface import (
    filterXMLfromArgs, FilterMatchFailureType, FilterSyntaxInvalidityType, ManifestSyntaxInvalidityType,
    ManifestUtils
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


class TestManifestUtils(unittest.TestCase):
    
    def test_getCondensedTags_and_getTags(self):
        manifest = ET.fromstring("""
<dict>
    <named-field name="specs">
        <dict>
            <named-field name="header">
                <dict>
                    <named-field name="name">
                        <string>ChatGPT-cloud</string>
                    </named-field>
                    <named-field name="class">
                        <string>chat-completion</string>
                    </named-field>
                    <named-field name="description">
                        <string>A chat-completion model.</string>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="capabilities">
                <dict>
                    <named-field name="question-answering"><string/></named-field>
                    <named-field name="world-knowledge"><string/></named-field>
                    <named-field name="question-asking"><string/></named-field>
                    <named-field name="task-breakdown"><string/></named-field>
                    <named-field name="instruction-comprehension"><string/></named-field>
                </dict>
            </named-field>
            <named-field name="callSpecs">
                <dict>
                    <named-field name="callScheme">
                        <string>chat-completion</string>
                    </named-field>
                    <named-field name="input">
                        <dict>
                            <named-field name="type">
                                <type-declaration>
                                    <type-list>
                                        <type-tuple>
                                            <type-string/>
                                            <type-bool/>
                                        </type-tuple>
                                    </type-list>
                                </type-declaration>
                            </named-field>
                            <named-field name="description">
                                <string>An list of chat messages. The first element of the tuple is the content, the second being true if the message is user-sent, false if bot-sent.</string>
                            </named-field>
                        </dict>
                    </named-field>
                    <named-field name="output">
                        <dict>
                            <named-field name="type">
                                <type-declaration>
                                    <type-string/>
                                </type-declaration>
                            </named-field>
                            <named-field name="description">
                                <string>The next bot-sent message.</string>
                            </named-field>
                        </dict>
                    </named-field>
                </dict>
            </named-field>
            <named-field name="tags">
                <tag-collection>
                    <tag>tag1.tag2</tag>
                    <tag>tag3::tag4</tag>
                </tag-collection>
            </named-field>
            <named-field name="properties">
                <dict>
                    <named-field name="deploymentType">
                        <string>cloud</string>
                    </named-field>
                    <named-field name="supportEncryption">
                        <bool>false</bool>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
    <named-field name="implementations">
        <dict>
            <named-field name="Python">
                <dict>
                    <named-field name="entryFile">
                        <string>model.py</string>
                    </named-field>
                    <named-field name="entryClass">
                        <string>Model</string>
                    </named-field>
                </dict>
            </named-field>
        </dict>
    </named-field>
</dict>
""")
        
        self.assertEqual(ManifestUtils.getCondensedTags(manifest), {'tag1.tag2', 'tag3::tag4'})
        self.assertEqual(ManifestUtils.getTags(manifest), {'tag1', 'tag1::tag2', 'tag3::tag4'})


if __name__ == '__main__':
    unittest.main()