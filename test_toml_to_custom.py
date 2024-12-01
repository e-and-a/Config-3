import pytest
import subprocess

def test_simple_conversion(tmp_path):
    input_toml = '''
title = "Пример конфигурации"
value = 42
'''
    expected_output = '''dict(
    title = @"Пример конфигурации",
    value = 42
)
'''

    output_file = tmp_path / "output.txt"
    process = subprocess.run(
        ['python', 'toml_to_custom.py', '--output', str(output_file)],
        input=input_toml.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    assert process.returncode == 0, f"Процесс завершился с кодом {process.returncode}. Ошибка: {process.stderr.decode()}"
    output_text = output_file.read_text(encoding='utf-8')
    assert output_text.strip() == expected_output.strip()

def test_constants(tmp_path):
    input_toml = '''
[_constants_]
pi = 3.14
greeting = "Привет"

[config]
message = "|greeting|, мир!"
circle = { radius = 10, area = "|pi|" }
'''
    expected_output = '''3.14 -> pi
@"Привет" -> greeting
dict(
    config = dict(
        message = @"Привет, мир!",
        circle = dict(
            radius = 10,
            area = 3.14
        )
    )
)
'''

    output_file = tmp_path / "output.txt"
    process = subprocess.run(
        ['python', 'toml_to_custom.py', '--output', str(output_file)],
        input=input_toml.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    assert process.returncode == 0, f"Процесс завершился с кодом {process.returncode}. Ошибка: {process.stderr.decode()}"
    output_text = output_file.read_text(encoding='utf-8')
    assert output_text.strip() == expected_output.strip()
