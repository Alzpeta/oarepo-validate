from oarepo_validate.marshmallow import Keep, DELETED


def merge(base, next):
    if next is DELETED:
        return DELETED
    if isinstance(next, Keep):
        return next.value  # perform no merging here
    if isinstance(base, list) or isinstance(next, list):
        return merge_lists(base, next)
    if isinstance(base, dict) or isinstance(next, dict):
        return merge_dicts(base, next)
    return next


def merge_lists(base, next):
    if next is None:
        next = []

    if not isinstance(base, list):
        base = []

    for idx in range(min(len(base), len(next))):
        base[idx] = merge(base[idx], next[idx])
    if len(next) > len(base):
        base.extend(next[len(base):len(next)])
    for k in reversed(range(len(base))):
        if base[k] is DELETED:
            del base[k]
    return base


def merge_dicts(base, next):
    if next is None:
        next = {}
    if not isinstance(base, dict):
        base = {}

    for k, v in list(base.items()):
        if k in next:
            merged = merge(base[k], next[k])
            if merged is DELETED:
                del base[k]
            else:
                base[k] = merged
    for k, v in next.items():
        if k not in base and v is not DELETED:
            base[k] = v
    return base
