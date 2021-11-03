from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import string
import random

from polls.models import Question, Choice

staff_username = 'staff_user'
admin_username = 'admin'
admin_password = 'admin'
regular_user = 'regular_user'
password = 'test123'

QUESTION_COUNT = 100
CHOICE_PER_QUESTION = 3


def generate_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_date():
    start = timezone.now() - timedelta(days=10)
    delta = timedelta(days=10)
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


class Command(BaseCommand):
    help = 'Populates database with dummy data'

    def create_questions(self):
        for i in range(QUESTION_COUNT):
            question_text = generate_random_string(10)
            date = generate_random_date()
            q = Question.objects.create(question_text=question_text, pub_date=date)
            self.create_choices(q)

    def create_choices(self, question: Question):
        for i in range(CHOICE_PER_QUESTION):
            choice_text = generate_random_string(5)
            Choice.objects.create(question=question, choice_text=choice_text)

    def create_users(self):
        self.admin = User.objects.create_user(
            username=admin_username,
            password=admin_password,
            is_staff=True,
            is_superuser=True
        )
        self.staff = User.objects.create_user(
            username=staff_username,
            password=password,
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username=regular_user,
            password=password,
            is_staff=False,
            is_superuser=False
        )

    def handle(self, *args, **options):
        if User.objects.exists():
            User.objects.all().delete()
            print('Users cleared.')

        self.create_users()
        print('Users created')

        if Question.objects.exists() or Choice.objects.exists():
            Question.objects.all().delete()
            Choice.objects.all().delete()
            print('Questions and choices cleared.')

        self.create_questions()
        print('Questions created')
