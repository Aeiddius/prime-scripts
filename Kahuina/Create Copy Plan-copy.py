import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan,Level, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import CurveLoop, DetailLine, XYZ, FilledRegion, ElementId, Electrical

clr.AddReference('System')
from System.Collections.Generic import  IList 

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")

class MyException(Exception):
    pass

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

def get_elements(ids):
  elements = []
  if all(isinstance(item, ElementId) for item in ids):
    for id in ids:
      elements.append(doc.GetElement(id))
  if all(isinstance(item, int) for item in ids):
    for id in ids:
      x = doc.GetElement(ElementId(id))
      elements.append(x)
  return elements

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


def get_room_curve(group_elements):
  room_curve = CurveLoop()
  for id in group_elements:
    e = doc.GetElement(id)
    if isinstance(e, DetailLine):
      line = e.GeometryCurve
      room_curve.Append(line)
  return room_curve
 

def get_view_range(target_view_type, target_discipline, range_value=None):
    result = []
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
    for view in view_list:
        view_type = view.LookupParameter("View Type").AsValueString()
        if view_type != target_view_type: continue

        discipline = view.LookupParameter("Type").AsValueString()
        if discipline != target_discipline: continue

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
    # Types
    floor_type = ElementId(1582582)
    view_template = ElementId(3525411)

    # Get levels
    target_levels = [4, 32, 33, 35, 36, 37, 38, 39, 40, 41, 43]
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
    levels = [level for level in levels if get_num(level.Name) in target_levels]

    # iterate through levels to create
    for level in levels:
      ViewPlan.Create()




start()

OUT = output.getvalue()



