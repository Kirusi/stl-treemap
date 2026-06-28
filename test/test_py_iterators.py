from stl_treemap.py_iterators import PyIterator, PyReverseIterator


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

    def py_begin(self):
        return 0

    def py_end(self):
        return 5  # one past the last valid value

    def py_rbegin(self):
        return 4

    def py_rend(self):
        return -1  # one before the first valid value


class TestPyIterator:
    def test_forward_iteration(self):
        c = _ContainerStub()
        actual = list(PyIterator(c))
        assert actual == [0, 1, 2, 3, 4]

    def test_backward_iteration_using_forward_iterator(self):
        c = _ContainerStub()
        actual = list(PyIterator(c).backwards())
        assert actual == [4, 3, 2, 1, 0]

    def test_default_value_policy(self):
        c = _ContainerStub()
        it = PyIterator(c)
        assert it.value_policy is c.value_policy

    def test_custom_value_policy(self):
        class DoublePolicy:
            def fetch(self, n):
                return n * 2

        c = _ContainerStub()
        actual = list(PyIterator(c, DoublePolicy()))
        assert actual == [0, 2, 4, 6, 8]

    def test_iter_protocol(self):
        c = _ContainerStub()
        it = PyIterator(c)
        assert iter(it) is it


class TestPyReverseIterator:
    def test_backward_iteration(self):
        c = _ContainerStub()
        actual = list(PyReverseIterator(c))
        assert actual == [4, 3, 2, 1, 0]

    def test_forward_iteration_using_backward_iterator(self):
        c = _ContainerStub()
        actual = list(PyReverseIterator(c).backwards())
        assert actual == [0, 1, 2, 3, 4]

    def test_default_value_policy(self):
        c = _ContainerStub()
        it = PyReverseIterator(c)
        assert it.value_policy is c.value_policy

    def test_custom_value_policy(self):
        class DoublePolicy:
            def fetch(self, n):
                return n * 2

        c = _ContainerStub()
        actual = list(PyReverseIterator(c, DoublePolicy()))
        assert actual == [8, 6, 4, 2, 0]

    def test_iter_protocol(self):
        c = _ContainerStub()
        it = PyReverseIterator(c)
        assert iter(it) is it
