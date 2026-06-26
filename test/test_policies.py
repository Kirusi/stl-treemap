from stl_treemap.policies import KeyOnlyPolicy, KeyValuePolicy, ValueOnlyPolicy
from stl_treemap.tree_node import TreeNode


class TestKeyOnlyPolicy:
    def test_fetch(self):
        p = KeyOnlyPolicy()
        n = TreeNode()
        n.key = "a"
        assert p.fetch(n) == "a"

    def test_copy(self):
        p = KeyOnlyPolicy()
        n_src = TreeNode()
        n_src.key = "a"
        n_dst = TreeNode()
        p.copy(n_dst, n_src)
        assert p.fetch(n_dst) == "a"

    def test_to_string(self):
        p = KeyOnlyPolicy()
        n = TreeNode()
        n.key = "a"
        assert p.to_string(n) == "a"

    def test_to_string_none(self):
        p = KeyOnlyPolicy()
        n = TreeNode()
        assert p.to_string(n) == "None"


class TestValueOnlyPolicy:
    def test_fetch(self):
        p = ValueOnlyPolicy()
        n = TreeNode()
        n.value = "a"
        assert p.fetch(n) == "a"

    def test_copy(self):
        p = ValueOnlyPolicy()
        n_src = TreeNode()
        n_src.value = "a"
        n_dst = TreeNode()
        p.copy(n_dst, n_src)
        assert p.fetch(n_dst) == "a"

    def test_to_string(self):
        p = ValueOnlyPolicy()
        n = TreeNode()
        n.value = "a"
        assert p.to_string(n) == "a"

    def test_to_string_none(self):
        p = ValueOnlyPolicy()
        n = TreeNode()
        assert p.to_string(n) == "None"


class TestKeyValuePolicy:
    def test_fetch(self):
        p = KeyValuePolicy()
        n = TreeNode()
        n.key = 1
        n.value = "a"
        assert p.fetch(n) == (1, "a")

    def test_copy(self):
        p = KeyValuePolicy()
        n_src = TreeNode()
        n_src.key = 1
        n_src.value = "a"
        n_dst = TreeNode()
        p.copy(n_dst, n_src)
        actual_key, actual_value = p.fetch(n_dst)
        assert actual_key == 1
        assert actual_value == "a"

    def test_to_string(self):
        p = KeyValuePolicy()
        n = TreeNode()
        n.key = 1
        n.value = "a"
        assert p.to_string(n) == "1:a"

    def test_to_string_none(self):
        p = KeyValuePolicy()
        n = TreeNode()
        assert p.to_string(n) == "None:None"
