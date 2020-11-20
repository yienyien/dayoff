from django.core import management
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Run into docker"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        management.call_command("makemigrations")
        management.call_command("migrate")
        # management.call_command('collectstatic', '--noinput')

        try:
            user = User.objects.create_superuser(
                username="aurelien",
                password="aurelienpassword",
                email="aurelien.moreau@yienyien.net",
            )
            Token.objects.create(user=user)

        except:
            print("Super user is already created")

        management.call_command("runserver", "--noreload", "0.0.0.0:8000")
