from django.contrib import admin

from . import models


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class OutgoingSMSAdmin(ReadOnlyAdmin):
    list_display = (
        'contact',
        'body',
        'timestamp',
        'twilio_sid',
    )


class IncomingSMSAdmin(ReadOnlyAdmin):
    list_display = (
        'contact',
        'body',
        'twilio_date_sent',
        'twilio_sid',
    )


admin.site.register(models.Contact)
admin.site.register(models.OutgoingSMS, OutgoingSMSAdmin)
admin.site.register(models.IncomingSMS, IncomingSMSAdmin)
