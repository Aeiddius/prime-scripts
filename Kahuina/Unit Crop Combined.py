import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan,ViewDuplicateOption, BuiltInCategory, ElementTransformUtils, FamilyInstance

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
  return int(''.join(char for char in str if char.isdigit()))



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

class UnitDetail:

  def __init__(self, min, max, pos, exclude=[]):
    self.min = min
    self.max = max
    self.pos = pos
    self.exclude = exclude


prefixes = {
  # "Lighting": "L",
  "Infrastructure": "I",
  # "Device": "DP",
}

range_value = [4, 43]

do_delete = UnwrapElement(IN[0])

# Range which the units appear
matrix = {
  # Level 4A Base
  "01 A-2A": UnitDetail(4, 31, {}),
  "02 A-2B": UnitDetail(4, 31, {}),
  "03 A-2BR": UnitDetail(4, 37, {}),
  "04 A-2AR": UnitDetail(4, 37, {}),
  "05 A-1BR": UnitDetail(4, 35, {}),
  "06 A-1B": UnitDetail(4, 35, {}),
  "07 A-2A": UnitDetail(4, 34, {}),
  "08 A-2B": UnitDetail(4, 34, {}),
  "09 A-2BR": UnitDetail(4, 38, {35: "08", 36: "07", 37: "07", 38: "06"}),
  "10 A-2AR": UnitDetail(4, 38, {35: "09", 36: "08", 37: "08", 38: "07"}),
  "11 A-1AR": UnitDetail(4, 36, {35: "10", 36: "09",}, [32]),
  "12 A-1A": UnitDetail(4, 31, {}),

  # Level 32
  "02 A-2B.1": UnitDetail(32, 32, {}),
  "01 A-3E": UnitDetail(32, 32, {}),

  # Level 33
  "02 A-2D.3": UnitDetail(33, 36, {}),
  "01 A-1C": UnitDetail(33, 36, {}),

  # Level 35
  "07 A-3B": UnitDetail(35, 35, {}),

  # Level 36
  "05 A-3F": UnitDetail(36, 36, {}),
  "06 A-2B.1": UnitDetail(36, 36, {}),

  # Level 37
  "01 A-3D": UnitDetail(37, 39, {}),
  "02 A-2D.1": UnitDetail(37, 39, {}),
  "05 A-3G": UnitDetail(37, 37, {}),
  "06 A-2D.1": UnitDetail(37, 37, {}),

  # Level 38
  "03 A-2BR.1": UnitDetail(38, 38, {}),
  "04 A-3H": UnitDetail(38, 38, {}),
  "05 A-2D.2": UnitDetail(38, 39, {}),

  # Level 39
  "03 A-2DR.1": UnitDetail(39, 39, {}),
  "04 A-3A": UnitDetail(39, 43, {43: "03",}),
  "06 A-3BR": UnitDetail(39, 39, {}),

  # Level 40
  "01 A-3J": UnitDetail(40, 40, {}),
  "02 A-2D": UnitDetail(40, 42, {}),
  "03 A-2DR": UnitDetail(40, 42, {}),
  "05 A-2D": UnitDetail(40, 42, {}),
  "06 A-2BR.2": UnitDetail(40, 40, {}),

  # Level 41
  "01 A-3DR": UnitDetail(41, 43, {}),
  "06 A-2DR": UnitDetail(41, 42, {}),

  # Level 43
  "02 A-3C": UnitDetail(43, 43, {}),
  "04 A-3C": UnitDetail(43, 43, {}),  
}

@transaction 
def start():

  curve_dict = {}
  crop_plans = get_view_range("Utility Views", "Dynamo Crop Plan")
  for crop_view in crop_plans:
    
    filled_region_list = FilteredElementCollector(doc, crop_view.Id).OfClass(FilledRegion).ToElements()
    for filreg in filled_region_list:
      name = filreg.LookupParameter("Comments").AsValueString()
      crop_shape = filreg.GetBoundaries()[0]
      print(name, crop_shape)
      curve_dict[name] = crop_shape


  for target_discipline in prefixes:
    prefix = prefixes[target_discipline]
    target_views = get_view_range("Presentation Views", target_discipline, range_value)
    
    print("Asds")
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
          if level in matrix[unit_name].exclude:
            continue
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
          print("RENAME: ", rename)
          dupli_view.Name = rename

          # Set Grids
          # detail_groups = FilteredElementCollector(doc, base_view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()







start()

OUT = output.getvalue()



