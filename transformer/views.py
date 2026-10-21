from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .transformer_api import transform_file
from .shopify_columns import SHOPIFY_COLUMNS

@api_view(['POST'])
def test_api(request):
    uploaded_file = request.FILES['file']
    mappings = json.loads(request.POST['mappings'])
    selected_columns = json.loads(
        request.POST.get('selected_columns', '[]')
    )
    force = request.POST.get('force') == 'true'

    result = transform_file(
        uploaded_file,
        mappings,
        force,
    )

    if 'structure_errors' in result:
        return Response({
            "structure_errors": result["structure_errors"]
        })

    errors = result['errors']

    if errors and not force:
        return Response({
            "errors": errors,
            "rows": result["rows"],
            "error_csv": result.get("error_csv")
        })

    response = HttpResponse(result["csv_content"], content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transformed.csv"'
    return response


@api_view(['GET'])
def get_shopify_columns(request):
    return Response(SHOPIFY_COLUMNS)
