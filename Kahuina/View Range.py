import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import CurveLoop, DetailLine, XYZ, View, ElementId, Electrical

clr.AddReference('System')
from System.Collections.Generic import  IList 

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

def get_num(str):
    return int(''.join(char for char in str if char.isdigit()))


filtered_views = []


target_view_type = UnwrapElement(IN[0])
target_discipline = UnwrapElement(IN[1])
range_value = UnwrapElement(IN[2])

min_range = range_value[0]
max_range = range_value[1]

@transaction 
def start():
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
    for view in view_list:
        view_type = view.LookupParameter("View Type").AsValueString()
        if view_type != target_view_type: continue

        discipline = view.LookupParameter("Type").AsValueString()
        if discipline != target_discipline: continue

        level = get_num(view.Name)
        if min_range <= level <= max_range:
            print(view.Name, level)

            filtered_views.append(view)
    # for vt in view_types:
    #     if vt.get_Name() == family_type_name and vt.ViewFamily == view_type:
    #         return vt




start()

# OUT = output.getvalue()
OUT = filtered_views