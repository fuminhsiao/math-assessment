from django.core.management.base import BaseCommand
from django.db import transaction
from assessments.models import FreeAnnotation


class Command(BaseCommand):
    help = "Reset all teacher note positions to the universal top-left corner, without deleting note text."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Confirm the database-wide position reset.")

    def handle(self, *args, **options):
        if not options["yes"]:
            self.stdout.write(self.style.WARNING(
                "No changes made. Run: python manage.py reset_teacher_note_positions --yes"
            ))
            return
        with transaction.atomic():
            count = FreeAnnotation.objects.update(x=-99.0, y=-99.0)
        self.stdout.write(self.style.SUCCESS(
            f"Reset positions for {count} teacher notes. Note text was preserved."
        ))
