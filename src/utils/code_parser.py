# src/utils/code_parser.py
import re

class CodeParser:
    @staticmethod
    def extract_python_code(response: str) -> str | None:
        code_pattern = r"```python(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        return matches[0].strip() if matches else None