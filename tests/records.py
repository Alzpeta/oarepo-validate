from marshmallow import Schema, fields, pre_load, post_load, INCLUDE

from oarepo_validate.marshmallow import MarshmallowValidatedRecord


class RecordTestSchema(Schema):
    name = fields.Str(required=True)


class RecordTestPIDSchema(Schema):
    id = fields.Int()

    @pre_load
    def on_load(self, in_data, **kwargs):
        assert 'pid' in self.context
        assert self.context['pid'] == 123
        return in_data


class RecordTestContextSchema(Schema):
    name = fields.Str(required=True)

    @post_load
    def loaded(self, data, **kwargs):
        assert self.context['initialized']
        assert self.context['extra_context_param'] is True
        self.context['passed'] = 1
        return data

    class Meta:
        unknown = INCLUDE


class RecordTestRecord(MarshmallowValidatedRecord):
    MARSHMALLOW_SCHEMA = RecordTestSchema


def fetcher(uuid, data, *args, **kwargs):
    print(uuid, data, *args, **kwargs)
    return data['id']


class RecordTestPIDRecord(MarshmallowValidatedRecord):
    MARSHMALLOW_SCHEMA = RecordTestPIDSchema
    PID_FETCHER = fetcher


class RecordTestRecordNoValidation(RecordTestRecord):
    VALIDATE_MARSHMALLOW = False
    VALIDATE_PATCH = True


class RecordTestContextRecord(MarshmallowValidatedRecord):
    MARSHMALLOW_SCHEMA = RecordTestContextSchema

