from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BusinessContactSerializer


@api_view(["POST"])
def business_contact(request):
    serializer = BusinessContactSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Thank you for contacting us. We will reach out soon."
        }, status=status.HTTP_201_CREATED)

    return Response({
        "success": False,
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
