"""
Problem Analysis:
  - Data type required to
  - Behavior: pop, push, peek.
  - Pop: remove top object from stack.
  - Push: Add to top of stack.
  - Peek: "Peek" into the top of the stack
  - Implemented using array, OO solution
  - Last in, first out logic

  - Limited stack size
  - handling if stack is empty
  - no python list methods
  - Implemented in a non-pythonic way - ie no list methods, predefined size, use of pointer etc.
"""

class Stack():
    # Stack stored using an array, of predefined size
    def __init__(self, size = 15):
        self.__size = size
        self.__pointer = -1
        self.__stack = [None for x in range(size)]

    # Getter for stack size
    @property
    def size(self):
        return self.__size

    # Pushes new data to stack
    def push(self, toPush):
        if self.__pointer < self.__size-1:
            self.__pointer += 1
            self.__stack[self.__pointer] = toPush
        else:
            print("Stack is full")

    # Removes top object from stack
    def pop(self):
        if self.__pointer >= 0:
            popped = self.__stack[self.__pointer]
            self.__stack[self.__pointer] = None
            self.__pointer -= 1
            return popped
        else:
            print("Stack is empty")

    # Reveals object at top of stack
    def peek(self):
        if self.__pointer >= 0:
            print(self.__stack[self.__pointer])
        else:
            print("Empty Stack")

    def isEmpty(self):
        return (self.__pointer == -1)

if __name__ == "__main__":
    size = 10
    a = Stack(size)

    # Testing
    a.pop()

    #for x in range(10):
    #    a.push(x)
        #print("peek: ", end="")
        #a.peek()
        #print("pop: " + str(a.pop()))

    for x in range(size):
        a.push(x)

    a.peek()
    a.push(1)

    try:
        print(a.stack)
    except AttributeError as e:
        print("your stuff works")
