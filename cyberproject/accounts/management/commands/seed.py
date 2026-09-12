from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from notes.models import Note

PASSWORD = 'password123'

# Note ids are pinned on purpose: the access-control demos rely on typing a
# known id into the URL, so re-running this command must always produce the
# same ids instead of letting them creep upwards.
USERS = [
    # username, is_staff, notes as (id, title, body)
    ('alice', False, [
        (1, 'Alice shopping list', 'Milk, bread, coffee.'),
        (2, 'Alice diary', 'Today I finally understood Django URL routing.'),
    ]),
    ('bob', False, [
        (3, 'Bob bank details', 'Account 12345678, PIN 4321. Very secret.'),
        (4, 'Bob holiday plans', 'Two weeks in Lapland in December.'),
    ]),
    ('admin', True, [
        (5, 'Admin todo', 'Review new user registrations.'),
    ]),
]


class Command(BaseCommand):
    help = 'Create the demo users and notes used for the security demos.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Wipe every note first so the pinned ids below are always free.
        Note.objects.all().delete()

        for username, is_staff, notes in USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'},
            )
            user.is_staff = is_staff
            user.is_superuser = is_staff
            user.set_password(PASSWORD)
            user.save()

            for note_id, title, body in notes:
                Note.objects.create(
                    pk=note_id,
                    owner=user,
                    title=title,
                    body=body,
                )

            state = 'created' if created else 'reset'
            self.stdout.write(f'{state}: {username} (staff={is_staff})')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. All demo users have the password: {PASSWORD}'
        ))
