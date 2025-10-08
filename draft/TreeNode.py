class TreeNode:
    """Small helper node class (kept for compatibility).
    Not used by the new A* implementation but preserved.
    """
    def __init__(self, coord, fx, gx=None):
        self.coord = coord
        self.priority = fx
        self.value_gx = gx if gx is not None else fx
        self.children = []
        self.parent = None

    def get_coord(self):
        return self.coord

    def get_priority(self):
        return self.priority

    def get_value_gx(self):
        return self.value_gx

    def set_parent(self, value):
        self.parent = value

    def get_parent(self):
        return self.parent

    def add_child(self, value):
        self.children.append(value)

    def remove_child(self, value):
        self.children.remove(value)

    def __lt__(self, other):
        return self.priority < other.priority