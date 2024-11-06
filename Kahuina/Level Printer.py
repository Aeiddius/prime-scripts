import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ViewType
from Autodesk.Revit.DB import FilteredElementCollector, Dimension

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, Level

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

def get_element_via_parameter(elements, parameter_name, parameter_value):
    result = []
    for el in elements:
        param_ViewType = el.GetParameters(parameter_name)[0]
        if param_ViewType.AsValueString() == parameter_value:
            result.append(el)
            continue
    return result


def get_all_view_type(elements, view_type):
    result = []
    for el in elements:
        if el.ViewType == view_type:
            result.append(el)
    return result

plan_dict = {
    "Floor Plan": ViewType.FloorPlan,
    "Ceiling Plan": ViewType.CeilingPlan
}

family_dict = {
    "Floor Plan": ViewFamily.FloorPlan,
    "Ceiling Plan": ViewFamily.CeilingPlan
}

to_print = UnwrapElement(IN[0])
elements = UnwrapElement(IN[1])

@transaction
def start():
  target_levels = UnwrapElement(IN[0])

  print(f"To print: {to_print}\n")
  if to_print == "Level":
    # Get all levels in the document
    collector = FilteredElementCollector(doc).OfClass(Level)
    levels = collector.ToElements()

    # Create a list of level names
    for level in levels:
      print(f'"{level.Id.ToString()}", // {level.Name}')

  # Print all plan
  elif to_print == "Plan":
    discipline_type = "Electrical"
    plan_type = "Ceiling Plan"
    elem_discipline = get_element_via_parameter(elements, "Discipline", discipline_type)
    elem_plan = get_all_view_type(elem_discipline, plan_dict[plan_type])
    for plan in elem_plan:
      print(f'"{plan.Id}", // {plan.Name}')


start()

OUT = result
OUT = output.getvalue()