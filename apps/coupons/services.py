from django.utils import timezone
from apps.coupons.models import Coupon, CouponUsage


def validate_coupon(coupon, user, amount, vc_plan_ids=None):
    """
    coupon      : Coupon instance
    user        : User instance or None
    amount      : Decimal/float
    vc_plan_ids : list of VcPlanID strings from cart e.g. ["VcPlanID", "VcPlanID1"]
    """

    # 1️⃣ Base coupon validation (status, date, global limit)
    valid, message = coupon.is_valid()
    if not valid:
        return False, message, 0

    # 2️⃣ User restriction — only if specific users are assigned
    if coupon.users.exists():
        if not user:
            return False, "Login required for this coupon", 0
        if not coupon.users.filter(id=user.id).exists():
            return False, "Coupon not valid for this user", 0

    # 3️⃣ Per-user usage limit (replaces simple is_use_once_per_customer for >1 cases)
    if user:
        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon, user=user
        ).count()

        if coupon.per_user_limit is not None:
            # Explicit per-user limit set
            if user_usage_count >= coupon.per_user_limit:
                return False, f"You have reached the usage limit for this coupon", 0
        elif coupon.is_use_once_per_customer:
            # Legacy one-time flag
            if user_usage_count >= 1:
                return False, "Coupon already used by this user", 0

    # 4️⃣ Plan restriction — match VcPlanID strings (vc_plan_id field on Plan)
    if coupon.plans.exists():
        if not vc_plan_ids:
            return False, "Coupon requires a valid plan in your cart", 0

        # Check if ANY cart plan matches ANY allowed plan on the coupon
        matched = coupon.plans.filter(
            vcPlanID__in=vc_plan_ids
        ).exists()

        if not matched:
            return False, "Coupon is not valid for the plans in your cart", 0

    # 5️⃣ Calculate discount
    if coupon.type == Coupon.FLAT:
        discount = float(coupon.discount)
    else:
        discount = (float(coupon.discount) / 100) * float(amount)

    discount = min(discount, float(amount))
    return True, "Coupon valid", round(discount, 2)