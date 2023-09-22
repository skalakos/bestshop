from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


def profile_avatar_dir_path(instance: "Avatar", filename: str) -> str:
    return "users/user_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Profile(models.Model):
    STATUS_CHOICES = [
        (_("beginner"), _("BEGINNER")),
        (_("silver"), _("SILVER")),
        (_("gold"), _("GOLD")),
        (_("platinum"), _("PLATINUM")),
    ]

    class Meta:
        ordering = ["user"]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name=_("user")
    )
    fullName = models.CharField(max_length=50, blank=True, verbose_name=_("full_name"))
    email = models.EmailField(max_length=200, verbose_name="email")
    registration_time = models.DateTimeField(
        auto_now_add=True, null=False, blank=True, verbose_name=_("registration_time")
    )
    # avatar = models.OneToOneField('Avatar', on_delete=models.CASCADE, null=True, blank=True,  verbose_name=_('avatar'))
    phone = models.CharField(
        max_length=40, null=True, blank=True, verbose_name=_("phone")
    )
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=20, blank=True, verbose_name=_("status")
    )
    balance = models.IntegerField(null=True, blank=True, verbose_name=_("balance"))

    def __str__(self):
        return self.fullName


class Avatar(models.Model):
    profile = models.OneToOneField(
        Profile, null=True, on_delete=models.PROTECT, related_name="avatar"
    )
    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_avatar_dir_path,
        verbose_name=_("avatar"),
    )
    alt = models.CharField(
        max_length=250, null=False, blank=True, verbose_name=_("description")
    )

    def __str__(self):
        return f"{self.pk}: {self.alt}".format(self.pk, self.alt)


#
