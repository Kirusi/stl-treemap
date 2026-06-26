from stl_treemap.js_iterators import JsIterator, JsReverseIterator


class _NodeIsValuePolicy:
    def fetch(self, n):
        return n


class _ContainerStub:
    """Stub container whose 'nodes' are plain integers in the range 0..4."""

    def __init__(self):
        self.value_policy = _NodeIsValuePolicy()

    def prev(self, n):
        return n - 1

    def next(self, n):
        return n + 1

    def js_begin(self):
        return 0

    def js_end(self):
        return 5  # one past the last valid value

    def js_rbegin(self):
        return 4

    def js_rend(self):
        return -1  # one before the first valid value


class TestJsIterator:
    def test_forward_iteration(self):
        c = _ContainerStub()
        actual = list(JsIterator(c))
        assert actual == [0, 1, 2, 3, 4]

    def test_backward_iteration_using_forward_iterator(self):
        c = _ContainerStub()
        actual = list(JsIterator(c).backwards())
        assert actual == [4, 3, 2, 1, 0]

    def test_default_value_policy(self):
        c = _ContainerStub()
        it = JsIterator(c)
        assert it.value_policy is c.value_policy

    def test_custom_value_policy(self):
        class DoublePolicy:
            def fetch(self, n):
                return n * 2

        c = _ContainerStub()
        actual = list(JsIterator(c, DoublePolicy()))
        assert actual == [0, 2, 4, 6, 8]

    def test_iter_protocol(self):
        c = _ContainerStub()
        it = JsIterator(c)
        assert iter(it) is it


class TestJsReverseIterator:
    def test_backward_iteration(self):
        c = _ContainerStub()
        actual = list(JsReverseIterator(c))
        assert actual == [4, 3, 2, 1, 0]

    def test_forward_iteration_using_backward_iterator(self):
        c = _ContainerStub()
        actual = list(JsReverseIterator(c).backwards())
        assert actual == [0, 1, 2, 3, 4]

    def test_default_value_policy(self):
        c = _ContainerStub()
        it = JsReverseIterator(c)
        assert it.value_policy is c.value_policy

    def test_custom_value_policy(self):
        class DoublePolicy:
            def fetch(self, n):
                return n * 2

        c = _ContainerStub()
        actual = list(JsReverseIterator(c, DoublePolicy()))
        assert actual == [8, 6, 4, 2, 0]

    def test_iter_protocol(self):
        c = _ContainerStub()
        it = JsReverseIterator(c)
        assert iter(it) is it
