import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import CurveLoop, DetailLine, XYZ, ViewDuplicateOption, ElementId, Electrical

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


def get_room_curve(group_elements):
  room_curve = CurveLoop()
  for id in group_elements:
    e = doc.GetElement(id)
    if isinstance(e, DetailLine):
      line = e.GeometryCurve
      room_curve.Append(line)
  return room_curve
 

base_view_id = "1581961"
target_views = UnwrapElement(IN[1])


@transaction 
def start():
  base_view = get_element(base_view_id)
  detail_groups = FilteredElementCollector(doc, base_view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()
  curve_dict = {}
  for dg in detail_groups:
    group_elements = dg.GetMemberIds()

    element = get_room_curve(group_elements)
    curve_dict[dg.Name] = element

  for plan_view in target_views:
    for unit_name, curve in curve_dict.items():
      new_plan = plan_view.Duplicate(ViewDuplicateOption.AsDependent)
      dupli_view = doc.GetElement(new_plan)
      dupli_view.CropBoxVisible = False
      print(dupli_view.Name)
      

      import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import CurveLoop, DetailLine, XYZ, ViewDuplicateOption, ElementId, Electrical

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

def get_element(id):
  if isinstance(id, str):
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
      elements.append(doc.GetElement(ElementId(id)))
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
  return int(''.join(char for char in str if char.isdigit()))



def get_room_curve(group_elements):
  room_curve = CurveLoop()
  for id in group_elements:
    e = doc.GetElement(id)
    if isinstance(e, DetailLine):
      line = e.GeometryCurve
      room_curve.Append(line)
  return room_curve
 

class UnitDetail:

  def __init__(self, min, max, pos, typical=False):
    self.min = min
    self.max = max
    self.pos = pos
    self.typical = typical


do_delete = UnwrapElement(IN[0])
target_views = UnwrapElement(IN[1])
prefix = UnwrapElement(IN[2])[0]



# Range which the units appear
matrix = {
  "01 A-2A": UnitDetail(4, 31, {}, True),
  "02 A-2B": UnitDetail(4, 31, {}, True),
  "03 A-2BR": UnitDetail(4, 37, {}, True),
  "04 A-2AR": UnitDetail(4, 37, {}, True),
  "05 A-1BR": UnitDetail(4, 35, {}, True),
  "06 A-1B": UnitDetail(4, 35, {}, True),
  "07 A-2A": UnitDetail(4, 34, {}, True),
  "08 A-2B": UnitDetail(4, 34, {}, True),
  "09 A-2BR": UnitDetail(4, 38, {35: "08", 36: "07", 37: "07", 38: "06"}, True),
  "10 A-2AR": UnitDetail(4, 38, {35: "09", 36: "08", 37: "08", 38: "07"}, True),
  "11 A-1AR": UnitDetail(4, 36, {35: "10", 36: "09",}, True),
  "12 A-1A": UnitDetail(4, 31, {}, True),
  "01 A-3E": UnitDetail(32, 32, {}, True),
  "02 A-2B.1": UnitDetail(32, 32, {}, True),
  "01 A-1C": UnitDetail(33, 36, {}, True),
  "02 A-2D": UnitDetail(33, 36, {}, True),
  "07 A-3B": UnitDetail(35, 35, {}, True),
  "05 A-3F": UnitDetail(36, 36, {}, True),
  "01 A-3D": UnitDetail(37, 39, {}, True),
  "05 A-3G": UnitDetail(37, 37, {}, True),
}

crop_detail_group = [
  # from floor plan id 1581961
  1582090,1582509,1582895,1583204,1583340,1583377,1583416,1583456,1583499,1583535,1583572,1583609,
  1760509, # 01 A-3E
  1771674, # 02 A-2B.1
  1771810, # 01 A-1C
  1783480, # 02 A-2D
  1785457, # 07 A-3B
  1799377, # 05 A-3F
  1834883, # 01 A-3D
  1836240, # 5 A-3G
]

@transaction 
def start():
  base_view = get_element(base_view_id)
  # detail_groups = FilteredElementCollector(doc, base_view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()
  detail_groups = get_elements(crop_detail_group)
  

  curve_dict = {}
  for dg in detail_groups:
    group_elements = dg.GetMemberIds()
    element = ""
    try:
      element = get_room_curve(group_elements)
    except Exception as e:
      print("Error: ", dg.Name)
      raise MyException(f"[{dg.Name}] is broken.\n\n{e}")

    curve_dict[dg.Name] = element

  # Apply copy crop
  for plan_view in target_views:
    # Get level num
    level = get_num(plan_view.Name)

    # Remove dependents
    dependents = plan_view.GetDependentViewIds()
    if dependents:
      for id_dpdt in dependents:
        doc.Delete(id_dpdt)
    if do_delete:
      continue
    for unit_name, curve in curve_dict.items():
      if unit_name not in matrix:
        raise MyException(f"[{unit_name}] is an unaccounted detail group")

      # Only copies within the range
      if matrix[unit_name].min <= level <= matrix[unit_name].max:
        # Duplicate
        new_plan = plan_view.Duplicate(ViewDuplicateOption.AsDependent)
        dupli_view = doc.GetElement(new_plan)
        dupli_view.CropBoxVisible = True
        dupli_view.CropBoxActive = True

        # Set Crop Shape
        crop_manager = dupli_view.GetCropRegionShapeManager()
        crop_manager.SetCropShape(curve)

        # Rename
        rename = ""
        if level in matrix[unit_name].pos:
          type_name = unit_name.split(" ")[1]
          unit_pos = matrix[unit_name].pos[level]
          rename = f"UNIT {level:02d}{unit_pos} {type_name}-{prefix}"
        else:
          rename = f"UNIT {level:02d}{unit_name}-{prefix}"

        dupli_view.Name = rename

        # Set Grids
        # detail_groups = FilteredElementCollector(doc, base_view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()






start()

OUT = output.getvalue()



