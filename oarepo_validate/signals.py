from blinker import signal

before_marshmallow_validate = signal('oarepo_before_marshmallow_validate')
"""
Signal invoked before record metadata are validated (loaded by marshmallow schema)
inside Record.validate

:param source:  the record being validated
:param record:  the record being validated
:param context: marshmallow context
:param **kwargs: kwargs passed to Record.create or Record.commit (or Record.validate)
"""

after_marshmallow_validate = signal('oarepo_after_marshmallow_validate')
"""
Signal invoked after record metadata are validated (loaded by marshmallow schema)
inside Record.validate

:param source:  the record being validated
:param record:  the record that was successfully validated
:param context: marshmallow context
:param result:  result of load that will be used to update record's metadata.
                Signal handler can modify it.
:param **kwargs: kwargs passed to Record.create or Record.commit (or Record.validate)
"""

