# -*- coding: utf-8 -*-
"""discord and other format functions"""

from html.parser import HTMLParser


class MLStripper(HTMLParser):
    """Markup Language Stripper"""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, data):
        """handle data"""
        self.fed.append(data)

    def get_data(self):
        """return data"""
        return "".join(self.fed)

    def error(self, message):
        """had to do this cuz abstract"""
        return message


def strip_tags(html):
    """strips text from xml/html tags"""
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()


def box(text, lang=""):
    """discord format for box with optional language highlighting"""
    return f"```{lang}\n{text}\n```"


def inline(text):
    """discord format for inline box"""
    return f"`{text}`"


def italics(text):
    """discord format for itallic text"""
    return f"*{text}*"


def bold(text):
    """discord format for itallic text"""
    return f"**{text}**"


def strikethrough(text):
    """discord format for strikethrough text"""
    return f"~~{text}~~"


def underline(text):
    """discord format for underlining"""
    return f"__{text}__"


def pagify(text, delims=None, page_length=2000):
    """DOES NOT RESPECT MARKDOWN BOXES OR INLINE CODE"""
    if delims is None:
        delims = ["\n"]
    in_text = text

    while len(in_text) > page_length:
        closest_delim = max([in_text.rfind(d, 0, page_length) for d in delims])
        closest_delim = closest_delim if closest_delim != -1 else page_length

        to_send = in_text[:closest_delim]
        yield str(to_send)
        in_text = in_text[closest_delim:]

    yield str(in_text)
