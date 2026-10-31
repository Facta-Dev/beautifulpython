"""One deliberate violation per lint in lints/ruff.toml.

Each expect marker says which rule must report on that line. The file must
otherwise be clean, so scripts/check-lints.py fails on both missing and
unexpected diagnostics. Everything below must stay a real violation the way an
unreviewed contributor would write it.
"""

import os  # expect: F401, an unused module import

from os.path import *  # expect: F403

from typing import List  # expect: UP035


def unused_local(x):
    result = x + 1  # expect: F841
    return x


def star_user():
    return join("a", "b")  # expect: F405


def bad_defaults(items=[], cache={}):  # expect: B006
    return items


def no_from(err=None):
    try:
        raise ValueError("inner")  # expect: EM101
    except ValueError as err:
        msg = f"wrapped: {err}"
        raise ValueError(msg)  # expect: B904


def raw_message(x):
    if x is None:
        raise ValueError("empty input")  # expect: EM101
    msg = f"bad value {x}"
    return msg


def fstring_message(values):
    """The f-string belongs on its own variable, not inline in the raise."""
    if not values:
        raise ValueError(f"expected values, got {values!r}")  # expect: EM102
    return values


def late_import():
    import json  # expect: PLC0415
    return json.dumps({})


def guard_style(value):
    assert value is not None  # expect: S101
    if value == None:  # expect: E711
        return False
    if value == True:  # expect: E712
        return True
    try:
        return int(value)
    except:  # expect: E722
        return 0


def printer():
    print("hello")  # expect: T201


class LegacyBase(object):  # expect: UP004
    pass


def annotated_old() -> List[int]:  # expect: UP006
    return [1, 2]


def short_noqa():
    value = 1  # noqa: E501  # expect: RUF100
    return value


def long_line():
    return "this line is deliberately far longer than the configured one hundred character limit so E501 fires"  # expect: E501
