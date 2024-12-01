import sys
import argparse
import toml
import re

def parse_args():
    parser = argparse.ArgumentParser(description='Преобразование TOML в учебный конфигурационный язык.')
    parser.add_argument('--output', required=True, help='Путь к выходному файлу.')
    return parser.parse_args()

def is_valid_name(name):
    return re.match(r'^[_a-z]+$', name) is not None

def format_value(value, constants, indent_level=0):
    indent = '    ' * indent_level  # Текущий уровень отступа
    next_indent = '    ' * (indent_level + 1)  # Отступ для вложенных элементов

    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            if not is_valid_name(k):
                raise ValueError(f"Недопустимое имя: {k}")
            formatted_value = format_value(v, constants, indent_level + 1)
            items.append(f"{next_indent}{k} = {formatted_value}")
        items_str = ',\n'.join(items)
        return f"{indent}dict(\n{items_str}\n{indent})"

    elif isinstance(value, list):
        items = [format_value(v, constants, indent_level + 1) for v in value]
        items_str = ' '.join(items)
        return f"{indent}[ {items_str} ]"

    else:
        if isinstance(value, str):
            # Обработка констант в строке
            pattern = r'\|(\w+)\|'
            full_match = re.fullmatch(pattern, value)
            if full_match:
                # Если строка полностью состоит из константы
                const_name = full_match.group(1)
                if const_name in constants:
                    const_value = constants[const_name]
                    # Рекурсивно форматируем значение константы
                    return format_value(const_value, constants, indent_level)
                else:
                    raise ValueError(f"Константа '{const_name}' не объявлена.")
            else:
                # Замена всех вхождений констант в строке
                def replace_constant(match):
                    const_name = match.group(1)
                    if const_name in constants:
                        return str(constants[const_name])
                    else:
                        raise ValueError(f"Константа '{const_name}' не объявлена.")
                value = re.sub(pattern, replace_constant, value)
                return f'@"{value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        else:
            raise TypeError(f"Недопустимый тип значения: {type(value)}")

def main():
    args = parse_args()
    try:
        input_text = sys.stdin.read()
        toml_data = toml.loads(input_text)
    except Exception as e:
        print(f"Ошибка парсинга TOML: {e}", file=sys.stderr)
        sys.exit(1)

    constants = {}
    output_lines = []

    try:
        # Обработка объявлений констант
        if '_constants_' in toml_data:
            consts = toml_data.pop('_constants_')
            for k, v in consts.items():
                if not is_valid_name(k):
                    raise ValueError(f"Недопустимое имя константы: {k}")
                constants[k] = v
                output_lines.append(f"{format_value(v, constants)} -> {k}")

        # Проверяем, остались ли данные после удаления констант
        if toml_data:
            # Обработка основного содержимого
            formatted_output = format_value(toml_data, constants)
            output_lines.append(formatted_output)
        else:
            print("Нет данных для обработки после удаления _constants_.", file=sys.stderr)

        # Запись в файл
        with open(args.output, 'w', encoding='utf-8') as f:
            for line in output_lines:
                f.write(line + '\n')

        print(f"Конфигурация успешно сохранена в {args.output}")

    except Exception as e:
        print(f"Ошибка преобразования: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3

import sys
import argparse
import toml
import re

class Конвертер:
    def __init__(self):
        self.constants = {}

    def преобразовать_значение(self, значение):
        if isinstance(значение, dict):
            элементы = []
            for ключ, знач in значение.items():
                if not re.match(r'^[_a-z]+$', ключ):
                    raise ValueError(f'Недопустимое имя: {ключ}')
                элементы.append(f'    {ключ} = {self.преобразовать_значение(знач)}')
            return 'dict(\n' + ',\n'.join(элементы) + '\n)'
        elif isinstance(значение, list):
            элементы = [self.преобразовать_значение(знач) for знач in значение]
            return '[ ' + ' '.join(элементы) + ' ]'
        elif isinstance(значение, str):
            # Проверка объявления и вычисления констант
            объявление_константы = re.match(r'(.+)\s*->\s*([_a-z]+)$', значение)
            вычисление_константы = re.match(r'\|([_a-z]+)\|$', значение)
            if объявление_константы:
                строка_значения, имя = объявление_константы.groups()
                значение_константы = self.преобразовать_значение(строка_значения.strip())
                self.constants[имя] = значение_константы
                return f'{значение_константы} -> {имя}'
            elif вычисление_константы:
                имя = вычисление_константы.group(1)
                if имя in self.constants:
                    return f'|{имя}|'
                else:
                    raise ValueError(f'Неопределенная константа: {имя}')
            else:
                return f'@"{значение}"'
        elif isinstance(значение, (int, float)):
            return str(значение)
        else:
            raise ValueError(f'Неподдерживаемый тип значения: {type(значение)}')

def разобрать_аргументы():
    parser = argparse.ArgumentParser(description='Конвертирует TOML в учебный конфигурационный язык.')
    parser.add_argument('-o', '--output', required=True, help='Путь к выходному файлу')
    return parser.parse_args()

def прочитать_toml_ввод():
    try:
        toml_input = sys.stdin.read()
        данные = toml.loads(toml_input)
        return данные
    except toml.TomlDecodeError as e:
        print(f'Синтаксическая ошибка во входных данных TOML: {e}')
        sys.exit(1)

def main():
    args = разобрать_аргументы()
    данные = прочитать_toml_ввод()
    конвертер = Конвертер()
    try:
        output = конвертер.преобразовать_значение(данные)
    except ValueError as e:
        print(f'Ошибка: {e}')
        sys.exit(1)

    try:
        with open(args.output, 'w') as f:
            f.write(output)
    except IOError as e:
        print(f'Ошибка при записи в выходной файл: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
