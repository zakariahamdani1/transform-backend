import re

def validate_stock(value):
            if not value.isdigit():
                return False
            return True

def validate_price(value):
    return bool(re.fullmatch(r'\d+(\.\d+)?', value))

def validate_text(value):
    return bool(value.strip())

def validate_csv_structure(header, row):
    expected_columns = len(header)
    actual_columns = len(row)

    if actual_columns != expected_columns:
        return {
            'expected': expected_columns,
            'actual': actual_columns
        }

    return True