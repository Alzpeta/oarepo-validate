import pytest
from werkzeug.exceptions import BadRequest

from oarepo_validate import json_loader
from oarepo_validate.loaders import json_files_loader


def test_json_loader(app):
    with app.test_request_context(data=b'{}', headers={
        'Content-Type': 'application/json'
    }):
        assert json_loader() == {}

    with pytest.raises(BadRequest):
        with app.test_request_context(data=b'{invalid}', headers={
            'Content-Type': 'application/json'
        }):
            assert json_loader() == {}


def test_files_loader(app):
    with app.test_request_context(data=b'{}', headers={
        'Content-Type': 'application/json'
    }):
        assert json_files_loader() == {}

    with app.test_request_context(data=b'{"_bucket": "blah"}', headers={
        'Content-Type': 'application/json'
    }):
        assert json_files_loader() == {}

    with app.test_request_context(data=b'{"_files": "blah"}', headers={
        'Content-Type': 'application/json'
    }):
        assert json_files_loader() == {}
