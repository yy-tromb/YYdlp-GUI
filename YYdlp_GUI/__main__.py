import sys

import os.path
path = os.path.realpath(os.path.abspath(__file__))
print(5,__package__)
print(6,__file__,os.path.abspath(__file__),path)
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
print(9,os.path.dirname(os.path.dirname(path)))
print(10,__name__)

if __package__ is None and not getattr(sys, 'frozen', False):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import YYdlp_GUI

if __name__ == '__main__':
    YYdlp_GUI.main()
