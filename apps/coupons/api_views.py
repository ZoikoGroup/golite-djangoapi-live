from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from apps.coupons.models import Coupon, CouponUsage
from .serializers import CouponPreviewSerializer, CouponApplySerializer
from .services import validate_coupon

User = get_user_model()


def get_coupon_by_code(code):
    return get_object_or_404(
        Coupon,
        Q(slug__iexact=code) | Q(name__iexact=code)
    )


def resolve_user(request, email=None):
    """
    Prefer the authenticated session user.
    Fall back to email lookup (for cases where frontend passes email only).
    """
    if request.user.is_authenticated:
        return request.user
    if email:
        return User.objects.filter(email__iexact=email).first()
    return None


class CouponPreviewAPI(APIView):
    """
    Preview coupon — full validation, NO DB write.
    Accepts: code, logged_user_email, cart_items_id
    """

    def post(self, request):
        serializer = CouponPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        email = serializer.validated_data.get("logged_user_email")
        vc_plan_ids = serializer.get_vc_plan_ids()

        coupon = get_coupon_by_code(code)
        user = resolve_user(request, email)

        # Full validation (including user + plan) — but NO amount, so no discount calc
        # Pass amount=0 just to run through all checks cleanly
        valid, message, _ = validate_coupon(
            coupon=coupon,
            user=user,
            amount=0,
            vc_plan_ids=vc_plan_ids,
        )

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
                "per_user_limit": coupon.per_user_limit,
                "is_use_once_per_customer": coupon.is_use_once_per_customer,
                "has_plan_restriction": coupon.plans.exists(),
                "has_user_restriction": coupon.users.exists(),
                "valid_till": coupon.valid_till,
                "limit": coupon.limit,
                "status": coupon.status,
            }
        })


class CouponApplyAPI(APIView):
    """
    Apply coupon — full validation + DB write.
    """

    def post(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        amount = serializer.validated_data["amount"]
        order_id = serializer.validated_data["order_id"]
        email = serializer.validated_data.get("logged_user_email")
        vc_plan_ids = serializer.get_vc_plan_ids()

        coupon = get_coupon_by_code(code)
        user = resolve_user(request, email)

        # Prevent duplicate order
        if CouponUsage.objects.filter(coupon=coupon, order_id=order_id).exists():
            return Response(
                {"error": "Coupon already applied to this order"},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid, message, discount = validate_coupon(
            coupon=coupon,
            user=user,
            amount=amount,
            vc_plan_ids=vc_plan_ids,
        )

        if not valid:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save usage
        CouponUsage.objects.create(
            coupon=coupon,
            user=user,
            order_id=order_id,
        )

        # Increment global counter atomically
        Coupon.objects.filter(pk=coupon.pk).update(
            used_count=models.F("used_count") + 1
        )

        return Response({
            "success": True,
            "coupon": coupon.name,
            "discount": discount,
            "final_amount": max(float(amount) - discount, 0),
            "order_id": order_id,
        })