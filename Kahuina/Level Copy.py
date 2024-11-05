import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension, ElementTransformUtils

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

@transaction 
def start():
  target_levels = UnwrapElement(IN[1])
  t_level = target_levels[0]
  print(t_level.Id)
  
  # Fliter Groups
  elements = UnwrapElement(IN[0])
  group = []
  for e in elements:
    if isinstance(e, Group):
      group.append(e)
   
   
  # Iterate through groups
  for grp in group:
    grp_elements = grp.GetMemberIds()
    elems = [doc.GetElement(e) for e in grp_elements]
    for e in elems:
      transform = e.Location.Point
      elementId = e.Id
      # params = e.GetParameters()
      # print(params)
      # print(elementId)
      

      copied_id = ElementTransformUtils.CopyElement(doc, elementId, transform)
      copied_instance = doc.GetElement(copied_id[0])
      print(copied_id[0])
      schedule_level = copied_instance.GetParameters("Schedule Level")[0]
      elevation_level = copied_instance.GetParameters("Elevation from Level")[0]
      
      print(schedule_level.AsString())
      print(elevation_level.AsString())
      schedule_level.Set(t_level.Id)
      elevation_level.	SetValueString("1000mm")

      # print(copied_instance)
      # Element.SetParameterByName(copied_instance, "Schedule Level", t_level)

      # copied_instance.Level = t_level

      break
    break

  # print(target_levels)

start()

OUT = output.getvalue()