from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'positions',
        'experience',
        'location',
        'status',
        'posted_by',
        'posted_at',
    )

    list_filter = ('status', 'location', 'posted_at')
    search_fields = ('title', 'subtitle', 'location')
    ordering = ('-posted_at',)
