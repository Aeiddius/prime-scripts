import clr
import math, sys
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet,Viewport, BuiltInCategory, ElementTransformUtils, FamilyInstance

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

def get_num(str):
  res = ''.join(char for char in str if char.isdigit())
  if res:
    return int(res)
  else: return None
def is_dependent(view):
  if "Dependent " in view.LookupParameter("Dependency").AsValueString():
    return True
  return False
def get_view_range(view_group, target_view_type, target_family_type, range_value=None):
    result = []
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
    for view in view_list:
        if view.IsTemplate == True: continue

        
        if view.LookupParameter("View Group").AsValueString() != view_group: continue

        if view.LookupParameter("View Type").AsValueString() != target_view_type: continue

        if view.LookupParameter("Type").AsValueString() != target_family_type: continue

        if range_value:
          min_range = range_value[0]
          max_range = range_value[1]

          level = get_num(view.Name)
          if min_range <= level <= max_range:
              result.append(view)
              continue
          
        else:
          result.append(view)
          continue
          
    return result


@transaction 
def start():
  view_list = get_view_range("Tower A", "Presentation Views", "Lighting")
  titleblock_id = ElementId(1941401)
  
  for view in view_list:
    if not is_dependent(view): continue

    level = view.GenLevel.Name


    print(get_element(view.GetPrimaryViewId()).Name, view.Name)
    new_sheet = ViewSheet.Create(doc, titleblock_id)
    new_sheet.LookupParameter("Sheet Group").Set("Unit Plan")
    new_sheet.LookupParameter("Sheet Type").Set(level)

    name = view.Name.replace("UNIT ", "")
    # break


    # new_sheet.LookupParameter("Sheet Sub-Type").Set("0402 A-2A")

start()

OUT = output.getvalue()