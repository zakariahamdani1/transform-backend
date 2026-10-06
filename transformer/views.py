from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .transformer_api import transform_file

@api_view(['POST'])
def test_api(request):
    uploaded_file = request.FILES['file']
    mapping = json.loads(request.POST['mapping'])

    force = request.POST.get('force') == 'true'
    result = transform_file(uploaded_file, mapping, force)

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
