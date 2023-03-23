class Session:
    def __init__(self, id=None):
        self.id = id

    def create_worker(self):
        # Implement this method
        pass

    def instruct(self):
        # Implement this method
        pass

    def call(self):
        # Implement this method
        pass

    def deploy(self):
        # Implement this method
        pass

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value