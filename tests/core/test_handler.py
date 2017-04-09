"""Tests for cement.core.handler."""

from cement.core import exc, handler, output, meta
from cement.utils import test
from cement.ext import ext_dummy
from cement.ext.ext_configparser import ConfigParserConfigHandler


class BogusOutputHandler(meta.MetaMixin):

    class Meta:
        # interface = IBogus
        label = 'bogus_handler'


class BogusOutputHandler2(meta.MetaMixin):

    class Meta:
        interface = 'output'
        label = 'bogus_handler'


class BogusHandler3(meta.MetaMixin):
    pass


class BogusHandler4(meta.MetaMixin):

    class Meta:
        interface = 'output'
        # label = 'bogus4'


class DuplicateHandler(output.OutputHandler):

    class Meta:
        interface = 'output'
        label = 'dummy'

    def _setup(self, config_obj):
        pass

    def render(self, data_dict, template=None):
        pass


class BogusHandler(handler.Handler):
    pass


class TestHandler(meta.MetaMixin):

    class Meta:
        interface = 'test_interface'
        label = 'test'


class HandlerTestCase(test.CementCoreTestCase):

    def setUp(self):
        super(HandlerTestCase, self).setUp()
        self.app = self.make_app()

    @test.raises(exc.FrameworkError)
    def test_get_invalid_handler(self):
        self.app.handler.get('output', 'bogus_handler')

    @test.raises(exc.InterfaceError)
    def test_register_invalid_handler(self):
        self.app.handler.register(BogusOutputHandler)

    @test.raises(exc.InterfaceError)
    def test_register_invalid_handler_no_meta(self):
        self.app.handler.register(BogusHandler3)

    @test.raises(exc.InterfaceError)
    def test_register_invalid_handler_no_Meta_label(self):
        self.app.handler.register(BogusHandler4)

    @test.raises(exc.FrameworkError)
    def test_register_duplicate_handler(self):
        self.app.handler.register(ext_dummy.DummyOutputHandler)
        try:
            self.app.handler.register(DuplicateHandler)
        except exc.FrameworkError:
            raise

    def test_register_force(self):
        class MyDummy(ext_dummy.DummyOutputHandler):
            pass

        # register once, verify
        self.app.handler.register(ext_dummy.DummyOutputHandler)
        res = self.app.handler.get('output', 'dummy')
        self.eq(res, ext_dummy.DummyOutputHandler)

        # register again with force, and verify we get new class back
        self.app.handler.register(MyDummy, force=True)
        res = self.app.handler.get('output', 'dummy')
        self.eq(res, MyDummy)

    def test_register_force_deprecated(self):
        class MyDummy(ext_dummy.DummyOutputHandler):
            pass

        # register once, verify
        self.app.handler.register(ext_dummy.DummyOutputHandler)
        res = self.app.handler.get('output', 'dummy')
        self.eq(res, ext_dummy.DummyOutputHandler)

        # register again with force, and verify we get new class back
        self.app.handler.register(MyDummy, force=True)
        res = self.app.handler.get('output', 'dummy')
        self.eq(res, MyDummy)

    @test.raises(exc.InterfaceError)
    def test_register_unproviding_handler(self):
        try:
            self.app.handler.register(BogusOutputHandler2)
        except exc.InterfaceError:
            del self.app.handler.__handlers__['output']
            raise

    def test_verify_handler(self):
        self.app.setup()
        self.ok(self.app.handler.registered('output', 'dummy'))
        self.eq(self.app.handler.registered('output', 'bogus_handler'), False)
        self.eq(self.app.handler.registered('bogus_type',
                                            'bogus_handler'), False)

    @test.raises(exc.FrameworkError)
    def test_get_bogus_handler(self):
        self.app.handler.get('log', 'bogus')

    @test.raises(exc.FrameworkError)
    def test_get_bogus_handler_type(self):
        self.app.handler.get('bogus', 'bogus')

    def test_handler_defined(self):
        for handler_type in ['config', 'log', 'argument', 'plugin',
                             'extension', 'output', 'controller']:
            self.eq(self.app.handler.defined(handler_type), True)

        # and check for bogus one too
        self.eq(self.app.handler.defined('bogus'), False)

    def test_handler_list(self):
        self.app.setup()
        handler_list = self.app.handler.list('config')
        res = ConfigParserConfigHandler in handler_list
        self.ok(res)

    @test.raises(exc.FrameworkError)
    def test_handler_list_bogus_type(self):
        self.app.setup()
        self.app.handler.list('bogus')

    @test.raises(exc.FrameworkError)
    def test_define_duplicate_interface(self):
        self.app.handler.define(output.OutputHandlerBase)
        self.app.handler.define(output.OutputHandlerBase)

    def test_handler_not_defined(self):
        self.eq(self.app.handler.defined('bogus'), False)

    def test_handler_registered(self):
        self.app.setup()
        self.eq(self.app.handler.registered('output', 'dummy'), True)

    def test_handler_get_fallback(self):
        self.app.setup()
        self.eq(self.app.handler.get('log', 'foo', 'bar'), 'bar')

    @test.raises(exc.FrameworkError)
    def test_register_invalid_handler_type(self):
        self.app.setup()
        
        class BadHandler(TestHandler):
            class Meta:
                interface = 'bad_interface_not_defined'
        self.app.handler.register(BadHandler)