import csv
from io import TextIOWrapper, StringIO

from .validation import (
    validate_stock, 
    validate_price, 
    validate_text,
    validate_csv_structure
    )

shopify_columns = {
    'handle': 'Handle',
    'title': 'Title',
    'vendor': 'Vendor',
    'sku': 'Variant SKU',
    'price': 'Variant Price',
    'stock': 'Variant Inventory Qty'
}

def create_handle(product_name):
    return product_name.lower().replace(" ", "-")

def create_error_csv(errors):
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['Row', 'Field', 'Value'])

    for error in errors:
        writer.writerow([error['row'], error['field'], error['value']])

    return csv_file.getvalue()

def transform_file(input_file, mapping, force=False):
    file = TextIOWrapper(input_file, encoding='utf-8')
    read_csv = csv.reader(file)

    header = next(read_csv)
    errors = []
    shopify_rows = []
    output = []
    rows = list(read_csv)
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    

    

    output.append([
        shopify_columns['handle'],
        shopify_columns['title'],
        shopify_columns['vendor'],
        shopify_columns['sku'],
        shopify_columns['stock'],
        shopify_columns['price']
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

    
    for row_number ,row in enumerate(rows, start=2):
        if mapping['title'] != None:
            product_name = row[mapping['title']]

            if not validate_text(product_name):
                errors.append({
                    'field': 'title',
                    'row': row_number,
                    'value': product_name
                })

                if force:
                    product_name = 'Empty'

            handle = create_handle(product_name)
        else:
            product_name = None
            handle = None

        

        if mapping['sku'] != None:
            product_code = row[mapping['sku']]

            if not validate_text(product_code):
                errors.append({
                    'field': 'sku',
                    'row': row_number,
                    'value': product_code
                })

                if force:
                    product_code = 'Empty'
        else:
            product_code = None

        if mapping['vendor'] != None:
            brand = row[mapping['vendor']]

            if not validate_text(brand):
                errors.append({
                    'field': 'vendor',
                    'row': row_number,
                    'value': brand
                })

                if force:
                    brand = 'Empty'
        else:
            brand = None

        if mapping['price'] != None:
            price = row[mapping['price']]

            if not validate_price(price):
                errors.append({
                    'field': 'price',
                    'row': row_number,
                    'value': price
                })

                if force:
                    price = '0'
        else:
            price = None

        if mapping['stock'] != None:
            stock = row[mapping['stock']]

            if not validate_stock(stock):
                errors.append({
                    'field': 'stock',
                    'row': row_number,
                    'value': stock
                })

                if force:
                    stock = '0'
        else:
            stock = None


        shopify_values = {
            'handle': handle,
            'title': product_name,
            'sku': product_code,
            'stock': stock,
            'vendor': brand,
            'price': price
        }

        shopify_rows.append(shopify_values)

        output.append([
            shopify_values['handle'],
            shopify_values['title'],
            shopify_values['vendor'],
            shopify_values['sku'],
            shopify_values['stock'],
            shopify_values['price']
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