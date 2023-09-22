from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Profile, Avatar


class AvatarInline(admin.TabularInline):
    model = Avatar


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [
        AvatarInline,
    ]
    list_display = (
        "pk",
        "user",
        "user_id",
        "fullName",
        "email",
        "registration_time",
    )
    list_display_links = "pk", "user"
    ordering = ("pk",)
    search_fields = ("user",)
    fields = (
        "user",
        "fullName",
        "email",
        "status",
        "phone",
    )
