import pytest
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors
from marshmallow import Schema, fields, pre_load

from oarepo_validate.marshmallow import MarshmallowValidatedRecord


def test_version(db, app):
    from oarepo_validate.version import __version__
