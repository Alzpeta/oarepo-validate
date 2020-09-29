import pytest
from invenio_records import Record

from oarepo_validate.record import FilesKeepingRecordMixin


class FileRec(FilesKeepingRecordMixin, Record):
    pass


DATA = {'_bucket': '123', '_files': [{'key': 'test'}]}


def test_files_clear():
    rec = FileRec(DATA)

    rec.clear()
    assert dict(rec) == DATA


def test_files_update():
    rec = FileRec(DATA)
    rec.update(_bucket='456', _files=[{'key': 'test1'}], test='blah')
    assert dict(rec) == {
        **DATA,
        'test': 'blah'
    }


def test_files_patch():
    rec = FileRec(DATA)
    with pytest.raises(AttributeError):
        rec.patch([
            {
                'op': 'replace',
                'path': '/_bucket',
                'value': 'invalid'
            }
        ])
    with pytest.raises(AttributeError):
        rec.patch([
            {
                'op': 'replace',
                'path': '/_files',
                'value': 'invalid'
            }
        ])
    nrec = rec.patch([
        {
            'op': 'add',
            'path': '/test',
            'value': 'blah'
        }
    ])
    assert dict(nrec) == {
        **DATA,
        'test': 'blah'
    }
