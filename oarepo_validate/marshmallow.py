from invenio_records import Record
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors
from jsonpatch import apply_patch
from marshmallow import ValidationError
from sqlalchemy.util import symbol

from .proxies import current_validate
from .signals import before_marshmallow_validate, after_marshmallow_validate

KNOWN_RECORD_VALIDATION_PROPS = {
    'format_checker',
    'validator'
}


class Keep:
    def __init__(self, value):
        self.value = value


DELETED = symbol('deleted')


class MarshmallowValidatedRecordMixin:
    """
    A mixin that keeps marshmallow schema and PID fetcher. This way later in processing
    (for example, out of invenio REST methods) we can use marshmallow for validation.
    """
    MARSHMALLOW_SCHEMA = None
    """The metadata schema"""

    PID_FETCHER = None
    """
    Optional PID fetcher to set up the persistent identifier in context
    (and have the same context as invenio has)
    """

    VALIDATE_MARSHMALLOW = True
    """
    Setting this variable to True will make the validate() method (called inside commit)
    to trigger marshmallow validation. If the same marshmallow schema is used on rest loaders,
    it will be validated twice.

    To fix this and be safe on REST side, set VALIDATE_MARSHMALLOW to False and VALIDATE_PATCH to True
    """

    MERGE_WITH_VALIDATED = True
    """
    If set to True, if validation is successful the validated data will be merged into the record's
    metadata.
    """

    MERGE_WITH_VALIDATED_ERROR = True
    """
    If set to True, if validation is not successful but partially valid content is reported from
    marshmallow, it will be merged into the record's metadata.
    """

    VALIDATE_PATCH = False
    """
    If VALIDATE_MARSHMALLOW is set to False, setting this variable will cause patch method to perform
    marshmallow validation. See the readme for details
    """

    def validate_marshmallow(self, data=None, validate_kwargs=None):
        """
        Validates marshmallow and returns validated data.
        Does not modify the record nor save it to the database.
        """
        if data is None:
            data = self
        validate_kwargs = validate_kwargs or {}
        context = {**validate_kwargs}
        if self.PID_FETCHER is not None:
            pid = self.__class__.PID_FETCHER(None, data)
            context['pid'] = pid
        context['record'] = self
        before_marshmallow_validate.send(
            self,
            record=self, context=context, **validate_kwargs)
        try:
            result = self.MARSHMALLOW_SCHEMA(context=context).load(data)
            after_marshmallow_validate.send(
                self,
                record=self, context=context, result=result, error=None, **validate_kwargs)
            return result
        except ValidationError as error:
            after_marshmallow_validate.send(
                self,
                record=self, context=context, result=None, error=error, **validate_kwargs)
            err = MarshmallowErrors(error.messages)
            err.valid_data = error.valid_data
            raise err
        except Exception as error:
            after_marshmallow_validate.send(
                self,
                record=self, context=context, result=None, error=error, **validate_kwargs)
            raise

    def patch(self, patch):
        """Patch record metadata. Overrides invenio patch to perform marshmallow validation

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        
        data = super().patch(patch)
        if self.VALIDATE_PATCH:
            data = self.validate_marshmallow(dict(data))
        return self.__class__(data, model=self.model)

    def validate(self, **kwargs):
        """
        Overloaded invenio validate. If VALIDATE_MARSHMALLOW is set on the instance
        or validate_marshmallow parameter set to True, marhsmallow validation will be performed
        as well

        :param validate_marshmallow set to True to perform marshmallow validation. If set to False,
        class-wide VALIDATE_MARSHMALLOW is used.
        """

        if kwargs.pop('validate_marshmallow', self.VALIDATE_MARSHMALLOW):
            try:
                data = self.validate_marshmallow(validate_kwargs=kwargs)
                if self.MERGE_WITH_VALIDATED:
                    self._merge_in(data)
            except MarshmallowErrors as e:
                if self.MERGE_WITH_VALIDATED_ERROR:
                    self._merge_in(e.valid_data)
                raise

        kwargs = {
            k: v for k, v in kwargs.items() if k in KNOWN_RECORD_VALIDATION_PROPS
        }
        return super().validate(**kwargs)

    def _merge_in(self, valid_data):
        current_validate.merge_function(self, valid_data)


class MarshmallowValidatedRecord(MarshmallowValidatedRecordMixin, Record):
    """
    Marshmallow-enabled record
    """
    pass
