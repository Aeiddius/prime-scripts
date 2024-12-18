import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, ViewType, XYZ, ViewPlan, ElementId, Electrical

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

def get_element(id):
  if isinstance(id, str) or isinstance(id, int):
    return doc.GetElement(ElementId(id))
  elif isinstance(id, ElementId):
    return doc.GetElement(id)
  return None

def get_element_via_parameter(elements, parameter_name, parameter_value):
    result = []
    for el in elements:
        param_ViewType = el.GetParameters(parameter_name)[0]
        if param_ViewType.AsValueString() == parameter_value:
            result.append(el)
            continue
    return result

view_type = "Presentation Views"

# view_discipline = "Electrical"
view_discipline = "Infrastructure"
# view_discipline = "Power"

target_id = "1581961"

@transaction 
def start():
  base_floor = get_element(target_id)

  view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
  for view in view_list:
    if view.Id.ToString() == target_id: continue
    if view.IsTemplate == True:
      # print("This is a template: ", view.Name)
      continue

    if "Dependent " in view.LookupParameter("Dependency").AsValueString():
        continue

    # Discipline
    disci = view.LookupParameter("View Type")
    if disci.AsValueString() != view_type: continue

    # Subdiscipline
    type = view.LookupParameter("Type")
    if type.AsValueString() != view_discipline: continue


    # view.CropBoxActive = True
    view.CropBoxVisible = False
    # view.CropBox = base_floor.get_CropBox()
    # print(view.Name)
    # break

start()

OUT = output.getvalue() 