import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")


# For Outputting print to watch node
output = StringIO()
sys.stdout = output
result = []
doc = DocumentManager.Instance.CurrentDBDocument

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper
 
def print_member(obj):
  for i in dir(obj):
      print(i)

@transaction
def start():
  target_levels = UnwrapElement(IN[0])

  # Get all levels in the document
  collector = FilteredElementCollector(doc).OfClass(Level)
  levels = collector.ToElements()

  # Create a list of level names
  for level in levels:
      lvl_name = level.Name
      lvl_id = level.Id.ToString()
      if lvl_id in target_levels:
        result.append(level)


start()

OUT = result