"""Tests for cement.core.backend."""

from cement.core import backend
from cement.utils import test

class BackendTestCase(test.CementTestCase):
    def test_defaults(self):
        defaults = backend.defaults('myapp', 'section2', 'section3')
        defaults['myapp']['debug'] = True
        defaults['section2']['foo'] = 'bar'
        self.app = self.make_app('myapp', config_defaults=defaults)
        self.app.setup()
        self.eq(self.app.config.get('myapp', 'debug'), True)
        self.ok(self.app.config.get_section_dict('section2'))
        
    def test_minimal_logger(self):
        log = backend.minimal_logger(__name__)
        log = backend.minimal_logger(__name__, debug=True)
    
        # set logging back to non-debug
        backend.minimal_logger(__name__, debug=False)
        pass