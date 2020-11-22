OAREPO_VALIDATE_MERGER = 'oarepo_validate.utils.merge'
"""
Merger function for merging partially validated data into stored record.
Must have a signature ``merger(record: Record, data: dict): None`` and
merge the data into the record.

Properties in the record not present in data should be left intact.
"""
