import unittest

import os
import sys

sys.path.append('..')

from mercury.interface import filterXMLfromArgs


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
        <list filter="none"/>
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
        <list filter="none"/>
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
        <list filter="all"><string filter="equals">question-answering</string><string filter="equals">math</string></list>
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
        <list filter="all"><string filter="equals">question-answering</string><string filter="equals">math</string></list>
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