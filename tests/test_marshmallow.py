import pytest
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors

from oarepo_validate import before_marshmallow_validate, after_marshmallow_validate
from .records import *


def test_validate(db, app):
    # create must not pass as name is not set
    with pytest.raises(MarshmallowErrors):
        RecordTestRecord.create({})

    # creating valid record
    rec = RecordTestRecord.create({'name': 'test'})

    # can commit a valid record
    rec.commit()

    # making the record invalid
    del rec['name']

    # can not commit invalid record
    with pytest.raises(MarshmallowErrors):
        rec.commit()


def test_validate_patch(db, app):
    # VALIDATE_MARSHMALLOW is not set, so create will pass
    rec = RecordTestRecordNoValidation.create({})

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
    rec = RecordTestRecord.create({}, validate_marshmallow=False)

    # but can not commit it normally
    with pytest.raises(MarshmallowErrors):
        rec.commit()

    # can temporarily switch off the validation
    rec.commit(validate_marshmallow=False)


def test_pid(db, app):
    rec = RecordTestPIDRecord.create({'id': 123})


def test_signals(db, app):
    def before(sender, record, context, **kwargs):
        context['initialized'] = True

    def after(sender, record, context, result, **kwargs):
        assert context['passed']
        result['test'] = True
        record.test = True

    try:
        before_marshmallow_validate.connect(before)
        after_marshmallow_validate.connect(after)

        rec = RecordTestContextRecord.create({'name': 'abc'}, extra_context_param=True)
        assert rec['test'] is True
        assert rec.test is True

        del rec['test']

        rec.commit(extra_context_param=True)
    finally:
        before_marshmallow_validate.disconnect(before)
        after_marshmallow_validate.disconnect(after)
