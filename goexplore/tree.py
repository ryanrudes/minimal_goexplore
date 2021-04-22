class TreeNode:
    def __init__(self, root, code, action):
        self.root = root
        self.action = action
        self.children = {}

    def add(self, action, code):
        node = TreeNode(self, code, action)
        self.children[action] = node
        return node

    def has(self, action):
        return action in self.children

    def get(self, action):
        return self.children[action]

class LinkedTree:
    def __init__(self, root_code):
        self.root = TreeNode(None, root_code, None)
        self.node = self.root

    def act(self, action, code):
        if self.node.has(action):
            self.node = self.node.get(action)
        else:
            self.node = self.node.add(action, code)

    def set(self, node):
        self.node = node

    def get_trajectory(self):
        temp = self.node
        trajectory = []
        while not temp.action is None:
            trajectory.append(temp.action)
            temp = temp.root
        return trajectory
