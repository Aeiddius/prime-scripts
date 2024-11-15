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
  if isinstance(id, str):
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

view_type = ViewType.FloorPlan
view_type = ViewType.CeilingPlan

view_discipline = "Electrical"
# view_subdiscipline = "Infrastructure"
view_subdiscipline = "Lighting"

@transaction 
def start():

  collector = FilteredElementCollector(doc).OfClass(ViewPlan)
  floor_plan_views = [view for view in collector if isinstance(view, ViewPlan) and view.ViewType == view_type]
  for view in floor_plan_views:
    if view.IsTemplate == True:
      print("This is a template: ", view.Name)
      continue
    # Discipline
    disci = view.LookupParameter("Discipline")
    if disci.AsValueString() != view_discipline: continue

    # Subdiscipline
    subdisci = view.LookupParameter("Sub-Discipline")
    if subdisci.AsValueString() != view_subdiscipline: continue

    suffix = "L"

    name = view.Name.split("-")[0].strip()
    name = f"{name}-{suffix}"
    view.Name = name
    # print(name)

start()

OUT = output.getvalue()