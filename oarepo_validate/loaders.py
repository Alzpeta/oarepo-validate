from flask import request


def json_loader():
    """Do-nothing loader."""
    return request.get_json(force=True)


def json_files_loader():
    """A loader that removes record-files stuff"""
    resp = json_loader()
    if '_bucket' in resp:
        del resp['_bucket']
    if '_files' in resp:
        del resp['_files']
    return resp
