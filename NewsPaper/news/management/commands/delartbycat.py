from django.core.management.base import BaseCommand, CommandError
from ...models import *


class Command(BaseCommand):
    help = 'This command delete articles by category'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        cat = [(i['name']) for i in Category.objects.values()]
        cat_str = " ,".join(cat)
        self.stdout.readable()
        self.stdout.write(f'Введите название категории, статьи в которой хотите удалить ({cat_str}): ')
        answer = input()

        if answer in cat:
            Post.objects.filter(category__name=answer).delete()
            self.stdout.write(self.style.SUCCESS('Успешно!'))
            return

        self.stdout.write(self.style.ERROR('Неверный ввод!'))
