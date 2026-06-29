from stl_treemap.tree_node import TreeNode


class TestGrandparent:
    def test_no_parent(self):
        n = TreeNode()
        assert n.grandparent() is None

    def test_no_grandparent(self):
        p = TreeNode()
        n = TreeNode()
        n.parent = p
        assert n.grandparent() is None

    def test_valid_grandparent(self):
        g = TreeNode()
        p = TreeNode()
        n = TreeNode()
        p.parent = g
        n.parent = p
        assert n.grandparent() is g


class TestSibling:
    def test_no_parent(self):
        n = TreeNode()
        assert n.sibling() is None

    def test_left_sibling(self):
        p = TreeNode()
        n = TreeNode()
        s = TreeNode()
        p.left = s
        p.right = n
        n.parent = p
        s.parent = p
        assert n.sibling() is s

    def test_right_sibling(self):
        p = TreeNode()
        n = TreeNode()
        s = TreeNode()
        p.left = n
        p.right = s
        n.parent = p
        s.parent = p
        assert n.sibling() is s


class TestUncle:
    def test_no_parent(self):
        n = TreeNode()
        assert n.uncle() is None

    def test_no_grandparent(self):
        p = TreeNode()
        n = TreeNode()
        n.parent = p
        assert n.uncle() is None

    def test_valid_uncle(self):
        g = TreeNode()
        p = TreeNode()
        u = TreeNode()
        n = TreeNode()
        n.parent = p
        p.left = n
        p.parent = g
        u.parent = g
        g.left = p
        g.right = u
        assert n.uncle() is u
