from invenio_records_rest.serializers import record_responsify, search_responsify
from invenio_records_rest.serializers.base import TransformerMixinInterface, PreprocessorMixin
from invenio_records_rest.serializers.json import JSONSerializerMixin


class JSONSerializer(JSONSerializerMixin, TransformerMixinInterface, PreprocessorMixin):
    def transform_record(self, pid, record, links_factory=None, **kwargs):
        """Transform record into an intermediate representation."""
        ret = self.preprocess_record(pid, record, links_factory=links_factory, **kwargs)
        if 'pid' in ret:
            ret['id'] = ret.pop('pid').pid_value
        return ret

    def transform_search_hit(self, pid, record_hit, links_factory=None,
                             **kwargs):
        """Transform search result hit into an intermediate representation."""
        ret = self.preprocess_search_hit(pid, record_hit, links_factory=links_factory, **kwargs)
        if 'pid' in ret:
            ret['id'] = ret.pop('pid').pid_value
        return ret

json_serializer = JSONSerializer(replace_refs=False)

json_response = record_responsify(json_serializer, 'application/json')
json_search = search_responsify(json_serializer, 'application/json')

