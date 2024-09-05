import clr
import math
import sys
import re

from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import CurveLoop, ElementId, BuiltInCategory, FilteredElementCollector
from Autodesk.Revit.DB import ViewPlan, CurveLoop
from Autodesk.Revit.DB import DetailLine , ViewType
from Autodesk.Revit.DB.Architecture import Room

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import ViewDuplicateOption, Line, ViewFamily

 
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')
# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument


def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

def print_member(obj):
    for i in dir(obj):
        print(i)

def set_view_crop(view, curve):
    crop_manager = view.GetCropRegionShapeManager()
    crop_shape = crop_manager.GetCropShape()[0]
    crop_manager.SetCropShape(curve)

def get_room_curve(group_elements):
    room_curve = CurveLoop()
    for id in group_elements:
        e = doc.GetElement(id)
        if isinstance(e, DetailLine):
            line = e.GeometryCurve
            room_curve.Append(line)
    return room_curve
 
def duplicate_view(view, name):
    newId = view.Duplicate(ViewDuplicateOption.AsDependent)
    newView = doc.GetElement(newId)
    newView.CropBoxVisible = False
    newView.Name = name
    return newView

def get_model_groups(base_view_id):
    detail_groups = FilteredElementCollector(doc, base_view_id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()
    return detail_groups

def get_model_curves(groups):
    curve_dict = {}
    for group in groups:
        group_elements = group.GetMemberIds()
        element = get_room_curve(group_elements)
        curve_dict[group.Name] = element
    return curve_dict

def create_unit_views(view, room_curve, group_name, num, prefix):
    # group_elements = group.GetMemberIds()

    # # Extract Room and Room Curve
    # room_curve = get_room_curve(group_elements)


    # Duplicate View as dependent
    newName = prefix + "-" + group_name.replace("04", num, 1)
    newView = duplicate_view(view, newName)

    # Set view crop
    set_view_crop(newView, room_curve)

def get_number_list(views):
    result = []
    for view in views:
        num = re.sub(r'\D', '', view.Name).strip()
        if num:
            result.append(num)
    return result

def get_only_range(views, range):
    range_min = range[0]
    range_max = range[1]

    accepted_views = []
    for view in views:
        num = re.sub(r'\D', '', view.Name).strip()
        num_int = int(num)
        if num_int < range_min or num_int > range_max: continue
        accepted_views.append([view, num])
    return accepted_views

@transaction
def start():
    views = UnwrapElement(IN[0])
    range = UnwrapElement(IN[2])
    prefix = UnwrapElement(IN[3])
    
    base_view_id = ElementId(UnwrapElement(IN[1]))    
    model_detail_group = get_model_groups(base_view_id)
    # model_curves = get_model_curves(model_detail_group)


    # view_range = get_only_range(views, range)
    # for view_group in view_range:
    #     view = view_group[0]
    #     num = view_group[1]
    #     for group_name, curve in model_curves.items():
    #         print(view, curve, group_name, num)
    #         create_unit_views(view, curve, group_name, num, prefix)



start()

OUT = output.getvalue()


