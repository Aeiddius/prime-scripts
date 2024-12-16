import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,FilledRegion, BuiltInCategory, ElementTransformUtils, FamilyInstance

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

view_type = "Presentation Views"
view_discipline = "Device"

target_id = "1363645"

floor_views = {}

@transaction 
def start():
  base_floor = get_element(target_id)
  cb = base_floor.CropBox

  view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
  for view in view_list:
    if view.IsTemplate == True:
      # print("This is a template: ", view.Name)
      continue

    if not "Dependent " in view.LookupParameter("Dependency").AsValueString():
      continue

    # View Type
    if view.LookupParameter("View Type").AsValueString() != view_type: continue

    # Discipline
    if view.LookupParameter("Type").AsValueString() != view_discipline: continue
    
    primary_view_id = view.GetPrimaryViewId()

    if primary_view_id not in floor_views:
       floor_views[primary_view_id] = []
    
    floor_views[primary_view_id].append(view)

  for floor_id in floor_views:
    main_floor = get_element(floor_id)
    print(main_floor)
    duplicated_plan = ViewPlan.Create(doc, ElementId(1942334) , main_floor.GenLevel.Id) # 1942323 Key Plan Floor type
    duplicated_plan.ViewTEmplateId = ElementId(1942323) # Key Plan View Template

    duplicated_plan.CropBox = main_floor.CropBox
    duplicated_plan.CropBoxActive = True
    duplicated_plan.CropBoxVisible = False

    duplicated_plan.Name = "KEY PLAN " + main_floor.Name.replace("-DP", "").replace("LEVEL", "").strip()
    # for view in view_list[]

    # break

    for view in floor_views[floor_id]:
        boundary = view.GetCropRegionShapeManager()
        crop_shape = boundary.GetCropShape()
        filled_region_id = ElementId(1964523)
        filled_region = FilledRegion.Create(doc, filled_region_id, duplicated_plan.Id, crop_shape)
        filled_region.LookupParameter("Comments").Set(view.Name)
    break
start()
print("\n\n\n")

OUT = output.getvalue()