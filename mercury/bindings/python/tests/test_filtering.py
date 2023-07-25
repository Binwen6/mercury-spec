import unittest
from lxml import etree as ET

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path

# from ..src.filter import match_filter, FilterMatchResult
from src.mercury_nn.filtering import matchFilter, FilterMatchResult, Filter, InvalidTagException
from src.mercury_nn.exceptions import InvalidFilterOperationTypeException

from src.mercury_nn.specification.interface import FilterMatchFailureType
from src.mercury_nn.config import Config


# convenient classes
_FailureInfo = FilterMatchResult.FailureInfo
_FailureTypes = FilterMatchFailureType
_FailurePosition = FilterMatchResult.FailureInfo.FailurePosition


class TestFilterMatchResult(unittest.TestCase):
    
    def test_failure_position(self):
        a = _FailurePosition(1, 2, tagStack=[])
        b = _FailurePosition(2, 1, tagStack=[])

        self.assertNotEqual(a, b)

        a = _FailurePosition(1, 2, tagStack=[])
        b = _FailurePosition(1, 2, tagStack=[])

        self.assertEqual(a, b)

        a = _FailurePosition(1, 2, tagStack=[])
        b = _FailurePosition(1, 1, tagStack=[])

        self.assertNotEqual(a, b)
        
        a = _FailurePosition(1, 2, tagStack=[])
        b = _FailurePosition(2, 2, tagStack=[])

        self.assertNotEqual(a, b)
        
        a = _FailurePosition(2, 2, tagStack=[])
        b = _FailurePosition(2, 2, tagStack=['test'])

        self.assertNotEqual(a, b)
    
    def test_failure_info(self):
        a = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[]),
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[]),
        )

        self.assertEqual(a, b)

        a = _FailureInfo(
            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
            failurePosition=_FailurePosition(1, 2, tagStack=[]),
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[]),
        )

        self.assertNotEqual(a, b)
        
        a = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[]),
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=[]),
        )

        self.assertNotEqual(a, b)

        a = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=[]),
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=['test']),
        )

        self.assertNotEqual(a, b)
    
    def test_filter_match_result(self):
        a = FilterMatchResult.success()
        b = FilterMatchResult.success()
        self.assertEqual(a, b)

        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )

        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )
        
        self.assertEqual(a, b)

        a = FilterMatchResult.success()
        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )
        
        self.assertNotEqual(a, b)

        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )
        
        b = FilterMatchResult.failure(
            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )
        
        self.assertNotEqual(a, b)
        
        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2, tagStack=[])
        )

        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=[])
        )
        
        self.assertNotEqual(a, b)
        
        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=[])
        )

        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1, tagStack=['test'])
        )
        
        self.assertNotEqual(a, b)


class TestFilterMatch(unittest.TestCase):

    def test_successful_match(self):
        filterElement = """
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="cute">
        <list filter="all">
            <string filter="none"/>
            <bool filter="none"/>
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
            """
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
            <bool>false</bool>
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection), FilterMatchResult.success())

    def test_base_model_match(self):
        with open(str(Config.baseModelFilterPath), 'r') as f:
            filterElement = ET.parse(f).getroot()

        result = matchFilter(
            filterObject=Filter.fromXMLElement(filterElement),
            dataElement=ET.parse(Config.modelCollectionRootPath.joinpath(Path('openai/chatgpt/manifest.xml'))).getroot(),
            loadedTags=None
        )
        
        self.assertEqual(result, FilterMatchResult.success())

    def test_missing_key(self):
        filterElement = """
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
        data = """
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.DICT_MISSING_KEY,
                             failurePosition=_FailurePosition(2, 2, tagStack=[])
                         ))

    def test_missing_item(self):
        filterElement = """
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
            """
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
                             failurePosition=_FailurePosition(8, 4, tagStack=[]))
                         )

    def test_incorrect_type(self):
        filterElement = """
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
</dict>
"""
        data = \
            """
<dict>
    <named-field name="koala">
        <time>koalas are so cute</time>
    </named-field>
</dict>
"""
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(4, 4, tagStack=[])
                         ))

    def test_not_all_match_dict(self):
        filterElement = """
<dict filter="all">
    <named-field name="koala">
        <string filter="none"/>
    </named-field>
    
    <named-field name="kangaroo">
        <string filter="none"/>
    </named-field>
</dict>
"""
        data = """
<dict>
    <named-field name="kangaroo">
        <time>kangaroo</time>
    </named-field>
    
    <named-field name="koala">
        <string>koalas are so cute</string>
    </named-field>
</dict>
"""

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(8, 4, tagStack=[])
                         ))

    def test_not_all_match_list(self):
        filterElement = """
<list filter="all">
    <string filter="none"/>
    <string filter="none"/>
</list>
"""
        data = """
<list>
    <string>koalas are so cute</string>
    <time>kangaroo</time>
</list>
"""

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(4, 4, tagStack=[])
                         ))
    
    def test_match_string_equal(self):
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koala</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())
    
    def test_float_comparisons(self):
        filterElement = """
        <float filter="equals">1.0</float>
        """

        dataElement = """
        <float>1.0</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <float filter="equals">1.0</float>
        """

        dataElement = """
        <float>1.1</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))

        filterElement = """
        <float filter="gt">1.0</float>
        """

        dataElement = """
        <float>1.1</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <float filter="gt">1.0</float>
        """

        dataElement = """
        <float>1.0</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <float filter="ge">1.0</float>
        """

        dataElement = """
        <float>1.0</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <float filter="ge">1.0</float>
        """

        dataElement = """
        <float>0.9</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <float filter="lt">1.0</float>
        """

        dataElement = """
        <float>0.9</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <float filter="lt">1.0</float>
        """

        dataElement = """
        <float>1.0</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <float filter="le">1.0</float>
        """

        dataElement = """
        <float>1.0</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <float filter="le">1.0</float>
        """

        dataElement = """
        <float>1.1</float>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
    def test_int_comparisons(self):
        filterElement = """
        <int filter="equals">1</int>
        """

        dataElement = """
        <int>1</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <int filter="equals">1</int>
        """

        dataElement = """
        <int>2</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))

        filterElement = """
        <int filter="gt">1</int>
        """

        dataElement = """
        <int>2</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <int filter="gt">1</int>
        """

        dataElement = """
        <int>1</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <int filter="ge">1</int>
        """

        dataElement = """
        <int>1</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <int filter="ge">1</int>
        """

        dataElement = """
        <int>0</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <int filter="lt">1</int>
        """

        dataElement = """
        <int>0</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <int filter="lt">1</int>
        """

        dataElement = """
        <int>1</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
        
        filterElement = """
        <int filter="le">1</int>
        """

        dataElement = """
        <int>1</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

        filterElement = """
        <int filter="le">1</int>
        """

        dataElement = """
        <int>2</int>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))


    def test_match_string_not_equal(self):
        # convenient objects
        failure = FilterMatchResult.failure(
            failureType=_FailureTypes.STRING_VALUE_NOT_EQUAL,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        )
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koalaa</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koal</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koale</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koala   </string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>
            koala
        </string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), failure)

    def test_type_Match(self):
        
        filterElement = """
        <type-declaration filter="type-match">
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """
        <type-declaration>
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())
    
    def test_type_NoMatch(self):
        filterElement = """
        <type-declaration filter="type-match">
            <type-tuple filter="all">
                <type-string/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """
        <type-declaration>
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT,
                             failurePosition=_FailurePosition(3, 3, tagStack=[])
                         ))
    
    def test_type_MatchNone(self):
        filterElement = """
        <type-declaration filter="none">
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """
        <type-declaration>
            <type-tuple>
                <type-string/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())
    
    def test_TypeAndOther_Match(self):
        filterElement = """
        <dict filter="all">
        
            <named-field name="type">
                <type-declaration filter="type-match">
                    <type-tuple filter="all">
                        <type-string/>
                        <type-bool/>
                    </type-tuple>
                </type-declaration>
            </named-field>

            <named-field name="name">
                <string filter="none"/>
            </named-field>
            
        </dict>
        """
        
        dataElement = """
        <dict filter="all">
        
            <named-field name="name">
                <string>koala</string>
            </named-field>

            <named-field name="type">
                <type-declaration>
                    <type-tuple>
                        <type-string/>
                        <type-bool/>
                    </type-tuple>
                </type-declaration>
            </named-field>
            
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement), self.tag_collection), FilterMatchResult.success())

    # Test type declarations
    def test_list_AllFilter_AllMatch_ReturnsSuccess(self):
        # Test scenario for 'type-list' tag with 'all' filter operation type and all elements matching
        filter_xml = """
            <type-list filter="all">
                <type-string/>
            </type-list>
        """
        data_xml = """
            <type-list>
                <type-string/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_list_AllFilter_OneMismatch_ReturnsFailure(self):
        # Test scenario for 'type-list' tag with 'all' filter operation type and one element mismatch
        filter_xml = """
            <type-list filter="all">
                <type-string/>
            </type-list>
        """
        data_xml = """
            <type-list>
                <type-bool/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(3, 3, tagStack=[])
        ))

    def test_list_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-list' tag with 'none' filter operation type
        filter_xml = """
            <type-list filter="none">
                <type-string/>
            </type-list>
        """
        data_xml = """
            <type-list>
                <type-int/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_list_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-list' tag with invalid filter operation type
        filter_xml = """
            <type-list filter="invalid">
                <type-bool/>
            </type-list>
        """
        data_xml = """
            <type-list>
                <type-bool/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidFilterOperationTypeException):
            matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)

    def test_tuple_AllFilter_AllMatch_ReturnsSuccess(self):
        # Test scenario for 'type-tuple' tag with 'all' filter operation type and all elements matching
        filter_xml = """
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tuple_AllFilter_OneMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tuple' tag with 'all' filter operation type and one element mismatch
        filter_xml = """
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """
            <type-tuple>
                <type-string/>
                <type-int/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(4, 4, tagStack=[])
        ))
    
    def test_tuple_AllFilter_WrongOrder_ReturnsFailure(self):
        # Test scenario for 'type-tuple' tag with 'all' filter operation type and one element mismatch
        filter_xml = """
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """
            <type-tuple>
                <type-bool/>
                <type-string/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(3, 3, tagStack=[])
        ))

    def test_tuple_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-tuple' tag with 'none' filter operation type
        filter_xml = """
            <type-tuple filter="none">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """
            <type-tuple>
                <type-string/>
                <type-int/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tuple_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-tuple' tag with invalid filter operation type
        filter_xml = """
            <type-tuple filter="invalid">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidFilterOperationTypeException):
            matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)

    def test_string_ReturnsSuccess(self):
        # Test scenario for 'type-string' tag
        filter_xml = """
        <type-string/>
        """
        
        data_xml = """
        <type-string/>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_bool_ReturnsSuccess(self):
        # Test scenario for 'type-bool' tag
        filter_xml = """
        <type-bool/>
        """
        
        data_xml = """
        <type-bool/>
        """

        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tensor_NdimEquals_NDimMatch_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'ndim-equals' filter operation type and all dimensions matching
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="none"/>
                <dim filter="none"/>
                <dim filter="none"/>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>5</dim>
                <dim>6</dim>
                <dim>7</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tensor_NdimEquals_OneDimMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'ndim-equals' filter operation type and one dimension mismatch
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="none"/>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))

    def test_tensor_ShapeEquals_AllDimsMatch_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and all dimensions matching
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tensor_ShapeEquals_OneDimMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>5</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
            failurePosition=_FailurePosition(5, 5, tagStack=[])
        ))
    
    def test_tensor_ShapeEquals_WrongOrder_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>4</dim>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
            failurePosition=_FailurePosition(4, 4, tagStack=[])
        ))
    
    def test_tensor_ShapeEquals_WrongDimNumber_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))

    def test_tensor_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'none' filter operation type
        filter_xml = """
            <type-tensor filter="none"/>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_tensor_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-tensor' tag with invalid filter operation type
        filter_xml = """
            <type-tensor filter="shape-equals"/>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidFilterOperationTypeException):
            matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
     
    def test_tensor_MixedRequirementsAllMatch_ReturnSuccess(self):
        # Test scenario for 'type-tensor' tag with invalid filter operation type
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="lt">3</dim>
                <dim filter="le">5</dim>
                <dim filter="gt">7</dim>
                <dim filter="ge">9</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>2</dim>
                <dim>2</dim>
                <dim>5</dim>
                <dim>8</dim>
                <dim>9</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
    
    def test_tensor_FailedDimRequirementMatches(self):
        filter_xml = """
            <type-tensor filter="all">
                <dim filter="lt">3</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3, tagStack=[])
                         ))

        filter_xml = """
            <type-tensor filter="all">
                <dim filter="le">5</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>6</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3, tagStack=[])
                         ))

        filter_xml = """
            <type-tensor filter="all">
                <dim filter="gt">7</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>7</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3, tagStack=[])
                         ))

        filter_xml = """
            <type-tensor filter="all">
                <dim filter="ge">9</dim>
            </type-tensor>
        """
        
        data_xml = """
            <type-tensor>
                <dim>8</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3, tagStack=[])
                         ))

    def test_namedValueCollection_AllFilter_AllKeysMatch_ReturnsSuccess(self):
        # Test scenario for 'type-named-value-collection' tag with 'all' filter operation type and all keys matching
        filter_xml = """
            <type-named-value-collection filter="all">
                <type-named-value name="key1"><type-string/></type-named-value>
                <type-named-value name="key2"><type-bool/></type-named-value>
            </type-named-value-collection>
        """
        
        data_xml = """
            <type-named-value-collection>
                <type-named-value name="key2"><type-bool/></type-named-value>
                <type-named-value name="key1"><type-string/></type-named-value>
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_namedValueCollection_AllFilter_OneKeyMismatch_ReturnsFailure(self):
        # Test scenario for 'type-named-value-collection' tag with 'all' filter operation type and one key mismatch
        filter_xml = """
            <type-named-value-collection filter="all">
                <type-named-value name="key1"><string/></type-named-value>
                <type-named-value name="key2"><string/></type-named-value>
            </type-named-value-collection>
        """
        
        data_xml = """
            <type-named-value-collection>
                <type-named-value name="key1"><string/></type-named-value>
                <type-named-value name="key3"><string/></type-named-value>
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))

    def test_namedValueCollection_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-named-value-collection' tag with 'none' filter operation type
        filter_xml = """
            <type-named-value-collection filter="none">
                <type-named-value name="key1"><string/></type-named-value>
                <type-named-value name="key2"><string/></type-named-value>
            </type-named-value-collection>
        """
        
        data_xml = """
            <type-named-value-collection>
                <type-named-value name="key3"><string/></type-named-value>
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
        self.assertEqual(result, FilterMatchResult.success())

    def test_namedValueCollection_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-named-value-collection' tag with invalid filter operation type
        filter_xml = """
            <type-named-value-collection filter="invalid">
                <type-named-value name="key1"><string/></type-named-value>
                <type-named-value name="key2"><string/></type-named-value>
            </type-named-value-collection>
        """
        data_xml = """
            <type-named-value-collection>
                <type-named-value name="key1"><string/></type-named-value>
                <type-named-value name="key2"><string/></type-named-value>
            </type-named-value-collection>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidFilterOperationTypeException):
            matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)

    def test_invalidTag_RaisesException(self):
        # Test scenario for an invalid tag
        filter_xml = """
            <type-invalid/>
        """
        data_xml = """
            <type-invalid/>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidTagException):
            matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection)
    
    # Test logical operations
    
    def test_AND_ReturnsSuccess(self):
        filter_xml = """
            <logical filter="and">
                <string filter="none"/>
                <string filter="equals">koala</string>
            </logical>
        """
        
        data_xml = """
            <string>koala</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
    
    def test_AND_ReturnsFailure(self):
        filter_xml = """
            <logical filter="and">
                <string filter="none"/>
                <string filter="equals">koala</string>
            </logical>
        """
        
        data_xml = """
            <string>koalas</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.STRING_VALUE_NOT_EQUAL,
            failurePosition=_FailurePosition(4, 2, tagStack=[])
        ))
    
    def test_OR_ReturnsSuccess(self):
        filter_xml = """
            <logical filter="or">
                <string filter="equals">koala</string>
                <string filter="equals">foo</string>
            </logical>
        """
        
        data_xml = """
            <string>foo</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
    
    def test_OR_ReturnsFailure(self):
        filter_xml = """
            <logical filter="or">
                <string filter="equals">koala</string>
                <string filter="equals">foo</string>
            </logical>
        """
        
        data_xml = """
            <string>test</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.LOGICAL_OPERATION_MATCH_FAILURE,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
    
    def test_NOT_ReturnsSuccess(self):
        filter_xml = """
            <logical filter="not">
                <string filter="none"/>
            </logical>
        """
        
        data_xml = """
            <int>1</int>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
        
        filter_xml = """
            <logical filter="not">
                <string filter="equals">koala</string>
            </logical>
        """
        
        data_xml = """
            <string>test</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertTrue(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
    
    def test_NOT_ReturnsFailure(self):
        filter_xml = """
            <logical filter="not">
                <string filter="equals">koala</string>
            </logical>
        """
        
        data_xml = """
            <string>koala</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.LOGICAL_OPERATION_MATCH_FAILURE,
            failurePosition=_FailurePosition(2, 2, tagStack=[])
        ))
    
    def test_NestedLogical_ReturnsSuccess(self):
        filter_xml = """
            <logical filter="or">
                <logical filter="and">
                    <string filter="none"/>
                    <string filter="equals">koala</string>
                </logical>
                <logical filter="and">
                    <string filter="none"/>
                    <string filter="equals">foo</string>
                </logical>
            </logical>
        """
        
        data_xml = """
            <string>foo</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.success())
    
    def test_NestedLogical_ReturnsFailure(self):
        filter_xml = """
            <logical filter="and">
                <logical filter="or">
                    <string filter="equals">a</string>
                    <string filter="equals">b</string>
                </logical>
                <logical filter="or">
                    <string filter="equals">c</string>
                    <string filter="equals">d</string>
                </logical>
            </logical>
        """
        
        data_xml = """
            <string>a</string>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(filter_element), data_element, self.tag_collection), FilterMatchResult.failure(
            failureType=_FailureTypes.LOGICAL_OPERATION_MATCH_FAILURE,
            failurePosition=_FailurePosition(7, 2, tagStack=[])
        ))
    
    # Test tags
    def test_TagCollection_ImplicitMatch_ReturnsSuccess(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="data">
                <string filter="equals">koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>string_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <string>koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection), FilterMatchResult.success())
    
    def test_TagCollection_ImplicitMatch_ReturnsFailure_NonTagError(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="data">
                <string filter="equals">koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>string_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <string>kangaroo</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.STRING_VALUE_NOT_EQUAL,
                             failurePosition=_FailurePosition(4, 4, tagStack=[])
                         ))
    
    def test_TagCollection_ImplicitMatch_TagMismatch(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="data">
                <string filter="equals">koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>int_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <string>koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             _FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(4, 4, tagStack=['int_tag'])
                         ))
    
    def test_TagCollection_ExplicitMatch_ReturnsSuccess(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="data">
                <string filter="equals">koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>string_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <string>koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>string_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection), FilterMatchResult.success())

    def test_TagCollection_ExplicitMatch_ReturnsFailure(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="data">
                <string filter="equals">koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>string_tag</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <string>koala</string>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_COLLECTION_EXPLICIT_TAG_MATCH_FAILURE,
                             failurePosition=_FailurePosition(8, 8, tagStack=[])
                         ))
    
    def test_CondensedTags_ExplicitMatch(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>5</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1</condensed-tags>
                    <condensed-tags>gt2</condensed-tags>
                    <condensed-tags>gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_COLLECTION_EXPLICIT_TAG_MATCH_FAILURE,
                             failurePosition=_FailurePosition(4, 8, tagStack=[])
                         ))

        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>5</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1</condensed-tags>
                    <condensed-tags>gt1::gt2</condensed-tags>
                    <condensed-tags>gt1::gt2::gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())

        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>5</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())
        
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="explicit-tag-match">
                    <condensed-tags>gt1.gt2::gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>5</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection>
                    <condensed-tags>gt1</condensed-tags>
                    <condensed-tags>gt1::gt2::gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())
    
    def test_CondensedTags_ImplicitMatch(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>3</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(4, 4, tagStack=['gt1::gt2::gt3'])
                         ))
        
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>gt1::gt2::gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>3</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(4, 4, tagStack=['gt1::gt2::gt3'])
                         ))
        
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>4</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())
        
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>gt1::gt2::gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>4</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())
    
    def test_nested_tags(self):
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>big</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>4</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.success())
        
        filter_xml = """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>big</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """
        
        data_xml = """
        <dict>
            <named-field name="data">
                <int>3</int>
            </named-field>
            
            <named-field name="tags">
                <tag-collection/>
            </named-field>
        </dict>
        """
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filter_xml)), ET.fromstring(data_xml), self.tag_collection),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.NUMERIC_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(4, 4, tagStack=['big', 'gt1::gt2::gt3'])
                         ))
    
    def setUp(self):
        int_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <int filter="none"/>
            </named-field>
        </dict>
        """)
        
        float_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <float filter="none"/>
            </named-field>
        </dict>
        """)

        string_tag = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <string filter="none"/>
            </named-field>
        </dict>
        """)

        tag_gt1 = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">1</int>
            </named-field>
        </dict>
        """)

        tag_gt1_gt2 = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">2</int>
            </named-field>
        </dict>
        """)
        
        tag_gt1_gt2_gt3 = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="data">
                <int filter="gt">3</int>
            </named-field>
        </dict>
        """)
        
        tag_big = ET.fromstring(
        """
        <dict filter="all">
            <named-field name="tags">
                <tag-collection filter="implicit-tag-match">
                    <condensed-tags>gt1.gt2.gt3</condensed-tags>
                </tag-collection>
            </named-field>
        </dict>
        """)
        
        self.tag_collection = {'int_tag': int_tag, 'float_tag': float_tag, 'string_tag': string_tag,
                               'gt1': tag_gt1, 'gt1::gt2': tag_gt1_gt2, 'gt1::gt2::gt3': tag_gt1_gt2_gt3,
                               'big': tag_big}


if __name__ == '__main__':
    unittest.main()
