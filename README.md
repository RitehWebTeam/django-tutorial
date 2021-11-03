- Tutorial based on django polls https://docs.djangoproject.com/en/3.2/intro/tutorial01/
- Original polls repo: https://github.com/do-community/django-polls/tree/master/polls
# 1. Task:Add 3 roles
1. Staff user
   1. Can add a new poll
   2. Can edit a poll
   3. Can delete a poll
2. Regular user
   1. Can vote
   2. Can view a poll results
3. Anonymous user
   1. Can only view a poll result

## Step-by-step

1. Enable only staff user to interact with polls

We have 3 views: detail, results and vote. User object can be fetched with the following.

```python
def detail(request, question_id):
    user = request.user
    ...
```

We can restrict access with the following piece of code. Apply this to all 3 views.
```python
def detail(request, question_id):
     if not request.user.is_staff:
        raise PermissionDenied('You are not allowed to perform this action.')
    ...
```

2. We don't want to click every time. Let's create test for vote, results and detail functionality.
**Read first:** https://docs.djangoproject.com/en/3.2/topics/testing/overview/

Go to file tests.py and add the following code.
```python
    def setUp(self):
        username = 'staff_user'
        password = 'test123'
        self.question = Question.objects.create(question_text='text', pub_date=timezone.now())
        self.choice = Choice.objects.create(question=self.question, choice_text='text')
        self.staff = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True,
        )
        self.client = Client()

    def test_detail_view(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('polls:detail', kwargs={'question_id': self.question.pk}))
        self.assertEqual(response.status_code, 200)
```
You can run tests with the following commands:

```shell
python manage.py test polls

python manage.py test polls.tests.StaffUserTests

python manage.py test polls.tests.StaffUserTests.test_detail_view

```

Add tests for results and vote.
```shell
...
 def test_results_view(self):
     self.client.force_login(self.staff)
     response = self.client.get(reverse('polls:results', kwargs={'question_id': self.question.pk}))
     self.assertEqual(response.status_code, 200)

 def test_vote_view(self):
     self.client.force_login(self.staff)
     response = self.client.post(
         reverse('polls:vote', kwargs={'question_id': self.question.pk}),
         {'choice': self.choice.pk}
     )
     self.assertEqual(response.status_code, 302)
```
3. Management commands
Let's write custom management command so we can reset out db whenever we wish.
**Read first:** https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#management-commands-and-locales

First, we need to create folder management/commands and inside of it file named by our custom command - populate_db.py
```python
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

staff_username = 'staff_user'
regular_user = 'regular_user'
password = 'test123'


class Command(BaseCommand):
    help = 'Populates database with dummy data'

    def create_users(self):
        self.staff = User.objects.create_user(
            username=staff_username,
            password=password,
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username=regular_user,
            password=password,
            is_staff=False,
            is_superuser=False
        )

    def handle(self, *args, **options):
        self.create_users()
        print('Users created')
```

Now we can run our command by: ```python manage.py populate_db```

4. Enable anonymous user to view everything
We have to allow anonymous user to check poll results. So remove restriction in detail and results view.

```python
def detail(request, question_id):
    if not request.user.is_staff:
        raise PermissionDenied('You are not allowed to perform this action.')
...
def results(request, question_id):
    if not request.user.is_staff:
        raise PermissionDenied('You are not allowed to perform this action.')
```

5. Add vote restriction for anonymous user
We have 2 options with this: using decorators or manual check.
   1. Using decorators - redirect to login
```python
from django.contrib.auth.decorators import login_required
...
@login_required(login_url='login')
def vote(request, question_id):
    ...
```

   2. Manual check
```python
def vote(request, question_id):
    if not request.user.is_authenticated:
        raise PermissionDenied('You are not allowed to perform this action.')
```

6. Django admin

6.1 Add search in questions
```python
# admin.py
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    search_fields = ['question_text']
```

6.2 Add filters in questions
```python
# admin.py
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date', 'was_published_recently']
    search_fields = ['question_text']
```

6.3 Show choices next to the questions
```python
from django.utils.html import format_html
from .models import Question, Choice


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'was_published_recently', 'get_choices')
    list_filter = ['pub_date',]
    search_fields = ['question_text']

    def get_choices(self, obj):
        html = ''
        choices = Choice.objects.filter(question=obj)
        for choice in choices:
            html += f'{choice.choice_text}<br>'
        return format_html(html)
```

6.4 Remove delete permission

```python
class QuestionAdmin(admin.ModelAdmin):
...
def has_delete_permission(self, request, obj=None):
    return False
```