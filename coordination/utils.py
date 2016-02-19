from string import digits
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from slugify import slugify_ru


def generate_random_username(name, length=4, chars='abcdefghjkmnpqrstuvwxyz''23456789'):
    slug = slugify_ru(name, max_length=8, to_lower=True, separator='')
    salt = get_random_string(length=length, allowed_chars=chars)
    username = "{0}{1}".format(slug, salt)
    try:
        User.objects.get(username=username)
        return generate_random_username(name, length=length, chars=chars)
    except User.DoesNotExist:
        return username


def generate_random_password(length=6, chars=digits):
    return get_random_string(length=length, allowed_chars=chars)


def get_timedelta(time):
    now = timezone.now()
    if time < now:
        return 0
    timedelta = time - now
    return timedelta.seconds


def get_timedelta_with_now(time):
    now = timezone.now()
    if now < time:
        return 0
    timedelta = now - time
    return timedelta.seconds


def time_in_minutes(time):
    return time // 60
