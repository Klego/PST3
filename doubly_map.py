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

    def get_length(self):
        return self.length

    def __set_length(self, length):
        self.length = length

    def add(self, key, value):

        new_node = Node(key, value)
        self.length += 1
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

    @staticmethod
    def delete_node(head, delete):

        if head is None or delete is None:
            return None

        if head == delete:
            head = delete.next

        if delete.next is not None:
            delete.next.prev = delete.prev

        if delete.prev is not None:
            delete.prev.next = delete.next

        delete = None
        length = head.get_length()
        length -= 1
        head.set_length(length)
        return head

    def delete_key(self, head, key):
        # if list is empty
        if head is None:
            return None

        current = head

        # traverse the list up to the end
        while current is not None:

            # if node found with the value 'x'
            if current.data == key:

                # save current's next node in the
                # pointer 'next'
                next = current.next

                # delete the node pointed to by
                # 'current'
                head = self.delete_node(head, current)

                # update current
                current = next

            # else simply move to the next node
            else:
                current = current.next

        return head

    def replace(self, key, new_value):
        curr = self.head
        while curr:
            if curr.get_key() == key:
                curr.set_value = new_value
                return True
            else:
                curr = curr.get_next_node()
        return False

    def print_list(self):
        if self.head is None:
            return None
        else:
            node = self.head
            while not node is None:
                print(node.data)
                node = node.next
