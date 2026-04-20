from django.db import models

class AccessibilityIssue(models.Model):

    ISSUE_TYPES = [
        ('Keyboard Navigation', 'Keyboard Navigation'),
        ('Screen Reader', 'Screen Reader'),
        ('Colour / Contrast', 'Colour / Contrast'),
        ('Text / Typography', 'Text / Typography'),
        ('Motion / Animation', 'Motion / Animation'),
        ('Other', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    issue_type = models.CharField(max_length=100, choices=ISSUE_TYPES)
    page_affected = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.issue_type}"