#!/usr/bin/env python3

import sys
import argparse
import toml
import re

class Converter:
    def __init__(self):
        self.constants = {}

    def convert_value(self, value, indent_level=0):
        indent = '    ' * indent_level
        if isinstance(value, dict):
            items = []
            for k, v in value.items():
                if not re.match(r'^[_a-z]+$', k):
                    raise ValueError(f'Invalid name: {k}')
                converted_value = self.convert_value(v, indent_level + 1)
                items.append(f'{indent}    {k} = {converted_value}')
            return 'dict(\n' + ',\n'.join(items) + f'\n{indent})'
        elif isinstance(value, list):
            items = [self.convert_value(v, indent_level) for v in value]
            return '[ ' + ' '.join(items) + ' ]'
        elif isinstance(value, str):
            # Check for constant declarations and evaluations
            const_decl_match = re.match(r'(.+)\s*->\s*([_a-z]+)$', value)
            const_eval_match = re.match(r'\|([_a-z]+)\|$', value)
            if const_decl_match:
                val_str, name = const_decl_match.groups()
                val_str = val_str.strip()
                # Process the constant value
                const_value = self.convert_constant_value(val_str, indent_level)
                # Store the constant
                self.constants[name] = const_value
                return f'{const_value} -> {name}'
            elif const_eval_match:
                name = const_eval_match.group(1)
                if name in self.constants:
                    return f'|{name}|'
                else:
                    raise ValueError(f'Undefined constant: {name}')
            else:
                return f'@"{value}"'
        elif isinstance(value, bool):
            return f'@"{value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            raise ValueError(f'Unsupported value type: {type(value)}')

    def convert_constant_value(self, val_str, indent_level):
        # Try to convert to int
        try:
            num_value = int(val_str)
            return str(num_value)
        except ValueError:
            pass
        # Try to convert to float
        try:
            num_value = float(val_str)
            return str(num_value)
        except ValueError:
            pass
        # If not a number, process as a string or other value
        return self.convert_value(val_str, indent_level)

def parse_args():
    parser = argparse.ArgumentParser(description='Convert TOML to the learning configuration language.')
    parser.add_argument('-o', '--output', required=True, help='Path to the output file')
    return parser.parse_args()

def read_toml_input():
    try:
        toml_input = sys.stdin.read()
        data = toml.loads(toml_input)
        return data
    except toml.TomlDecodeError as e:
        print(f'Syntax error in TOML input: {e}')
        sys.exit(1)

def main():
    args = parse_args()
    data = read_toml_input()
    converter = Converter()
    try:
        output = converter.convert_value(data)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)

    try:
        with open(args.output, 'w') as f:
            f.write(output)
    except IOError as e:
        print(f'Error writing to output file: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
