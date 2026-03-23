from django.db import models


class BusinessContact(models.Model):
    BUSINESS_NEEDS_CHOICES = [
        ("new_plan", "New Plan"),
        ("plan_upgrade", "Plan Upgrade"),
        ("troubleshooting", "Troubleshooting"),
        ("custom_solution", "Custom Solution"),
        ("other", "Other"),
    ]

    full_name      = models.CharField(max_length=255)
    business_name  = models.CharField(max_length=255)
    business_email = models.EmailField()
    business_needs = models.CharField(max_length=50)
    message        = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Business Contact"
        verbose_name_plural = "Business Contacts"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.business_email}"
