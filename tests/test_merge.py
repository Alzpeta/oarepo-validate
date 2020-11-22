from oarepo_validate.marshmallow import DELETED, Keep
from oarepo_validate.utils import merge


def test_merge_lists():
    l1 = [1, 2, 3]
    l2 = [3, 4]
    assert merge(l1, l2) == [3, 4, 3]

    l1 = [1]
    l2 = [3, 4]
    assert merge(l1, l2) == [3, 4]

    l1 = []
    l2 = [3, 4]
    assert merge(l1, l2) == [3, 4]

    l1 = [1, 2, 3]
    l2 = []
    assert merge(l1, l2) == [1, 2, 3]

    l1 = [1, 2, 3]
    l2 = None
    assert merge(l1, l2) == [1, 2, 3]

    l1 = [1, 2, 3]
    l2 = [3, DELETED, 4]
    assert merge(l1, l2) == [3, 4]

    l1 = [1, 2, 3]
    l2 = DELETED
    assert merge(l1, l2) == DELETED

    l1 = [1, 2, 3]
    l2 = Keep([3, 4])
    assert merge(l1, l2) == [3, 4]


def test_merge_dicts():
    d1 = dict(a=1, b=2)
    d2 = dict(a=3, b=4)
    assert merge(d1, d2) == dict(a=3, b=4)

    d1 = dict(a=1, b=2)
    d2 = dict()
    assert merge(d1, d2) == dict(a=1, b=2)

    d1 = dict(a=1, b=2)
    d2 = None
    assert merge(d1, d2) == dict(a=1, b=2)

    d1 = dict()
    d2 = dict(a=1, b=2)
    assert merge(d1, d2) == dict(a=1, b=2)

    d1 = dict(a=1, b=2)
    d2 = dict(a=DELETED, b=4)
    assert merge(d1, d2) == dict(b=4)

    d1 = dict(a=1, b=2)
    d2 = DELETED
    assert merge(d1, d2) == DELETED

    d1 = dict(a=1, b=2, c=3)
    d2 = Keep(dict(a=3, b=4))
    assert merge(d1, d2) == dict(a=3, b=4)
