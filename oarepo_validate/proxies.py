from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

current_validate = LocalProxy(
    lambda: current_app.extensions['oarepo-validate'])
"""Helper proxy to access oarepo validate state object."""
