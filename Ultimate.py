import clr
import math
import re

from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import CurveLoop, ElementId, ViewFamilyType, BoundingBoxXYZ
from Autodesk.Revit.DB import ViewPlan, ViewPlacementOnSheetStatus, ForgeTypeId
from Autodesk.Revit.DB import ViewType
from Autodesk.Revit.DB.Architecture import Room

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import ViewDuplicateOption, FilteredElementCollector, ViewFamily


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


def get_all_non_sheet(elements):
    result = []
    for el in elements:
        
        sheet_status = el.GetPlacementOnSheetStatus()
        if sheet_status == ViewPlacementOnSheetStatus.NotApplicable:
            result.append(el)
        if sheet_status == ViewPlacementOnSheetStatus.NotPlaced:
            result.append(el)
        if sheet_status == ViewPlacementOnSheetStatus.PartiallyPlaced:
            continue
        if sheet_status == ViewPlacementOnSheetStatus.CompletelyPlaced:
            continue
    return result

def clean_view_list(elements, exclude_name):
    result = []
    exn = [name + "-U" for name in exclude_name]
    for el in elements:
        if el.Name in exn: continue
        if "-" not in el.get_Name():
            continue
        result.append(el)
    return result

def get_elementType(doc, family_type_name, view_type):
    view_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    for vt in view_types:
        if vt.get_Name() == family_type_name and vt.ViewFamily == view_type:
            return vt
    return None

def set_viewfamily_type(element, family_type):
    param_ViewType = element.GetParameters("Type")[0]
    param_ViewType.Set(family_type.Id)


def duplicate_view(element, name, family_type):
    newId = element.Duplicate(ViewDuplicateOption.Duplicate)
    dupli_element = doc.GetElement(newId)
    dupli_element.CropBoxVisible = False
    dupli_element.Name = name
    
    set_viewfamily_type(dupli_element, family_type)

    return dupli_element

def contains_number_regex(s):
    return bool(re.search(r'\d', s))

def _get_all_unit_views(elements):
    unit_plans = []
    for el in elements:
        if not el.Name.endswith("-U"): continue
        if "-B-" in el.Name: continue # Remove Building B
        if not contains_number_regex(el.Name): continue
        unit_plans.append(el)
    return unit_plans


def duplicate_view(view, name):
    newId = view.Duplicate(ViewDuplicateOption.AsDependent)
    newView = doc.GetElement(newId)
    newView.CropBoxVisible = False
    newView.Name = name
    return newView

plan_dict = {
    "Floor Plan": ViewType.FloorPlan,
    "Ceiling Plan": ViewType.CeilingPlan
}

family_dict = {
    "Floor Plan": ViewFamily.FloorPlan,
    "Ceiling Plan": ViewFamily.CeilingPlan
}

elements = UnwrapElement(IN[0])
view_group = UnwrapElement(IN[1])
discipline = UnwrapElement(IN[2])
plan_type = UnwrapElement(IN[3])
base_view_name = UnwrapElement(IN[4])
family_type = UnwrapElement(IN[5])
# family_type = f"{discipline} Unit Plan"

isDuplicateOn = UnwrapElement(IN[6])

processed_elements = []

@transaction
def start():
    global processed_elements
    # view_types = FilteredElementCollector(doc).OfClass(Views).ToElements()
    
    elem_present = get_element_via_parameter(elements, "View Type", view_group)

    elem_discipline = get_element_via_parameter(elem_present, "Discipline", discipline)

    elem_floorplan = get_all_view_type(elem_discipline, plan_dict[plan_type])

    elem_non_sheet = get_all_non_sheet(elem_floorplan)

    elem_cleaned = clean_view_list(elem_non_sheet, base_view_name)

    view_family_type = get_elementType(doc, family_type, family_dict[plan_type])
    
    unit_plans = _get_all_unit_views(elem_non_sheet)
    if isDuplicateOn:
        print("Duplicate is turned on.")
        for el in elem_cleaned:
            viewplan_name = el.get_Name()
            if viewplan_name in base_view_name: continue
            print(viewplan_name)
            duplicate_view(el, viewplan_name + "-U", view_family_type)
    else:
        print("Duplicate is turned off.")

    processed_elements = unit_plans

start()

OUT = [output.getvalue(), processed_elements]


