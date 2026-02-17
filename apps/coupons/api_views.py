from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.coupons.models import Coupon, CouponUsage
from apps.plans.models import Plan

from .serializers import CouponPreviewSerializer, CouponApplySerializer
from .services import validate_coupon



def get_coupon_by_code(code):
    """
    Fetch coupon by slug OR name (case-insensitive)
    """
    return get_object_or_404(
        Coupon,
        Q(slug__iexact=code) | Q(name__iexact=code)
    )


class CouponPreviewAPI(APIView):
    """
    Preview coupon (NO calculation, NO DB write)
    """

    def post(self, request):
        serializer = CouponPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        coupon = get_coupon_by_code(code)

        # ✅ Basic validation only
        valid, message = coupon.is_valid()

        if not valid:
            return Response(
                {"valid": False, "error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "valid": True,
            "coupon": {
                "name": coupon.name,
                "code": coupon.slug,
                "type": coupon.type,
                "discount": coupon.discount,
                "is_use_once_per_customer": coupon.is_use_once_per_customer,
                "has_plan_restriction": coupon.plans.exists(),
                "allowed_plan_ids": list(coupon.plans.values_list("id", flat=True)),

                "has_user_restriction": coupon.users.exists(),
                "allowed_user_ids": list(coupon.users.values_list("id", flat=True)),

                "valid_till": coupon.valid_till,
                "limit": coupon.limit,
                "status": coupon.status
            }
        })


class CouponApplyAPI(APIView):
    """
    Apply coupon (DB WRITE)
    """

    def post(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        amount = serializer.validated_data["amount"]
        order_id = serializer.validated_data["order_id"]
        plan_id = serializer.validated_data.get("plan_id")

        coupon = get_coupon_by_code(code)
        plan = Plan.objects.filter(id=plan_id).first() if plan_id else None

        # ❌ Prevent duplicate order usage
        if CouponUsage.objects.filter(coupon=coupon, order_id=order_id).exists():
            return Response(
                {"error": "Coupon already applied to this order"},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid, message, discount = validate_coupon(
            coupon=coupon,
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            plan=plan
        )

        if not valid:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Save usage
        CouponUsage.objects.create(
            coupon=coupon,
            user=request.user if request.user.is_authenticated else None,
            order_id=order_id
        )

        # ✅ Increment usage count
        coupon.used_count += 1
        coupon.save(update_fields=["used_count"])

        return Response({
            "success": True,
            "coupon": coupon.name,
            "discount": discount,
            "final_amount": max(float(amount) - discount, 0),
            "order_id": order_id
        })
