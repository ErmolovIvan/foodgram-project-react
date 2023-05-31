import csv
import os
from foodgram import settings

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def ingredient_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        units=row[1]
    )


class Command(BaseCommand):
    help = 'Load ingredients to DB'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                ingredient_create(row)
        self.stdout.write('The ingredients has been loaded successfully.')
