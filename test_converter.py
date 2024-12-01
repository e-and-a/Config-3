import pytest
from converter import Converter

@pytest.fixture
def converter():
    return Converter()

def test_number(converter):
    assert converter.convert_value(42) == '42'

def test_string(converter):
    assert converter.convert_value('hello') == '@"hello"'

def test_array(converter):
    assert converter.convert_value([1, 2, 'three']) == '[ 1 2 @"three" ]'

def test_dict(converter):
    input_dict = {'name': 'test', 'value': 123}
    expected_output = 'dict(\n    name = @"test",\n    value = 123\n)'
    assert converter.convert_value(input_dict) == expected_output

def test_nested_structures(converter):
    input_data = {'config': {'items': [1, 2, 3], 'enabled': True}}
    expected_output = (
        'dict(\n'
        '    config = dict(\n'
        '        items = [ 1 2 3 ],\n'
        '        enabled = @"True"\n'
        '    )\n'
        ')'
    )
    assert converter.convert_value(input_data) == expected_output

def test_constant_declaration(converter):
    result = converter.convert_value('123 -> myconst')
    assert 'myconst' in converter.constants
    assert converter.constants['myconst'] == '123'
    assert result == '123 -> myconst'

def test_constant_evaluation(converter):
    converter.constants['myconst'] = '123'
    result = converter.convert_value('|myconst|')
    assert result == '|myconst|'

def test_invalid_name(converter):
    with pytest.raises(ValueError):
        converter.convert_value({'Invalid-Name': 123})

def test_undefined_constant(converter):
    with pytest.raises(ValueError):
        converter.convert_value('|undefined|')
