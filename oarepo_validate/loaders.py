from flask import request


def json_loader():
    """Do-nothing loader."""
    return request.get_json(force=True)
