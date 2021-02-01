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
        self.length = 0
        self.tail = None

    def get_length(self):
        return self.length

    def __set_length(self, length):
        self.length = length

    def append(self, key, value):

        new_node = Node(key, value)
        self.length += 1
        last = self.head
        new_node.next = None

        if self.head is None:
            new_node.prev = None
            self.head = new_node
            self.tail = new_node
            return

        while last.next is not None:
            last = last.next
        last.next = new_node
        self.tail = new_node
        new_node.prev = last

    def find_node(self, key):
        curr = self.head
        while curr:
            if curr.get_key() == key:
                return curr.get_value()
            else:
                curr = curr.get_next_node()
        return False

    def delete_node_by_key(self, delete):
        if self.head is None:
            return
        elif delete == self.head.key:
            if self.head.next is not None:
                self.head = self.head.next
            else:
                self.head = None
        else:
            current = self.head
            while current is not None:
                if current.key == delete:
                    if current == self.tail:
                        if current.prev is not None:
                            self.tail = current.prev
                    if current.next is not None:
                        current.next.prev = current.prev
                    elif current.prev is not None:
                        current.prev.next = current.next
                else:
                    current = current.next
        length = self.length
        length -= 1
        self.length = length

    def replace(self, key, new_value):
        curr = self.head
        while curr:
            if curr.get_key() == key:
                curr.set_value = new_value
                return True
            else:
                curr = curr.get_next_node()
        return False

    def print_list_key(self):
        if self.head is None:
            return None
        else:
            node = self.head
            while node is not None:
                print(node.key)
                node = node.next

    def get_cursor(self):
        return self.head

    def get_tail(self):
        return self.tail

    def __iter__(self):
        cursor = self.get_cursor()
        if cursor is None:
            return False
        else:
            count = 1
            while cursor is not None and count <= self.length:
                yield cursor.key
                cursor = cursor.next
                count += 1

    def iter_backwards(self):
        cursor = self.get_tail()
        if cursor is None:
            return False
        else:
            count = self.length
            while cursor is not None and count >= 0:
                yield cursor.key
                cursor = cursor.prev
                count -= 1

    def __getitem__(self, item):
        value = self.find_node(item)
        return value

    def __delitem__(self, key):
        self.delete_node_by_key(key)

    def __setitem__(self, key, value):
        self.replace(key, value)

    def __len__(self):
        return self.length
