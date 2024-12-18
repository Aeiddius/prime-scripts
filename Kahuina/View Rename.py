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

view_type = "Utility Views"

# view_discipline = "Electrical"
view_discipline = "Dynamo Copy Plan"
# view_discipline = "Power"


@transaction 
def start():

  view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
  for view in view_list:
    if view.IsTemplate == True:
      # print("This is a template: ", view.Name)
      continue
    # Discipline
    # Discipline
    disci = view.LookupParameter("View Type")
    if disci.AsValueString() != view_type: continue

    # Subdiscipline
    subdisci = view.LookupParameter("Type")
    if subdisci.AsValueString() != view_discipline: continue
    
    if view.Name == "LEVEL 4A Base Crop": continue

    # name = view.Name.split(" ")
    # unity_type = name[2].replace("(", "").strip()

    # unit_nums = list(name[1].strip())
    # new_unit_no = f"{unit_nums[0]}{unit_nums[1]} ({unit_nums[2]}{unit_nums[3]} {unity_type}"

    # new_name = f"Dynamo Crop Unit {new_unit_no}"



    #### Working plan rename
    # if "Level" in view.Name: continue
    # name = view.Name.split(" ")
    # new_id = f"{name[2][0:2]} ({name[2][-2:]} {name[3].replace('(', '')}"
    # new_name = f"{name[0]} {name[1]} {new_id} {name[4]} "


    # suffix = "L"
    # if "-L" in view.Name: continue
    # name = view.Name.split("-")[0].strip()
    # name = f"{name}-{suffix}"
    view.Name = view.Name.replace(" D", "")
    print(view.Name)

start()

OUT = output.getvalue()