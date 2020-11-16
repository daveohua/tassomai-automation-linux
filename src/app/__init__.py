import os

__title__ = 'app'
__author__ = 'Gloryness'
__license__ = 'MIT License'
__version__ = '1.0.7'
__module__ = os.getcwd()

if not __module__.endswith(("app\\__init__.py", "app/__init__.py")):
    __module__ = __module__+'\\'
    is_executable = True
else:
    __module__ = __module__.replace("app\\__init__.py", "").replace("app/__init__.py", "").replace("/", "\\")
    is_executable = False

path = lambda *p: __module__+'\\'.join(p)