import unittest
import xml.etree.ElementTree as ET

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from ..src.filter import match_filter, FilterMatchResult
from src.filtering import matchFilter, FilterMatchResult, Filter, _matchTypeDeclarationFilter, InvalidTagException
from src.exceptions import InvalidFilterOperationTypeException


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

    def test_type_Match(self):
        
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration filter="type-match">
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration>
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.SUCCESS)
    
    def test_type_NoMatch(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration filter="type-match">
            <type-tuple filter="all">
                <type-string/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration>
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.FAILURE)
    
    def test_type_MatchNone(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration filter="none">
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        </type-declaration>
        """
        
        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
        <type-declaration>
            <type-tuple>
                <type-string/>
            </type-tuple>
        </type-declaration>
        """
        
        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.SUCCESS)
    
    def test_TypeAndOther_Match(self):
        filterElement = """<?xml version="1.0" encoding="UTF-8"?>
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
        
        dataElement = """<?xml version="1.0" encoding="UTF-8"?>
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
        
        self.assertEqual(matchFilter(Filter.fromXML(ET.fromstring(filterElement)), ET.fromstring(dataElement)), FilterMatchResult.SUCCESS)


# The following code are authored by ChatGPT and finetuned by Trent Fellbootman.
class TestMatchTypeDeclarationFilter(unittest.TestCase):
    def test_list_AllFilter_AllMatch_ReturnsSuccess(self):
        # Test scenario for 'type-list' tag with 'all' filter operation type and all elements matching
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list filter="all">
                <type-string/>
            </type-list>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list>
                <type-string/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_list_AllFilter_OneMismatch_ReturnsFailure(self):
        # Test scenario for 'type-list' tag with 'all' filter operation type and one element mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list filter="all">
                <type-string/>
            </type-list>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list>
                <type-bool/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)

    def test_list_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-list' tag with 'none' filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list filter="none">
                <type-string/>
            </type-list>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list>
                <type-int/>
            </type-list>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_list_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-list' tag with invalid filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-list filter="invalid">
                <type-bool/>
            </type-list>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple>
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tuple_AllFilter_OneMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tuple' tag with 'all' filter operation type and one element mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple>
                <type-string/>
                <type-int/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)
    
    def test_tuple_AllFilter_WrongOrder_ReturnsFailure(self):
        # Test scenario for 'type-tuple' tag with 'all' filter operation type and one element mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple filter="all">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple>
                <type-bool/>
                <type-string/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)

    def test_tuple_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-tuple' tag with 'none' filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple filter="none">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple>
                <type-string/>
                <type-int/>
            </type-tuple>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tuple_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-tuple' tag with invalid filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tuple filter="invalid">
                <type-string/>
                <type-bool/>
            </type-tuple>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <type-string/>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <type-string/>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_bool_ReturnsSuccess(self):
        # Test scenario for 'type-bool' tag
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <type-bool/>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <type-bool/>
        """

        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tensor_NdimEquals_NDimMatch_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'ndim-equals' filter operation type and all dimensions matching
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="none"/>
                <dim filter="none"/>
                <dim filter="none"/>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>5</dim>
                <dim>6</dim>
                <dim>7</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tensor_NdimEquals_OneDimMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'ndim-equals' filter operation type and one dimension mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="none"/>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)

    def test_tensor_ShapeEquals_AllDimsMatch_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and all dimensions matching
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tensor_ShapeEquals_OneDimMismatch_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>5</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)
    
    def test_tensor_ShapeEquals_WrongOrder_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
                <dim filter="equals">4</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>4</dim>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)
    
    def test_tensor_ShapeEquals_WrongDimNumber_ReturnsFailure(self):
        # Test scenario for 'type-tensor' tag with 'shape-equals' filter operation type and one dimension mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="equals">3</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)

    def test_tensor_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-tensor' tag with 'none' filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="none"/>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>3</dim>
                <dim>4</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_tensor_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-tensor' tag with invalid filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="shape-equals"/>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
     
    def test_tensor_MixedRequirementsSomeMisMatch_ReturnFailure(self):
        # Test scenario for 'type-tensor' tag with invalid filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="equals">2</dim>
                <dim filter="lt">3</dim>
                <dim filter="lt">4</dim>
                <dim filter="le">5</dim>
                <dim filter="le">6</dim>
                <dim filter="gt">7</dim>
                <dim filter="gt">8</dim>
                <dim filter="ge">9</dim>
                <dim filter="ge">10</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>2</dim>
                <dim>2</dim>
                <dim>4</dim>
                <dim>5</dim>
                <dim>7</dim>
                <dim>8</dim>
                <dim>8</dim>
                <dim>9</dim>
                <dim>9</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.FAILURE)
    
    def test_tensor_MixedRequirementsAllMatch_ReturnSuccess(self):
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="lt">3</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>3</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.FAILURE)

        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="le">5</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>6</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.FAILURE)

        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="gt">7</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>7</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.FAILURE)

        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor filter="all">
                <dim filter="ge">9</dim>
            </type-tensor>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-tensor>
                <dim>8</dim>
            </type-tensor>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        self.assertEqual(_matchTypeDeclarationFilter(filter_element, data_element), FilterMatchResult.FAILURE)

    def test_namedValueCollection_AllFilter_AllKeysMatch_ReturnsSuccess(self):
        # Test scenario for 'type-named-value-collection' tag with 'all' filter operation type and all keys matching
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection filter="all">
                <type-named-value name="key1" />
                <type-named-value name="key2" />
            </type-named-value-collection>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection>
                <type-named-value name="key2" />
                <type-named-value name="key1" />
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_namedValueCollection_AllFilter_OneKeyMismatch_ReturnsFailure(self):
        # Test scenario for 'type-named-value-collection' tag with 'all' filter operation type and one key mismatch
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection filter="all">
                <type-named-value name="key1" />
                <type-named-value name="key2" />
            </type-named-value-collection>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection>
                <type-named-value name="key1" />
                <type-named-value name="key3" />
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.FAILURE)

    def test_namedValueCollection_NoneFilter_ReturnsSuccess(self):
        # Test scenario for 'type-named-value-collection' tag with 'none' filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection filter="none">
                <type-named-value name="key1" />
                <type-named-value name="key2" />
            </type-named-value-collection>
        """
        
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection>
                <type-named-value name="key3" />
            </type-named-value-collection>
        """
        
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        result = _matchTypeDeclarationFilter(filter_element, data_element)
        self.assertEqual(result, FilterMatchResult.SUCCESS)

    def test_namedValueCollection_InvalidFilterOpType_RaisesException(self):
        # Test scenario for 'type-named-value-collection' tag with invalid filter operation type
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection filter="invalid">
                <type-named-value name="key1" />
                <type-named-value name="key2" />
            </type-named-value-collection>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-named-value-collection>
                <type-named-value name="key1" />
                <type-named-value name="key2" />
            </type-named-value-collection>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidFilterOperationTypeException):
            _matchTypeDeclarationFilter(filter_element, data_element)

    def test_invalidTag_RaisesException(self):
        # Test scenario for an invalid tag
        filter_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-invalid/>
        """
        data_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <type-invalid/>
        """
        filter_element = ET.fromstring(filter_xml)
        data_element = ET.fromstring(data_xml)

        with self.assertRaises(InvalidTagException):
            _matchTypeDeclarationFilter(filter_element, data_element)


if __name__ == '__main__':
    unittest.main()
