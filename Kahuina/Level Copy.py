import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, Group


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

def copy_to_level(element, target_level):
  transform = XYZ(0, 0, 0)
  elementId = element.Id

  copied_id = ElementTransformUtils.CopyElement(doc, elementId, transform)
  copied_instance = doc.GetElement(copied_id[0])

  print("ID: ", copied_id[0])
  reference_level = copied_instance.GetParameters("Reference Level")[0]
  reference_level.Set(target_level.Id)


proceed = UnwrapElement(IN[0])
elements = UnwrapElement(IN[1])
target_plans = UnwrapElement(IN[2])
target_levels = UnwrapElement(IN[3])


@transaction 
def start():
  t_level = target_levels[0] # Temporary
  print(t_level.Id)
  
  # Fliter Groups
  for e in elements:
    if isinstance(e, Group):
      copy_to_level(e, t_level)



      # collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory. OST_GenericAnnotation) \
      #                                            .WhereElementPropertyEquals(BuiltInParameter.LEVEL_PARAM, t_level.Id)
      # # elems = [e for e in e.GetMemberIds() if isinstance(doc.GetElement(e), IndependentTag)]
      
      # print(collector)
      # # for  i in e.GetMemberIds():
      # #   a = doc.GetElement(i)
      # #   print(a.Name)


    break
  
   
if proceed:
  print("Starting Script")
  start()
else:
  print("Script not enabled")

OUT = output.getvalue()