from rest_framework import serializers


class CouponPreviewSerializer(serializers.Serializer):
    code = serializers.CharField()
    logged_user_email = serializers.EmailField(required=False, allow_null=True)
    cart_items_id = serializers.CharField(required=False, allow_blank=True)
    # Parses "VcPlanID, VcPlanID1" → ["VcPlanID", "VcPlanID1"]
    def get_vc_plan_ids(self):
        raw = self.validated_data.get("cart_items_id", "") or ""
        return [p.strip() for p in raw.split(",") if p.strip()]


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.CharField()
    logged_user_email = serializers.EmailField(required=False, allow_null=True)
    cart_items_id = serializers.CharField(required=False, allow_blank=True)

    def get_vc_plan_ids(self):
        raw = self.validated_data.get("cart_items_id", "") or ""
        return [p.strip() for p in raw.split(",") if p.strip()]