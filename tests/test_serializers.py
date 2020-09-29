import uuid

from invenio_pidstore.minters import recid_minter
from invenio_records import Record

from oarepo_validate import JSONSerializer


def test_serializer(app, db):
    data = {'test': 'blah'}
    record_uuid = uuid.uuid4()
    pid = recid_minter(record_uuid, data)
    rec = Record.create(data, id_=record_uuid)
    serializer = JSONSerializer()
    serialized = serializer.transform_record(pid, rec)
    serialized.pop('created')
    serialized.pop('updated')
    assert serialized == {'id': '1', 'links': {}, 'metadata': {'control_number': '1', 'test': 'blah'}, 'revision': 0}


def test_search_serializer(app, db):
    data = {'test': 'blah'}
    record_uuid = uuid.uuid4()
    pid = recid_minter(record_uuid, data)

    serializer = JSONSerializer()
    serialized = serializer.transform_search_hit(pid, {
        '_source': data,
        '_version': 0,
        '_index': "draft-restoration-restoration-object-v1.0.0-1601321953",
        '_type': "_doc",
        '_id': str(record_uuid),
        '_score': 1,
    })
    serialized.pop('created')
    serialized.pop('updated')
    assert serialized == {'id': '1', 'links': {}, 'metadata': {'control_number': '1', 'test': 'blah'}, 'revision': 0}
