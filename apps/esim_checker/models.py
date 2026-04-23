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
        help_text="Origin URL of the registered site (e.g. https://driverxmobile.com)"
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


class ESIMCheckerLog(models.Model):
    """
    Cache table for IMEI lookup results from VCare.
    On a cache hit the VCare API is skipped entirely.
    Fields match the requested schema:
        id           – auto primary key
        imei         – the queried IMEI
        url          – the VCare endpoint URL that was called
        created_date – SQLite-compatible UTC timestamp (auto-set on first insert)
        hit_count    – incremented every time this cached record is served
    """
    imei = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="IMEI number that was checked."
    )
    url = models.CharField(
        max_length=512,
        help_text="VCare API URL that returned the successful response."
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        help_text="UTC timestamp when this IMEI was first successfully checked."
    )
    hit_count = models.PositiveIntegerField(
        default=1,
        help_text="How many times this cached result has been served (starts at 1 on first insert)."
    )
    # Store the full VCare response so we can replay it from cache
    cached_response = models.JSONField(
        help_text="Full JSON response payload from the VCare API."
    )

    class Meta:
        verbose_name = "eSIM Checker Log"
        verbose_name_plural = "eSIM Checker Logs"
        ordering = ['-created_date']

    def __str__(self):
        return f"IMEI {self.imei} — hits: {self.hit_count}"

    def increment_hit_count(self):
        """Atomically increment hit_count for this cached record."""
        ESIMCheckerLog.objects.filter(pk=self.pk).update(
            hit_count=models.F('hit_count') + 1
        )
