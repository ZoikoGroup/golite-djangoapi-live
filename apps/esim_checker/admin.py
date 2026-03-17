from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ESIMCheckerEndpoint


@admin.register(ESIMCheckerEndpoint)
class ESIMCheckerEndpointAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------ #
    # List view
    # ------------------------------------------------------------------ #
    list_display = (
        'site_url',
        'masked_secret_key',
        'status_badge',
        'hits_count',
        'last_hit_at',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('site_url',)
    readonly_fields = (
        'secret_key_display',
        'hits_count',
        'last_hit_at',
        'created_at',
        'updated_at',
    )
    actions = ['activate_endpoints', 'deactivate_endpoints', 'regenerate_keys', 'reset_hits']

    # ------------------------------------------------------------------ #
    # Add / Change form
    # ------------------------------------------------------------------ #
    fieldsets = (
        ('Site Registration', {
            'fields': ('site_url', 'is_active'),
        }),
        ('Secret Key', {
            'fields': ('secret_key_display',),
            'description': (
                'The secret key is auto-generated when you add a new endpoint. '
                'Use the <strong>Regenerate secret key</strong> action from the list view '
                'to rotate it.'
            ),
        }),
        ('Statistics', {
            'fields': ('hits_count', 'last_hit_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ------------------------------------------------------------------ #
    # Custom display columns
    # ------------------------------------------------------------------ #
    @admin.display(description='Secret Key')
    def masked_secret_key(self, obj):
        key = obj.secret_key
        masked = key[:4] + '●' * (len(key) - 4)
        return format_html(
            '<code style="font-family:monospace">{}</code>',
            masked
        )

    @admin.display(description='Full Secret Key (copy)')
    def secret_key_display(self, obj):
        """Reveal full key in the detail form with a copy button."""
        if not obj.pk:
            return "Will be generated on save."
        return format_html(
            '<code id="sk" style="font-family:monospace;font-size:1.1em;'
            'background:#f4f4f4;padding:4px 8px;border-radius:4px">{}</code>'
            '&nbsp;<button type="button" onclick="'
            'navigator.clipboard.writeText(document.getElementById(\'sk\').innerText);'
            'this.innerText=\'Copied!\';setTimeout(()=>this.innerText=\'Copy\',1500)"'
            ' style="cursor:pointer">Copy</button>',
            obj.secret_key,
        )

    @admin.display(description='Status', boolean=False)
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color:white;background:#28a745;padding:2px 8px;'
                'border-radius:10px;font-size:0.8em">{}</span>',
                '● Active'
            )
        return format_html(
            '<span style="color:white;background:#dc3545;padding:2px 8px;'
            'border-radius:10px;font-size:0.8em">{}</span>',
            '● Inactive'
        )

    # ------------------------------------------------------------------ #
    # Bulk actions
    # ------------------------------------------------------------------ #
    @admin.action(description='✅ Activate selected endpoints')
    def activate_endpoints(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} endpoint(s) activated.", messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected endpoints')
    def deactivate_endpoints(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} endpoint(s) deactivated.", messages.WARNING)

    @admin.action(description='🔑 Regenerate secret key for selected endpoints')
    def regenerate_keys(self, request, queryset):
        for endpoint in queryset:
            endpoint.regenerate_secret_key()
        self.message_user(
            request,
            f"Secret keys regenerated for {queryset.count()} endpoint(s). "
            "Make sure to update the key in the corresponding client applications.",
            messages.SUCCESS,
        )

    @admin.action(description='🔄 Reset hit counter for selected endpoints')
    def reset_hits(self, request, queryset):
        updated = queryset.update(hits_count=0, last_hit_at=None)
        self.message_user(request, f"Hit counters reset for {updated} endpoint(s).", messages.SUCCESS)

    # ------------------------------------------------------------------ #
    # Prevent editing the secret_key field directly in the form
    # ------------------------------------------------------------------ #
    def get_readonly_fields(self, request, obj=None):
        base = list(self.readonly_fields)
        if obj:  # editing existing record
            base.append('site_url')  # URL is immutable once registered
        return base
