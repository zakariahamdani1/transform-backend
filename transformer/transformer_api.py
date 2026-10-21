import csv
from io import TextIOWrapper, StringIO
from .shopify_columns import SHOPIFY_COLUMNS

from .validation import (
    validate_stock, 
    validate_price, 
    validate_text,
    validate_csv_structure
    )

def create_handle(product_name):
    return product_name.lower().replace(" ", "-")

def create_error_csv(errors):
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['Row', 'Field', 'Value'])

    for error in errors:
        writer.writerow([error['row'], error['field'], error['value']])

    return csv_file.getvalue()

def transform_file(input_file, mappings, force=False):
    file = TextIOWrapper(input_file, encoding='utf-8')
    read_csv = csv.reader(file)

    header = next(read_csv)
    errors = []
    shopify_rows = []
    output = []
    rows = list(read_csv)
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    

    

    column_by_key = {
        column["key"]: column
        for column in SHOPIFY_COLUMNS
    }

    active_mappings = []

    for item in mappings:
        shopify_key = item.get("shopifyKey")

        if not shopify_key or shopify_key == "__dont_use":
            continue

        column = column_by_key.get(shopify_key)

        if column is None:
            continue

        if column["type"] in ("generated", "default"):
            if not item.get("enabled", True):
                continue

        elif column["type"] == "source":
            if item.get("sourceIndex") is None:
                continue

        active_mappings.append({
            "mapping": item,
            "column": column
        })

    output_columns = [
        item["column"]
        for item in active_mappings
    ]

    source_mapping = {
        item["column"]["key"]: item["mapping"]["sourceIndex"]
        for item in active_mappings
        if item["column"]["type"] == "source"
    }

    output.append([
        column["label"] for column in output_columns
    ])

    for row_number, row in enumerate(rows, start=2):
        structure_error = validate_csv_structure(header, row)
        if structure_error is not True:
            errors.append({
                'type': 'structure',
                'row': row_number,
                'expected': structure_error['expected'],
                'actual': structure_error['actual']
            })

    if errors:
        return {
            'structure_errors': errors
        }

    
    for row_number, row in enumerate(rows, start=2):
        shopify_values = {}

        for item in active_mappings:
            column = item["column"]
            key = column["key"]
            column_type = column["type"]

            if column_type == "generated":
                if key == "handle":
                    title_index = source_mapping.get("title")

                    if title_index is not None:
                        product_name = row[title_index]
                        shopify_values[key] = create_handle(product_name)
                    else:
                        shopify_values[key] = ""

            elif column_type == "default":
                if key == "option1_name":
                    shopify_values[key] = "Title"
                elif key == "option1_value":
                    shopify_values[key] = "Default Title"

            elif column_type == "source":
                source_index = item["mapping"]["sourceIndex"]
                value = row[source_index]
                shopify_values[key] = value

                if key == "title" and not validate_text(value):
                    errors.append({
                        "field": key,
                        "row": row_number,
                        "value": value
                    })

                elif key == "sku" and not validate_text(value):
                    errors.append({
                        "field": key,
                        "row": row_number,
                        "value": value
                    })

                elif key == "vendor" and not validate_text(value):
                    errors.append({
                        "field": key,
                        "row": row_number,
                        "value": value
                    })

                elif key == "price" and not validate_price(value):
                    errors.append({
                        "field": key,
                        "row": row_number,
                        "value": value
                    })

                elif key == "stock" and not validate_stock(value):
                    errors.append({
                        "field": key,
                        "row": row_number,
                        "value": value
                    })

        shopify_rows.append(shopify_values)

        output.append([
            shopify_values.get(column["key"], "")
            for column in output_columns
        ])

    if errors and not force:
        return {
            'errors': errors,
            'rows': shopify_rows,
            'error_csv': create_error_csv(errors)
        }
    writer.writerows(output)
    csv_content = csv_file.getvalue()

    return {
        'errors': errors,
        'rows': shopify_rows,
        'csv_content': csv_content
    }