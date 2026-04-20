from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccessibilityIssueSerializer

class AccessibilityIssueCreateView(APIView):

    def post(self, request):
        serializer = AccessibilityIssueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Accessibility issue submitted successfully"
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)