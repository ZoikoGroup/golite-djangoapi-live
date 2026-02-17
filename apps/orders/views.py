from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VCareOrderSerializer
from .models import VCareOrder
from collections import defaultdict


# -------------------------
# EXISTING CREATE API
# (UNCHANGED)
# -------------------------
class VCareOrderCreateAPIView(APIView):
    def post(self, request):
        serializer = VCareOrderSerializer(
            data={"raw_data": request.data}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Order saved successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


# -------------------------
# NEW GROUPED ORDERS API
# -------------------------
class VCareUserGroupedOrdersAPIView(APIView):
    """
    POST BODY:
    {
        "logged_user": "sumonklyn@gmail.com"
    }
    """

    def post(self, request):

        logged_user = request.data.get("logged_user")

        if not logged_user:
            return Response({
                "status": False,
                "message": "logged_user is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        orders = VCareOrder.objects.all().order_by("-id")

        grouped_data = defaultdict(lambda: defaultdict(list))

        for order in orders:
            data = order.raw_data   # already dict

            order_block = data.get("order", {})
            customer_list = data.get("customer", {}).get("data", [])

            if order_block.get("logged_user") != logged_user:
                continue

            shipping_email = order_block.get("order_shipping_email")

            for customer in customer_list:
                enrollment_id = customer.get("enrollment_id")

                grouped_data[shipping_email][enrollment_id].append({
                    "order_db_id": order.id,
                    "total": order_block.get("total"),
                    "currency": order_block.get("currency"),
                    "plans": order_block.get("cart"),
                    "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

        return Response({
            "status": True,
            "logged_user": logged_user,
            "groups": grouped_data
        })
