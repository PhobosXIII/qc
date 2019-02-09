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
    if not time:
        return 0
    now = timezone.now()
    if time < now:
        return 0
    timedelta = time - now
    return timedelta.seconds


def get_timedelta_with_now(time):
    if not time:
        return 0
    now = timezone.now()
    if now < time:
        return 0
    timedelta = now - time
    return timedelta.seconds


def get_interval(start, end):
    if not start or not end:
        return None
    if end < start:
        return None
    timedelta = end - start
    return timedelta


def time_in_minutes(time):
    if not time:
        return 0
    return time // 60


def is_game_over(count, missions, quest):
    """

    :param count: count of player's uncompleted missions
    :param missions: all missions or current missions of quest
    :param quest: parent quest
    :return: true if game for player is over, false otherwise
    """
    return missions and count == 0 or quest.is_game_over or quest.ended


def is_ml_game_over(player, quest):
    count = 0
    current_missions = quest.current_missions_multilinear(player)
    for current_mission in current_missions:
        if not current_mission.mission.is_finish:
            count += 1
    game_over = is_game_over(count, current_missions, quest)
    return game_over
