class ImageStack:  # 创建一个栈
    def __init__(self):  # 初始为空栈
        self.items = []

    def clear(self):
        self.items.clear()

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def top(self):
        return self.items[-1]

    def size(self):
        return len(self.items)
