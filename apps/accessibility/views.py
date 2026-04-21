from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings

from .serializers import AccessibilityIssueSerializer


class AccessibilityIssueCreateView(APIView):

    def post(self, request):
        serializer = AccessibilityIssueSerializer(data=request.data)

        if serializer.is_valid():
            report = serializer.save()

            email_sent = False  # default

            # ── TRY SENDING EMAIL ───────────────────────
            try:
                subject = f"New Accessibility Issue: {report.issue_type}"

                message = f"""
New Accessibility Issue Submitted

Name: {report.full_name}
Email: {report.email}
Issue Type: {report.issue_type}
Page Affected: {report.page_affected}

Description:
{report.description}
"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )

                email_sent = True  # ✅ success

            except Exception as e:
                print("Email failed:", str(e))
                email_sent = False  # ❌ failed

            # ── UPDATE EMAIL STATUS ─────────────────────
            report.email_sent = email_sent
            report.save(update_fields=["email_sent"])

            # ── ALWAYS SUCCESS RESPONSE ─────────────────
            return Response({
                "status": True,
                "message": "Accessibility issue submitted successfully",
                "email_sent": email_sent   # optional (frontend can use)
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)