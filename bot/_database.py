
class RedisDb:
    def __init__(redis_client):
        self.db = redis_client

    def get(self, key):
        try:
            return eval(self.db.get(str(key)))
        except:
            return self.db.get(str(key))

    def set(self, key, value):
        return self.db.set(str(key), str(value))

    def delete(self, key):
        return self.db.delete(str(key))
