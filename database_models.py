from sqlalchemy import Column, String, Boolean
from database import Base

class Shortcode(Base):
    __tablename__ = "shortcodes"
    shortcode = Column(String(20), primary_key=True, unique=True)
    target_url = Column(String(1024))
    is_random = Column(Boolean())

    def __init__(self, shortcode=None, target_url=None, is_random=True):
        self.shortcode = shortcode
        self.target_url = target_url
        self.is_random = is_random

    def __repr__(self):
        return "<Shortcode %r>" % (self.shortcode)
