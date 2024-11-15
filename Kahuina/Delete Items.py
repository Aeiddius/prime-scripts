import clr
import math
from io import StringIO
import sys

import Autodesk
import RevitServices
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Electrical, FilteredElementCollector,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

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
ui_app = DocumentManager.Instance.CurrentUIApplication
app = ui_app.Application

doc = DocumentManager.Instance.CurrentDBDocument


active_view = doc.ActiveView

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper


def gen_transaction(func):
    def wrapper(*args, **kwargs):
            t = Transaction(doc, 'Copy Elements C: Between Projects')
            t.Start()
            func(*args, **kwargs)
            t.Commit()
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

exception_categories = [
  int(BuiltInCategory.OST_RvtLinks),
  int(BuiltInCategory.OST_Grids),
  int(BuiltInCategory.OST_SectionBox),
  int(BuiltInCategory.OST_Cameras),
  int(BuiltInCategory.OST_Elev),
  int(BuiltInCategory.OST_Viewers),
  # int(BuiltInCategory.OST_IOSModelGroups),
]






view_type = ViewType.FloorPlan
# view_type = ViewType.CeilingPlan

view_discipline = "Electrical"
# view_subdiscipline = "Lighting"
view_subdiscipline = "Devices"

lists = ["5A", "6A", "7A", "8A", "9A", "10A", "11A", "12A", "13A", "14A", "15A", "16A", "17A", "18A", "19A", "20A", "21A", "22A", "23A", "24A", "25A", "26A", "27A", "28A", "29A", "30A", "31A", "32A"]

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
    x = view.Name.split("-")[0].split(" ")[1]
    for i in lists:
        if i == x:
          print(view.Name)
          elems = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_IOSModelGroups).ToElements()
          for ed in elems:
              doc.Delete(ed.Id)

start()

OUT = output.getvalue()