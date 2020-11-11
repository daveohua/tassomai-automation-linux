
__title__ = 'app'
__author__ = 'Gloryness'
__license__ = 'MIT License'

path = __file__
if not path.endswith(("app\\__init__.py", "app/__init__.py")):
    path = ""
else:
    path = path.replace("app\\__init__.py", "").replace("__init__.py", "").replace("\\", "/")