import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan, ViewDuplicateOption, BuiltInCategory, ElementTransformUtils, FamilyInstance

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


def get_room_curve(group_elements):
  room_curve = CurveLoop()
  for id in group_elements:
    e = doc.GetElement(id)
    if isinstance(e, DetailLine):
      line = e.GeometryCurve
      room_curve.Append(line)
  return room_curve
 


filtered_views = []



target_discipline = "Power"




info = {
    "Data": ElementId(1583642),
    "Power": ElementId(1583645)
}

@transaction 
def start():
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()

    for view in view_list:
        view_type = view.LookupParameter("View Type").AsValueString()
        if view_type != "Utility Views": continue

        discipline = view.LookupParameter("Type").AsValueString()
        if discipline != "Lighting": continue

        
        
        filtered_views.append(view)

    for view in filtered_views:

        crop_manager = view.GetCropRegionShapeManager()
        shape = crop_manager.GetCropShape()
        print(view.Name, view.GenLevel.Id)

        # Create floor plan
        floor_plan_type = info[target_discipline]
        suffix = target_discipline[0]
        floor_plan = ViewPlan.Create(doc, floor_plan_type, view.GenLevel.Id)
        floor_plan.Name = f"Working {view.Name.replace('UNIT', 'Unit')} {suffix}"

        # Set Values
        floor_plan.LookupParameter("View Type").Set("Working Views")
        floor_plan.LookupParameter("Sub-Discipline").Set(target_discipline)
        floor_plan.LookupParameter("Discipline").Set("Electrical")
        
        # Set Crop Setting
        floor_plan.CropBoxVisible = True
        floor_plan.CropBoxActive = True

        # Set Crop Shape
        floor_plan_crop_manager = floor_plan.GetCropRegionShapeManager()
        floor_plan_crop_manager.SetCropShape(shape[0])

        if view.Name == "LEVEL 4A Base":
            detail_groups = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()
            curve_dict = {}
            for dg in detail_groups:
                if not dg: continue
                group_elements = dg.GetMemberIds()
                element = get_room_curve(group_elements)
                curve_dict[dg.Name] = element
                
            for unit_name, curve in curve_dict.items():
                # Duplicate
                new_plan = floor_plan.Duplicate(ViewDuplicateOption.AsDependent)
                dupli_view = doc.GetElement(new_plan)
                dupli_view.CropBoxVisible = True
                dupli_view.CropBoxActive = True

                # Set Crop Shape
                crop_manager = dupli_view.GetCropRegionShapeManager()
                crop_manager.SetCropShape(curve)


                # Rename
                level = get_num(view.Name)
                rename = f"Working Unit {level:02d} ({unit_name}) {suffix}"
                dupli_view.Name = rename

        # break
start()

OUT = output.getvalue()
# OUT = filtered_views