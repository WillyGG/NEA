from Stack import Stack

class Tower(Stack):
    def __init__(self, left_tower = False):
        super().__init__(3)
        if left_tower:
            for x in range(3, 0, -1):
                self.push(x)

    def move(self, next_tower):
        self_top = self.peek()
        next_top = next_tower.peek()
        if next_top == None or next_top < self_top:
            next_tower.push(self.pop())
        
    

tower1 = Stack(3)
tower2 = Stack(3)
tower3 = Stack(3)
