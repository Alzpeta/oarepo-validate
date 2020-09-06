from invenio_records import Record
from invenio_records_rest.loaders.marshmallow import MarshmallowErrors
from jsonpatch import apply_patch
from marshmallow import ValidationError

from .signals import before_marshmallow_validate, after_marshmallow_validate


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
            raise MarshmallowErrors(error.messages)

    def patch(self, patch):
        """Patch record metadata. Overrides invenio patch to perform marshmallow validation

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        data = apply_patch(dict(self), patch)
        if self.VALIDATE_PATCH:
            data = self.validate_marshmallow(data)
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
            data = self.validate_marshmallow(validate_kwargs=kwargs)
            self.update(data)
        return super().validate()   # do not pass kwargs along the stack


class MarshmallowValidatedRecord(MarshmallowValidatedRecordMixin, Record):
    """
    Marshmallow-enabled record
    """
    pass
