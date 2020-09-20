import json
import os

class Database:
    def __init__(self):
        self.folder = os.path.abspath(f'{os.environ["USERPROFILE"]}/AppData/Local/tassomai-automation/')
        self.filename = self.folder + '\\answers.json'

        if not os.path.exists(self.folder): # making sure all the folders exist to avoid errors
            os.makedirs(self.folder)

        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as f:
                data = json.loads('{}')
                json.dump(data, f, indent=3)

    def _test_if_empty(self):
        with open(self.filename) as f:
            try:
                data = json.load(f)
            except:  # if the file is somehow 0 bytes
                with open(self.filename, 'w') as ff:
                    data = json.loads('{}')
                    json.dump(data, ff, indent=3)
                    return True
        return False

    def cached(self, key):
        """
        Check if the question has already been stored.
        """
        empty = self._test_if_empty()
        if empty: return False

        with open(self.filename) as f:
            data = json.load(f)
        if key in data.keys():
            return True
        return False

    def all(self):
        """
        Return the whole database.
        """
        empty = self._test_if_empty()
        if empty: return {}

        with open(self.filename) as f:
            data = json.load(f)

        return data

    def store(self, dictionary):
        """
        Add to the database.
        """
        empty = self._test_if_empty()
        if empty: return {}

        with open(self.filename) as f:
            data = json.load(f)

        for key in dictionary:
            data[key] = dictionary[key]

        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=3)

    def get(self, key):
        with open(self.filename) as f:
            data = json.load(f)
        if not self.cached(key):
            return ""
        return data[key]

class Cache(Database):
    def __init__(self):
        super(Cache, self).__init__()
        self.filename = self.folder + '\\info.json'

        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as f:
                data = json.loads('{}')
                json.dump(data, f, indent=3)
