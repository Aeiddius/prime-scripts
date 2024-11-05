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


def  level_printer():
  # Get all levels in the document
  collector = FilteredElementCollector(doc).OfClass(Level)
  levels = collector.ToElements()

  for level in levels:
      lvl_name = level.Name
      lvl_id = level.Id.ToString()
      print(f'"{lvl_id}" # {lvl_name}, ')

def  level_sort(target_levels):
  # Get all levels in the document
  collector = FilteredElementCollector(doc).OfClass(Level)
  levels = collector.ToElements()

  # Create a list of level names
  level_names = []
  for level in levels:
      lvl_name = level.Name
      lvl_id = level.Id.ToString()
      if lvl_id in target_levels:
        level_names.append(level)
  return level_names

@transaction
def start():
  base_levels = UnwrapElement(IN[0])
  target_levels = UnwrapElement(IN[1])

  # level_printer()

  levels = level_sort(target_levels)
  print(levels)

start()

OUT = output.getvalue()