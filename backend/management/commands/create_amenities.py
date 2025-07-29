from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from backend.models import Amenity

class Command(BaseCommand):
    help = 'Create 100 unique real estate amenities'

    def handle(self, *args, **options):
        faker = Faker()
        User = get_user_model()
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users available to assign created_by'))
            return

        # Real unique amenities list
        names = [
            'In‑unit washer & dryer',
            'High‑speed internet',
            'Pre‑installed Wi‑Fi',
            'Air conditioning',
            'Dishwasher',
            'Smart lock',
            'Smart thermostat',
            'Video doorbell',
            'EV charging station',
            'Secure package lockers',
            'Fitness center',
            'Rooftop lounge',
            'Swimming pool',
            'Community garden',
            'Dog park',
            'Pet spa',
            'Pet washing station',
            'Co‑working space',
            'On‑site laundry room',
            'Hardwood floors',
            'Walk‑in closet',
            'Large windows',
            'Private balcony',
            'Microwave',
            'Garbage disposal',
            'Energy‑efficient appliances',
            'Balcony or patio',
            'Fireplace',
            'Clubhouse',
            'Jogging path',
            'Media room',
            'Sports courts',
            'Yoga room',
            'BBQ outdoor kitchen',
            'Secure garage parking',
            'Covered parking',
            'Bike storage',
            'Bike repair station',
            'Smart lighting',
            'Online rent payment',
            'Online maintenance requests',
            'Electric car charger',
            'Concierge service',
            'Resident events',
            'Sauna',
            'Spa services',
            'Pilates studio',
            'Business center',
            'Package Room',
            'Hot tub',
            'Childrens play area',
            'Community kitchen',
            'Library / reading room',
            'Guest suite',
            'Storage lockers',
            'Smart appliances',
            'Virtual doorman',
            'Motion sensor exterior lights',
            'Accessibility ramps',
            'Elevator',
            'Smart building access',
            'Sound system in common areas',
            'Happy hour events',
            'Art gallery rotating',
            'Rotating social events',
            'Craft room / hobby room',
            'Private dining room',
            'Walking trails',
            'BBQ grills',
            'Outdoor seating lounge',
            'Cinema room',
            'Game room',
            'Children play room',
            'Study / study pods',
            'Golf simulator',
            'Tennis court',
            'Sauna & steam room',
            'Roof deck',
            'Fire pit lounge',
            'Electric vehicle charging',
            'Smart blinds',
            'Smart garage door',
            'Rain‑shower bathroom',
            'Heated floors',
            'Wine refrigerator',
            'Wet bar',
            'Food truck access',
            'Rooftop garden',
            'Bike‑share docking station',
            'Package notification system',
            'Smart mirror',
            'Infrared sauna',
            'Cold plunge pool',
            'Circadian lighting',
            'Biophilic living wall',
            'Wine storage vault',
            'On‑site Tesla share vehicle',
            'Bowling alley',
            'Golf simulator',
            'Maker space / arts & craft studio',
            'Near School'
        ]

        names = list(dict.fromkeys(names))  # ensure unique
        if len(names) < 100:
            self.stdout.write(self.style.ERROR(f'Only {len(names)} unique names provided. Need 100.'))
            return

        # optionally trim to first 100
        names = names[:100]

        for name in names:
            Amenity.objects.get_or_create(
                name=name,
                defaults={
                    'created_by': faker.random_element(users),
                    'created_at': faker.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc),
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully created 100 unique amenities'))
