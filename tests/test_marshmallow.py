import pytest
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors
from marshmallow import Schema, fields

from oarepo_validate.marshmallow import MarshmallowValidatedRecord


class TestSchema(Schema):
    name = fields.Str(required=True)


class TestRecord(MarshmallowValidatedRecord):
    MARSHMALLOW_SCHEMA = TestSchema


class TestRecordNoValidation(TestRecord):
    VALIDATE_MARSHMALLOW = False
    VALIDATE_PATCH = True


def test_validate(db, app):
    # create must not pass as name is not set
    with pytest.raises(MarshmallowErrors):
        TestRecord.create({})

    # creating valid record
    rec = TestRecord.create({'name': 'test'})

    # can commit a valid record
    rec.commit()

    # making the record invalid
    del rec['name']

    # can not commit invalid record
    with pytest.raises(MarshmallowErrors):
        rec.commit()


def test_validate_patch(db, app):
    # VALIDATE_MARSHMALLOW is not set, so create will pass
    rec = TestRecordNoValidation.create({})

    # validate raises exception as name is not present
    with pytest.raises(MarshmallowErrors):
        rec.validate_marshmallow()

    # patch raises exception as name will not be present after patch
    with pytest.raises(MarshmallowErrors):
        rec.patch([])

    # adding name will make it ok
    rec.patch([{
        'op': 'add',
        'path': '/name',
        'value': 'test'
    }])


def test_prevent_validation(db, app):
    # can create an invalid record if needed
    rec = TestRecord.create({}, validate_marshmallow=False)

    # but can not commit it normally
    with pytest.raises(MarshmallowErrors):
        rec.commit()

    # can temporarily switch off the validation
    rec.commit(validate_marshmallow=False)
