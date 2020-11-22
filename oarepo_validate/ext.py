from invenio_base.utils import obj_or_import_string
from werkzeug.utils import cached_property
from . import config


class OARepoValidateState:
    """State for record references."""

    def __init__(self, app):
        """Initialize state."""
        self.app = app

    @cached_property
    def merge_function(self):
        return obj_or_import_string(self.app.config['OAREPO_VALIDATE_MERGER'])


class OARepoValidate:
    def __init__(self, app=None, db=None):
        self.init_app(app, db)

    def init_app(self, app, db):
        self.init_config(app, db)
        state = OARepoValidateState(app)
        app.extensions['oarepo-validate'] = state

    def init_config(self, app, db):
        app.config.setdefault('OAREPO_VALIDATE_MERGER', config.OAREPO_VALIDATE_MERGER)
