import unittest
import xml.etree.ElementTree as ET

import sys
sys.path.append('..')

# from ..src.filter import match_filter, FilterMatchResult
from src.filter import match_filter, FilterMatchResult

class TestFilterMatch(unittest.TestCase):
    
    def test_successful_match(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="cute">
        <list filter="all">
            <string filter="none"/>
            <time filter="none"/>
        </list>
    </named-field>
    
    <named-field name="l">
        <list filter="none"/>
    </named-field>

    <named-field name="d">
        <dict filter="none"/>
    </named-field>
</dict>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="l">
        <list></list>
    </named-field>
    
    <named-field name="d">
        <dict>
            <named-field name="1">
                <string>koalas are so cute</string>
            </named-field>
        </dict>
    </named-field>

    <named-field name="cute">
        <list>
            <string>koala</string>
            <time>20230702</time>
            <string>cute</string>
        </list>
    </named-field>
    
    <named-field name="koala">
        <string>koalas are so cute</string>
    </named-field>
    
    <named-field name="tmp">
        <string>koala</string>
    </named-field>
</dict>
"""
        
        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.SUCCESS)
    
    def test_base_model_match(self):
        self.assertEqual(match_filter(
            filter=ET.parse('data/base_model.xml').getroot(),
            element=ET.parse('data/alexnet_manifest.xml').getroot()[0][0]
        ), FilterMatchResult.SUCCESS)

    def test_missing_key(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="cute">
        <list filter="all">
            <string filter="none"/>
            <time filter="none"/>
        </list>
    </named-field>
</dict>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="l">
        <list></list>
    </named-field>
    
    <named-field name="d">
        <dict>
            <named-field name="1">
                <string>koalas are so cute</string>
            </named-field>
        </dict>
    </named-field>

    <named-field name="cute">
        <list>
            <string>koala</string>
            <time>20230702</time>
            <string>cute</string>
        </list>
    </named-field>
    
    <named-field name="tmp">
        <string>koala</string>
    </named-field>
</dict>
"""
        
        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.FAILURE)

    def test_missing_item(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="cute">
        <list filter="all">
            <string filter="none"/>
            <time filter="none"/>
        </list>
    </named-field>
</dict>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="cute">
        <list>
            <string>koala</string>
        </list>
    </named-field>
    
    <named-field name="koala">
        <string>koalas are so cute</string>
    </named-field>
    
    <named-field name="tmp">
        <string>koala</string>
    </named-field>
</dict>
"""
        
        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.FAILURE)
    
    def test_incorrect_type(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
</dict>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="koala">
        <time>koalas are so cute</time>
    </named-field>
</dict>
"""
        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.FAILURE)
    
    def test_not_all_match_dict(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="kangaroo">
        <string filter="none"/>
    </named-field>
</dict>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="koala">
        <string>koalas are so cute</string>
    </named-field>

    <named-field name="kangaroo">
        <time>kangaroo</time>
    </named-field>
</dict>
"""

        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.FAILURE)
        
    def test_not_all_match_list(self):
        filter = \
"""<?xml version="1.0" encoding="UTF-8"?>
<list filter="all">
    <string filter="none"/>
    <string filter="none"/>
</list>
"""
        data = \
"""<?xml version="1.0" encoding="UTF-8"?>
<list>
    <string>koalas are so cute</string>
    <time>kangaroo</time>
</list>
"""

        self.assertEqual(match_filter(ET.fromstring(filter), ET.fromstring(data)), FilterMatchResult.FAILURE)

if __name__ == '__main__':
    unittest.main()