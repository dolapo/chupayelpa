import os
import site
import sys

environment = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(environment, '../third_party'))
sys.path.insert(0, os.path.join(environment, '../third_party/tornado'))
