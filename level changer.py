import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, ViewPlan, ElementId, Electrical

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

def get_element_via_parameter(elements, parameter_name, parameter_value):
    result = []
    for el in elements:
        param_ViewType = el.GetParameters(parameter_name)[0]
        if param_ViewType.AsValueString() == parameter_value:
            result.append(el)
            continue
    return result


@transaction 
def start():
  exception_categories = [
    int(BuiltInCategory.OST_ConduitCenterLine),   # Detail components
    int(BuiltInCategory.OST_Grids),              # Grids
    int(BuiltInCategory.OST_Levels),             # Levels
    int(BuiltInCategory.OST_RvtLinks),           # Revit links
    int(BuiltInCategory.OST_Views),              # Views
    int(BuiltInCategory.OST_Sections),           # Section views
    int(BuiltInCategory.OST_Elev),   # Elevation markers
    int(BuiltInCategory.OST_TextNotes),          # Text notes
    int(BuiltInCategory.OST_Dimensions),         # Dimensions
    int(BuiltInCategory.OST_Tags),               # Tags
    int(BuiltInCategory.OST_Sheets)   
  ]

  collector = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
  # filtered = [e for e in collector if e and e.Category.Id.IntegerValue not in exception_categories ]

  x = 0
  for i in collector:
      if not i: continue
      x+=1
      if x == 13: break
      print(i)
  
start()  

OUT = output.getvalue()