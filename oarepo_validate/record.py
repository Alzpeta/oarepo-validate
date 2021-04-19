#
# Copyright (c) 2019 UCT Prague.
#
# record.py is part of Invenio Explicit ACLs
# (see https://github.com/oarepo/invenio-explicit-acls).
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""ACL related mixins for Record class."""
import json
from functools import wraps

from invenio_jsonschemas import current_jsonschemas
from invenio_records import Record
from jsonpatch import apply_patch


def convert_relative_schema_to_absolute(x):
    """Convert relative record schema to absolute if needed."""
    if x.startswith('http://') or x.startswith('https://'):
        return x
    return current_jsonschemas.path_to_url(x)


class AllowedSchemaMixin(object):
    """A mixin that keeps allowed and preferred schema. Not to be used directly."""

    # DO NOT forget to set these up in subclasses
    ALLOWED_SCHEMAS = ()
    PREFERRED_SCHEMA = None
    _RESOLVED = False

    @classmethod
    def _prepare_schemas(cls):
        """Converts ALLOWED_SCHEMAS and PREFERRED_SCHEMA to absolute urls."""
        if not cls._RESOLVED:
            cls.ALLOWED_SCHEMAS = tuple(convert_relative_schema_to_absolute(x) for x in cls.ALLOWED_SCHEMAS)
            cls.PREFERRED_SCHEMA = convert_relative_schema_to_absolute(cls.PREFERRED_SCHEMA)
            cls._RESOLVED = True

    @classmethod
    def _convert_and_get_schema(cls, data):
        """Locate $schema in data and if needed convert it to absolute. Returns the converted schema."""
        cls._prepare_schemas()
        schema = data.get('$schema')
        if schema:
            absolute_schema = convert_relative_schema_to_absolute(schema)
            if absolute_schema is not None and schema != absolute_schema:
                schema = absolute_schema
                data['$schema'] = absolute_schema
        return schema


class SchemaKeepingRecordMixin(AllowedSchemaMixin):
    """
    A mixin for Record class that makes sure $schema is always in allowed schemas.

    Note that this mixin is not enough, always use invenio_explicit_acls.marshmallow.SchemaEnforcingMixin
    as well. The reason is that Invenio does not inject custom Record implementation for PUT, PATCH and DELETE
    operations.
    """

    # DO NOT forget to set these up in subclasses
    ALLOWED_SCHEMAS = ()
    PREFERRED_SCHEMA = None
    _RESOLVED = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if '$schema' not in self:
            self._prepare_schemas()
            self['$schema'] = self.PREFERRED_SCHEMA
        else:
            self._check_schema(self)

    def clear(self):
        """Preserves the schema even if the record is cleared and all metadata wiped out."""
        schema = self.get('$schema')
        super().clear()
        if schema:
            self['$schema'] = schema

    def update(self, e=None, **f):
        """Dictionary update."""
        self._check_schema(e or f)
        return super().update(e, **f)

    @classmethod
    def _check_schema(cls, data):
        schema = cls._convert_and_get_schema(data)
        if schema:
            if schema not in cls.ALLOWED_SCHEMAS:
                raise AttributeError('Schema %s not in allowed schemas %s' % (data['$schema'], cls.ALLOWED_SCHEMAS))

    def __setitem__(self, key, value):
        """Dict's setitem."""
        if key == '$schema':
            self._prepare_schemas()
            if value not in self.ALLOWED_SCHEMAS:
                value = current_jsonschemas.path_to_url(value)
                if value not in self.ALLOWED_SCHEMAS:
                    raise AttributeError('Schema %s not in allowed schemas %s' % (value, self.ALLOWED_SCHEMAS))
            value = convert_relative_schema_to_absolute(value)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        """Dict's delitem."""
        if key == '$schema':
            raise AttributeError('Schema can not be deleted')
        return super().__delitem__(key)

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """
        Creates a new record instance and store it in the database.

        For parameters see :py:class:invenio_records.api.Record
        """
        cls._prepare_schemas()

        if '$schema' not in data:
            data['$schema'] = convert_relative_schema_to_absolute(cls.PREFERRED_SCHEMA)
        else:
            cls._check_schema(data)
        ret = super().create(data, id_, **kwargs)
        return ret

    def patch(self, patch):
        """Patch record metadata. Overrides invenio patch to check if schema has changed

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        record = super().patch(patch)
        self._check_schema(dict(record))
        return record


def files_keeping_wrapper(f):
    @wraps(f)
    def wrap(self, *args, **kwargs):
        bucket_id = self.get('_bucket')
        files = self.get('_files')
        ret = f(self, *args, **kwargs)
        if bucket_id:
            self['_bucket'] = bucket_id
        if files is not None:
            self['_files'] = files
        return ret

    return wrap


def json_equals(a, b):
    a = json.dumps(a, sort_keys=True)
    b = json.dumps(b, sort_keys=True)
    return a == b


class FilesKeepingRecordMixin:

    @files_keeping_wrapper
    def clear(self):
        super().clear()

    @files_keeping_wrapper
    def update(self, *args, **kwargs):
        """Dictionary update."""
        return super().update(*args, **kwargs)

    def patch(self, patch):
        bucket_id = self.get('_bucket')
        files = self.get('_files')

        record = super().patch(patch)
        if record.get('_bucket') != bucket_id:
            raise AttributeError('_bucket can not be overwritten')
        if not json_equals(record.get('_files'), files):
            raise AttributeError('_files can not be overwritten')
        return record


class SchemaEnforcingRecord(SchemaKeepingRecordMixin, Record):
    ALLOWED_SCHEMAS = ('records/record-v1.0.0.json',)
    PREFERRED_SCHEMA = 'records/record-v1.0.0.json'
