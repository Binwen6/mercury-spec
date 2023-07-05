import unittest
import xml.etree.ElementTree as ET

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from ..src.filter import match_filter, FilterMatchResult
from src.filtering import matchFilter, FilterMatchResult, Filter


class TestFilterMatch(unittest.TestCase):

    def test_successful_match(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.SUCCESS)

    def test_base_model_match(self):
        self.assertEqual(matchFilter(
            filterObject=Filter.fromXML(ET.parse('data/base_model.xml').getroot()),
            dataElement=ET.parse('data/alexnet_manifest.xml').getroot()[0][0]
        ), FilterMatchResult.SUCCESS)

    def test_missing_key(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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
        data = """<?xml version="1.0" encoding="UTF-8"?>
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

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.FAILURE)

    def test_missing_item(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.FAILURE)

    def test_incorrect_type(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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
        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.FAILURE)

    def test_not_all_match_dict(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="kangaroo">
        <string filter="none"/>
    </named-field>
</dict>
"""
        data = """<?xml version="1.0" encoding="UTF-8"?>
<dict>
    <named-field name="koala">
        <string>koalas are so cute</string>
    </named-field>

    <named-field name="kangaroo">
        <time>kangaroo</time>
    </named-field>
</dict>
"""

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.FAILURE)

    def test_not_all_match_list(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.FAILURE)
    
    def test_match_string_equal(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>koala</string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.SUCCESS)

    def test_match_string_not_equal(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>koalaa</string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)
        
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>koal</string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)
        
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>koale</string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)
        
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>koala   </string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)
        
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string filter="equals">koala</string>
        """

        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <string>
            koala
        </string>
        """

        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)

    def test_empty_string_equal(self):
        pass


if __name__ == '__main__':
    unittest.main()
