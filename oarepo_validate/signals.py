from blinker import signal

before_marshmallow_validate = signal('oarepo_before_marshmallow_validate')
"""
Signal invoked before marshmallow is validated inside Record.validate

:param source:  the record being validated
:param record:  the record being validated
:param context: marshmallow context
:param **kwargs: kwargs passed to Record.validate or Record.commit
"""

after_marshmallow_validate = signal('oarepo_after_marshmallow_validate')
"""
Signal invoked before marshmallow is validated inside Record.validate

:param source:  the record being validated
:param record:  the record that was successfully validated
:param context: marshmallow context
:param result:  result of load that will be used to update record's metadata.
                Signal handler can modify it.
:param **kwargs: kwargs passed to Record.validate or Record.commit
"""

