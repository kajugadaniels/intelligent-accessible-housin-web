import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.models import Category
from faker import Faker
from slugify import slugify

class Command(BaseCommand):
    help = 'Create 20 real-estate property categories'

    def handle(self, *args, **options):
        faker = Faker()
        names = [
            'Single-family home', 'Townhouse (terraced house)', 'Condominium',
            'Co‑operative (co‑op)', 'Multi‑family duplex', 'Triplex / quadplex',
            'Apartment building (small)', 'Apartment building (mid‑rise)',
            'Apartment building (high‑rise)', 'Bungalow', 'Ranch‑style house',
            'Tiny house', 'Modular / prefab home', 'Mobile / manufactured home',
            'Studio flat', 'Penthouse', 'Vacant land (raw land)',
            'Mixed‑use development', 'Retail property', 'Industrial warehouse'
        ]
        names = list(dict.fromkeys(names))  # ensure unique
        if len(names) < 20:
            self.stdout.write(self.style.ERROR('Need at least 20 unique names'))
            return

        for name in names:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'created_at': faker.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {name}'))

        self.stdout.write(self.style.SUCCESS('Done creating 20 property categories'))
