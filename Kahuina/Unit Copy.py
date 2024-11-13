import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, Group, ElementId, Electrical

clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")


# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
active_view = doc.ActiveView

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

def print_member(obj):
  for i in dir(obj):
      print(i)

def get_element(id_str):
  return doc.GetElement(ElementId(id_str))

exception_categories = [
  int(BuiltInCategory.OST_RvtLinks),
  int(BuiltInCategory.OST_Grids),
  int(BuiltInCategory.OST_SectionBox),
  int(BuiltInCategory.OST_Cameras),
  int(BuiltInCategory.OST_Elev),
  int(BuiltInCategory.OST_Viewers),
  int(BuiltInCategory.OST_Viewers),
  int(BuiltInCategory.OST_IOSModelGroups)
]

proceed = UnwrapElement(IN[0])

units = {
   
}

@transaction 
def start():
  collector = FilteredElementCollector(doc).OfClass(ViewPlan)
  floor_plan_views = [view for view in collector if isinstance(view, ViewPlan) and view.ViewType == ViewType.FloorPlan]

if proceed:
  print("Starting Script")
  start()
else:
  print("Script not enabled")

OUT = output.getvalue()