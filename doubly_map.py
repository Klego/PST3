import gc


class Node:

    def __init__(self, key, value, next=None, prev=None):
        self.key = key
        self.value = value
        self.next = next
        self.prev = prev

    def get_value(self):
        return self.value

    def get_key(self):
        return self.key

    def set_value(self, value):
        self.value = value

    def set_key(self, key):
        self.key = key

    def get_next_node(self):
        return self.next

    def set_next_node(self, node):
        self.next = node

    def get_prev_node(self):
        return self.prev

    def set_prev_node(self, node):
        self.prev = node


class DoublyLinkedList:

    def __init__(self, head=None):
        self.head = head
        self.size = 0

    def get_size(self):
        return self.size

    def append(self, key, value):

        new_node = Node(key, value)
        self.size += 1
        last = self.head
        new_node.next = None

        if self.head is None:
            new_node.prev = None
            self.head = new_node
            return

        while last.next is not None:
            last = last.next
        last.next = new_node
        new_node.prev = last

    def find_node(self, key):
        curr = self.head
        while curr:
            if curr.get_key() == key:
                return curr.get_value()
            else:
                curr = curr.get_next_node()
        return False

    def delete_node(self, node):

        if self.head is None or node is None:
            return

        if self.head == node:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev

        if node.prev is not None:
            node.prev.next = node.next
        gc.collect()