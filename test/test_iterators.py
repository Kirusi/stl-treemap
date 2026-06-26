import pytest

from stl_treemap.iterators import ReverseIterator, TreeIterator


class ContainerStub:
    def prev(self, n):
        return n - 1

    def next(self, n):
        return n + 1


class TestTreeIterator:
    def test_constructor_node_and_container(self):
        c = ContainerStub()
        it = TreeIterator(5, c)
        assert it.node == 5
        assert it.container is c

    def test_constructor_copy_of_iterator(self):
        c = ContainerStub()
        it = TreeIterator(5, c)
        it1 = TreeIterator(it)
        assert it1.node == 5
        assert it1.container is c

    def test_constructor_copy_of_reverse_iterator(self):
        c = ContainerStub()
        it = ReverseIterator(5, c)
        it1 = TreeIterator(it)
        assert it1.node == 6
        assert it1.container is c

    def test_constructor_too_many_parameters(self):
        with pytest.raises(ValueError, match="provided parameters"):
            TreeIterator("test", "test", "test")

    def test_constructor_invalid_copy_request(self):
        with pytest.raises(ValueError) as exc_info:
            TreeIterator("test")
        msg = str(exc_info.value)
        assert "Iterator" in msg
        assert "str" in msg

    def test_next(self):
        c = ContainerStub()
        it = TreeIterator(5, c)
        it.next()
        assert it.node == 6
        assert it.container is c

    def test_prev(self):
        c = ContainerStub()
        it = TreeIterator(5, c)
        it.prev()
        assert it.node == 4
        assert it.container is c


class TestReverseIterator:
    def test_constructor_node_and_container(self):
        c = ContainerStub()
        it = ReverseIterator(5, c)
        assert it.node == 5
        assert it.container is c

    def test_constructor_copy_of_reverse_iterator(self):
        c = ContainerStub()
        it = ReverseIterator(5, c)
        it1 = ReverseIterator(it)
        assert it1.node == 5
        assert it1.container is c

    def test_constructor_copy_of_iterator(self):
        c = ContainerStub()
        it = TreeIterator(5, c)
        it1 = ReverseIterator(it)
        assert it1.node == 4
        assert it1.container is c

    def test_constructor_too_many_parameters(self):
        with pytest.raises(ValueError, match="provided parameters"):
            ReverseIterator("test", "test", "test")

    def test_constructor_invalid_copy_request(self):
        with pytest.raises(ValueError) as exc_info:
            ReverseIterator("test")
        msg = str(exc_info.value)
        assert "ReverseIterator" in msg
        assert "str" in msg

    def test_next(self):
        c = ContainerStub()
        it = ReverseIterator(5, c)
        it.next()
        assert it.node == 4
        assert it.container is c

    def test_prev(self):
        c = ContainerStub()
        it = ReverseIterator(5, c)
        it.prev()
        assert it.node == 6
        assert it.container is c


class TestBaseIterator:
    def test_equals_same_node(self):
        c = ContainerStub()
        it1 = TreeIterator(5, c)
        it2 = TreeIterator(5, c)
        assert it1.equals(it2)
        assert it2.equals(it1)

    def test_equals_different_nodes(self):
        c = ContainerStub()
        it1 = TreeIterator(4, c)
        it2 = TreeIterator(5, c)
        assert not it1.equals(it2)
        assert not it2.equals(it1)

    def test_equals_different_containers(self):
        c1 = ContainerStub()
        c2 = ContainerStub()
        it1 = TreeIterator(4, c1)
        it2 = TreeIterator(5, c2)
        with pytest.raises(ValueError, match="different containers"):
            it1.equals(it2)
        with pytest.raises(ValueError, match="different containers"):
            it2.equals(it1)

    def test_equals_different_iterator_types(self):
        c1 = ContainerStub()
        c2 = ContainerStub()
        it1 = TreeIterator(4, c1)
        it2 = ReverseIterator(5, c2)
        with pytest.raises(ValueError) as exc_info:
            it1.equals(it2)
        msg = str(exc_info.value)
        assert "TreeIterator" in msg
        assert "ReverseIterator" in msg
        with pytest.raises(ValueError) as exc_info:
            it2.equals(it1)
        msg = str(exc_info.value)
        assert "ReverseIterator" in msg
        assert "TreeIterator" in msg

    def test_equals_non_iterator(self):
        c = ContainerStub()
        it = TreeIterator(4, c)
        with pytest.raises(ValueError) as exc_info:
            it.equals("test")
        msg = str(exc_info.value)
        assert "TreeIterator" in msg
        assert "str" in msg
