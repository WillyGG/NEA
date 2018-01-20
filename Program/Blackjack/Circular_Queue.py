class Circular_Queue:
    def __init__(self, size):
        self.__size = size
        self.__circQ = [None for _ in range(self.__size)]
        self.__front = -1
        self.__rear = -1

    @property
    def size(self):
        return self.__size

    def push(self, toPush):
        if self.isFull():
            return False
        if self.isEmpty():
            self.__front += 1

        if self.__rear == (self.__size - 1):
            self.__rear = 0
        else:
            self.__rear += 1

        self.__circQ[self.__rear] = toPush
        return True

    def pop(self):
        if self.isEmpty():
            return False
        toReturn = self.__circQ[self.__front]
        self.__circQ[self.__front] = None

        if self.__front == self.__rear:
            self.__front, self.__rear = -1, -1
        elif self.__front == (self.__size -1):
            self.__front = -1
        else:
            self.__front += 1

    def peek(self):
        return self.__circQ[self.__front]

    def isFull(self):
        noPopCond = self.__front == 0 and self.__rear == (self.__size -1)
        generalCond = self.__front == (self.__rear + 1)
        return noPopCond or generalCond

    def isEmpty(self):
        return self.__front == -1 and self.__rear == -1