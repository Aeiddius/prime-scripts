import clr
import math
from io import StringIO
from pprint import pprint
import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory , ViewDuplicateOption,FilledRegion, CopyPasteOptions, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, OverrideGraphicSettings , XYZ, ViewPlan, ElementId, Transform
from System.Collections.Generic import List

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


def is_dependent(view):
  if "Dependent " in view.LookupParameter("Dependency").AsValueString():
    return True
  return False


# Variables
# Source Variable where the views where the key plan will use as basis 
view_Group = "Tower A"
target_view_type = "Presentation Views"
target_family_type = "Lighting"
remove_prefix = "-L"
# The view where the text 01 02 03 are placed for all.
master_text_view = 1942310 

# Functions
@transaction 
def start_delete():
  # Delete
  original_views = get_view_range(view_Group, "Key Plan", "Key Plan")
  for i in original_views:
    try:
      doc.Delete(i.Id)
    except Exception as e:
      print(f"Error: {e}")

@transaction 
def start_generate_views():
  # Get Key plan data
  floor_views = {}
  view_list = get_view_range(view_Group, target_view_type, target_family_type)

  for view in view_list:
    if not is_dependent(view):
       floor_views[view.Id] = []
       continue
    
    floor_views[view.GetPrimaryViewId()].append(view)


 
  # Text Notes
  text_view = get_element(master_text_view)
  text_notes = FilteredElementCollector(doc, text_view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()

  text_notes_dict = {}
  for textn in text_notes:
    key = get_num(textn.Name)
    text_notes_dict[key] = textn

  # Create key plans
  for floor_id in floor_views:
    main_floor = get_element(floor_id)
    level = get_num(main_floor.Name)

    if level in [1,2,3]: continue
    duplicated_plan = ViewPlan.Create(doc, ElementId(1942334) , main_floor.GenLevel.Id) # 1942323 Key Plan Floor type
    duplicated_plan.ViewTEmplateId = ElementId(1942323) # Key Plan View Template

    duplicated_plan.CropBox = main_floor.CropBox
    duplicated_plan.CropBoxActive = True
    duplicated_plan.CropBoxVisible = False

    duplicated_plan.Name = "KEY PLAN " + main_floor.Name.replace(remove_prefix, "").replace("LEVEL", "").strip()
  
    duplicated_plan.LookupParameter("View Group").Set(view_Group)

    # Copy the text
    copied_ids = ElementTransformUtils.CopyElements(
      text_view, 
      List[ElementId]([text_notes_dict[level].Id]),
      duplicated_plan, 
      Transform.Identity,
      CopyPasteOptions()
    )

    # Create filled region
    for view in floor_views[floor_id]:
        boundary = view.GetCropRegionShapeManager()
        crop_shape = boundary.GetCropShape()
        filled_region_id = ElementId(1964523)
        filled_region = FilledRegion.Create(doc, filled_region_id, duplicated_plan.Id, crop_shape)
        filled_region.LookupParameter("Comments").Set(view.Name.replace("UNIT", "KP").replace(remove_prefix, ""))

@transaction 
def start_generate_subkp():
  view_list = get_view_range(view_Group, "Key Plan", "Key Plan")
  for keyplan_view in view_list:
    if is_dependent(keyplan_view): continue

    print(keyplan_view.Name)

    # Get Filled Region
    filled_reg = FilteredElementCollector(doc, keyplan_view.Id).OfClass(FilledRegion).ToElements()
    filreg_dict = {}
    for freg in filled_reg:
        name = freg.LookupParameter("Comments").AsValueString()
        filreg_dict[name] = freg.Id

    # Get Text Notes
    text_notes = FilteredElementCollector(doc, keyplan_view.Id).OfCategory(BuiltInCategory.OST_TextNotes).ToElements()

    # Iterate through every filled region unit in a plan view
    for freg in filreg_dict:
      to_hide = List[ElementId]([filreg_dict[i] for i in filreg_dict if i != freg])
      unit_no = freg.split(" ")[1][2:4]

      # Duplicate dependent views
      for prefix in ["DP", "L", "KB"]:
        dupli_id = keyplan_view.Duplicate(ViewDuplicateOption.AsDependent)
        dupli_view = get_element(dupli_id)
        dupli_view.Name = f"{freg}-{prefix}"
        dupli_view.HideElements(to_hide)
        dupli_view.CropBoxVisible = False

        # Half-tone other units
        for textn in text_notes:
          text = textn.Text.strip()
          if text == unit_no: continue
          override = OverrideGraphicSettings()
          override.SetHalftone(True)
          dupli_view.SetElementOverrides(textn.Id, override)

    # break
start_delete()
start_generate_views()
start_generate_subkp()

OUT = output.getvalue()