from django.contrib import admin

from .models import Diagnosis


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "validity_from", "validity_to"]
    list_display_links = ["code", "name"]
    search_fields = ["code", "name"]
    ordering = ["code"]
    list_filter = [("validity_to", admin.EmptyFieldListFilter)]
    fields = ["code", "name", "validity_from", "validity_to"]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append("code")
        return readonly_fields

    def save_model(self, request, obj, form, change):
        obj.audit_user_id = request.user.id_for_audit
        super().save_model(request, obj, form, change)