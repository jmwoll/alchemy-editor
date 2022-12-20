
class DragNDrop:
    def __init__(self) -> None:
        self.clear()

    def at_start(self):
        return self.start_x is None

    def pending(self):
        return not self.at_start()

    def ready_to_commit(self):
        return all([self.start_x,self.end_x,self.start_y,self.end_y,])

    def clear(self):
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
