from database import db_session
from database_models import Shortcode


#@functools.lru_cache()
def get_shortcode_target(shortcode):
    return Shortcode.query.filter(Shortcode.shortcode == shortcode.lower()).first()


def find_by_target(target_url):
    return Shortcode.query.filter(Shortcode.target_url == target_url).first()

def get_all():
    return Shortcode.query.all()


def insert_shortcode(shortcode, target_url, random):
    if not shortcode or len(shortcode) == 0 or not target_url or len(target_url) == 0:
        return False

    sc = Shortcode(shortcode.lower(), target_url, random)
    db_session.add(sc)
    db_session.commit()
    return True # How to check DB result?


def update_shortcode(shortcode, target_url):
    if not shortcode or len(shortcode) == 0 or not target_url or len(target_url) == 0:
        return False

    existing = get_shortcode_target(shortcode)
    if not existing:
        return False

    existing.target_url = target_url
    db_session.add(existing)
    db_session.commit()
    return True # How to check DB result?


def delete_shortcode(shortcode):
    if not shortcode or len(shortcode) == 0:
        return False

    sc = get_shortcode_target(shortcode)
    db_session.delete(sc)
    db_session.commit()
    return True # How to check DB result?
