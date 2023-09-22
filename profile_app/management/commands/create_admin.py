from django.contrib.auth.models import User
from django.core.management import BaseCommand

from profile_app.models import Profile, Avatar


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create_superuser(username="admin", password="admin")
        user.save()

        profile = Profile.objects.create(fullName="administrator", user_id=user.id)
        Avatar.objects.create(profile=profile, src=None, alt="default")
