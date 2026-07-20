from hashlib import sha256

from django.conf import settings
from django.core.cache import cache


LIST_VERSION_KEY = 'masters:list:version'


def cache_ttl():
    return settings.CACHE_TTL


def list_version():
    version = cache.get(LIST_VERSION_KEY)
    if version is None:
        cache.add(LIST_VERSION_KEY, 1, None)
        version = cache.get(LIST_VERSION_KEY, 1)
    return version


def master_list_key(query_string):
    digest = sha256(query_string.encode()).hexdigest()[:20]
    return f'masters:list:v{list_version()}:{digest}'


def master_detail_key(master_id):
    return f'masters:{master_id}:detail'


def master_comments_key(master_id):
    return f'masters:{master_id}:comments:latest10'


def master_like_count_key(master_id):
    return f'masters:{master_id}:likes:count'


def master_comment_count_key(master_id):
    return f'masters:{master_id}:comments:count'


def bump_list_version():
    try:
        cache.incr(LIST_VERSION_KEY)
    except ValueError:
        cache.set(LIST_VERSION_KEY, 2, None)


def invalidate_master_cache(master_id):
    cache.delete_many([
        master_detail_key(master_id),
        master_comments_key(master_id),
        master_like_count_key(master_id),
        master_comment_count_key(master_id),
    ])
    bump_list_version()
