import secrets
import string
from django.db import models
from django.utils import timezone


def generate_secret_key():
    """Generate a cryptographically secure 16-character alphanumeric secret key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(16))


class ESIMCheckerEndpoint(models.Model):
    """
    Registered client sites allowed to call the eSIM checker API.
    Each site gets a unique 16-digit secret key used for request authentication.
    """
    site_url = models.URLField(
        unique=True,
        help_text="Origin URL of the registered site (e.g. https://react.driverxmobile.com)"
    )
    secret_key = models.CharField(
        max_length=16,
        unique=True,
        default=generate_secret_key,
        editable=False,
        help_text="Auto-generated 16-character secret key for this endpoint."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate to block API calls from this site without deleting the record."
    )
    hits_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Total number of successful API calls made from this site."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_hit_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Timestamp of the last successful API call."
    )

    class Meta:
        verbose_name = "eSIM Checker Endpoint"
        verbose_name_plural = "eSIM Checker Endpoints"
        ordering = ['-created_at']

    def __str__(self):
        status = "✓ Active" if self.is_active else "✗ Inactive"
        return f"{self.site_url} [{status}] — hits: {self.hits_count}"

    def regenerate_secret_key(self):
        """Generate and save a brand-new secret key for this endpoint."""
        self.secret_key = generate_secret_key()
        self.save(update_fields=['secret_key', 'updated_at'])

    def increment_hits(self):
        """Atomically increment the hit counter and record the timestamp."""
        ESIMCheckerEndpoint.objects.filter(pk=self.pk).update(
            hits_count=models.F('hits_count') + 1,
            last_hit_at=timezone.now()
        )
