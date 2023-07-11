import unittest
from lxml import etree as ET

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from ..src.filter import match_filter, FilterMatchResult
from mercury.filtering import matchFilter, FilterMatchResult, Filter, _matchTypeDeclarationFilter, InvalidTagException
from mercury.exceptions import InvalidFilterOperationTypeException

from mercury.interface import FilterMatchFailureType


# convenient classes
_FailureInfo = FilterMatchResult.FailureInfo
_FailureTypes = FilterMatchFailureType
_FailurePosition = FilterMatchResult.FailureInfo.FailurePosition


class TestFilterMatchResult(unittest.TestCase):
    
    def test_failure_position(self):
        a = _FailurePosition(1, 2)
        b = _FailurePosition(2, 1)

        self.assertNotEqual(a, b)

        a = _FailurePosition(1, 2)
        b = _FailurePosition(1, 2)

        self.assertEqual(a, b)

        a = _FailurePosition(1, 2)
        b = _FailurePosition(1, 1)

        self.assertNotEqual(a, b)
        
        a = _FailurePosition(1, 2)
        b = _FailurePosition(2, 2)

        self.assertNotEqual(a, b)
    
    def test_failure_info(self):
        a = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        self.assertEqual(a, b)

        a = _FailureInfo(
            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
            failurePosition=_FailurePosition(1, 2)
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        self.assertNotEqual(a, b)
        
        a = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        b = _FailureInfo(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1)
        )

        self.assertNotEqual(a, b)
    
    def test_filter_match_result(self):
        a = FilterMatchResult.success()
        b = FilterMatchResult.success()
        self.assertEqual(a, b)

        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )
        
        self.assertEqual(a, b)

        a = FilterMatchResult.success()
        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )
        
        self.assertNotEqual(a, b)

        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )
        
        b = FilterMatchResult.failure(
            failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
            failurePosition=_FailurePosition(1, 2)
        )
        
        self.assertNotEqual(a, b)
        
        a = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 2)
        )

        b = FilterMatchResult.failure(
            failureType=_FailureTypes.DICT_MISSING_KEY,
            failurePosition=_FailurePosition(1, 1)
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)), FilterMatchResult.success())

    def test_base_model_match(self):
        result = matchFilter(
            filterObject=Filter.fromXMLElement(ET.parse('data/base_model.xml').getroot()),
            dataElement=ET.parse('data/alexnet_manifest.xml').getroot()[0][0]
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.DICT_MISSING_KEY,
                             failurePosition=_FailurePosition(2, 2)
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.LIST_INSUFFICIENT_CHILDREN,
                             failurePosition=_FailurePosition(8, 4))
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
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(4, 4)
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(8, 4)
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

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(data)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TAG_MISMATCH,
                             failurePosition=_FailurePosition(4, 4)
                         ))
    
    def test_match_string_equal(self):
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koala</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.success())

    def test_match_string_not_equal(self):
        # convenient objects
        failure = FilterMatchResult.failure(
            failureType=_FailureTypes.STRING_VALUE_NOT_EQUAL,
            failurePosition=_FailurePosition(2, 2)
        )
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koalaa</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koal</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koale</string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>koala   </string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), failure)
        
        filterElement = """
        <string filter="equals">koala</string>
        """

        dataElement = """
        <string>
            koala
        </string>
        """

        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), failure)

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
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.success())
    
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
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_TUPLE_INCORRECT_CHILDREN_COUNT,
                             failurePosition=_FailurePosition(3, 3)
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
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.success())
    
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
        
        self.assertEqual(matchFilter(Filter.fromXMLElement(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.success())


# The following code are authored by ChatGPT and finetuned by Trent Fellbootman.
class TestMatchTypeDeclarationFilter(unittest.TestCase):
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(3, 3)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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
            _matchTypeDeclarationFilter(filter_element, data_element)

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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(4, 4)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TAG_MISMATCH,
            failurePosition=_FailurePosition(3, 3)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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
            _matchTypeDeclarationFilter(filter_element, data_element)

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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
            failurePosition=_FailurePosition(2, 2)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
            failurePosition=_FailurePosition(5, 5)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
            failurePosition=_FailurePosition(4, 4)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_TENSOR_DIFFERENT_DIM_NUMBER,
            failurePosition=_FailurePosition(2, 2)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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
            _matchTypeDeclarationFilter(filter_element, data_element)
     
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

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.success())
    
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

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3)
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

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3)
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

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3)
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

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element),
                         FilterMatchResult.failure(
                             failureType=_FailureTypes.TYPE_DECLARATION_DIM_FAILED_COMPARISON,
                             failurePosition=_FailurePosition(3, 3)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.failure(
            failureType=_FailureTypes.TYPE_DECLARATION_NAMED_VALUE_COLLECTION_DIFFERENT_KEYS,
            failurePosition=_FailurePosition(2, 2)
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

        result = _matchTypeDeclarationFilter(filter_element, data_element)
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
            _matchTypeDeclarationFilter(filter_element, data_element)

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
            _matchTypeDeclarationFilter(filter_element, data_element)


if __name__ == '__main__':
    unittest.main()
