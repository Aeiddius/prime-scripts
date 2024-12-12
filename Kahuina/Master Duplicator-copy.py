import clr
import math
import re
from io import StringIO
import time

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewPlan, Transform, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import CurveLoop, DetailLine, IndependentTag, FamilyInstance, MEPSystem, ElementId, CopyPasteOptions
from Autodesk.Revit.DB.Electrical import ElectricalEquipment, ElectricalSystem
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


def get_view_range(target_view_type, target_plan_type):
    filtered_list = []
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()

    for view in view_list:

        view_type = view.LookupParameter("View Type").AsValueString()
        if view_type != target_view_type: continue

        plan_type = view.LookupParameter("Type").AsValueString()
        if plan_type != target_plan_type: continue

        filtered_list.append(view)
    return filtered_list


def filter_source_elements(base_view):
    exception_categories = [
        int(BuiltInCategory.OST_RvtLinks),
        int(BuiltInCategory.OST_Grids),
        int(BuiltInCategory.OST_SectionBox),
        int(BuiltInCategory.OST_Cameras),
        int(BuiltInCategory.OST_Elev),
        int(BuiltInCategory.OST_Viewers),
        # int(BuiltInCategory.OST_IOSModelGroups)
        ]

    elements_source = FilteredElementCollector(doc, base_view.Id).WhereElementIsNotElementType().ToElements()
    filtered_elements = []
    added_ids = []
    
    # Filter Elements
    group_count = 0
    for e in elements_source:
        # skip weird shit that does not have a category.
        category = e.Category
        if not category: continue

        # skip banned categories
        if not category or (category and category.Id.IntegerValue in exception_categories):
            continue

        # Add model groups containing 3d models
        if category.Id.IntegerValue == int(BuiltInCategory.OST_IOSModelGroups):
            # print(f"Group {group_count}: ", e.Name)
            # Gets the instances inside the model group
            ids = e.GetMemberIds()
            for id in ids:
                grp_elem = get_element(id)
                filtered_elements.append(grp_elem)
                added_ids.append(grp_elem.Id)

                # Get Electrical System
                if isinstance(grp_elem, FamilyInstance) and grp_elem.MEPModel:
                    elec_system = grp_elem.MEPModel.GetElectricalSystems().GetEnumerator()
                    for j in elec_system:
                        if j.Id not in added_ids:
                            filtered_elements.append(j)
                            added_ids.append(j.Id)
                            
            group_count += 1
            continue
        
        # Add panels
        if isinstance(e, FamilyInstance) and isinstance(e.MEPModel, ElectricalEquipment):
            # print("Included: ", e.Name, " ", e.Id)
            filtered_elements.append(e)
            continue
        
        # Skip circuits since we added it already
        if isinstance(e, ElectricalSystem):
            continue
        
        # Filter out Switch systems
        if isinstance(e, MEPSystem):
            if (e.BaseEquipment):
                if e.BaseEquipment.Id in added_ids and e not in filtered_elements:
                    filtered_elements.append(e)
            continue

        # add anything else extra
        filtered_elements.append(e)
        added_ids.append(e.Id)


    return filtered_elements




class UnitDetail:

  def __init__(self, min, max, pos, typical=False):
    self.min = min
    self.max = max
    self.pos = pos
    self.typical = typical

class Source:

    def __init__(self, view, elements, ):
        self.elements = list(set(elements))
        self.elements_id = [e.Id for e in self.elements]
        self.sview = view
        self.elements_list = List[ElementId](self.elements_id)




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
  "01 A-3E": UnitDetail(32, 32, {}),
  "02 A-2B.1": UnitDetail(32, 32, {}),
  "01 A-1C": UnitDetail(33, 36, {}),
  "02 A-2D": UnitDetail(33, 42, {}),
  "07 A-3B": UnitDetail(35, 35, {}),
  "05 A-3F": UnitDetail(36, 36, {}),
  "01 A-3D": UnitDetail(37, 39, {}),
  "05 A-3G": UnitDetail(37, 37, {}),
  "03 A-2BR.1": UnitDetail(38, 38, {}),
  "04 A-3H": UnitDetail(38, 38, {}),
  "04 A-3A": UnitDetail(39, 43, {43: "03",}),
  "06 A-3BR": UnitDetail(39, 39, {}),
  "01 A-3J": UnitDetail(40, 40, {}),
  "06 A-2BR.2": UnitDetail(40, 40, {}),
  "01 A-3DR": UnitDetail(41, 43, {}),
  "03 A-2DR": UnitDetail(39, 42, {}),
  "02 A-3C": UnitDetail(43, 43, {}),
  "04 A-3C": UnitDetail(43, 43, {}),
  "06 A-2D": UnitDetail(37, 42, {38: "05", 39: "05",  40: "05", 41: "05", 42: "05"}),
  "06 A-2B.1": UnitDetail(36, 36, {}),
}


target_discipline = "Lighting"

filtered_views = []
unit_source = {}




@transaction
def start():
    # delete group models with DYNAMOSCRIPTMODEL name
    

    # Get source views
    st_a1 = time.perf_counter()
    source_views = get_view_range("Utility Views", "Dynamo Copy Plan")
    for view in source_views:
        if "Level 4A" in view.Name: continue
        
        unit_name = re.search(r"\((.*?)\)", view.Name).group(1)
        filtered_elements = filter_source_elements(view)

        if "Dependent " in view.LookupParameter("Dependency").AsValueString():
            unit_source[unit_name] = Source(get_element(view.GetPrimaryViewId()), filtered_elements)
        else:
            unit_source[unit_name] = Source(view, filtered_elements)

    # Get Target views in a neat dictionary
    # target_views = get_view_range("Presentation Views", "Lighting")
    target_views = get_view_range("Utility Views", "Dynamo Target Plan")
    target_source = {}
    for tview in target_views:
        if "Dependent " in tview.LookupParameter("Dependency").AsValueString():
            continue
        level = get_num(tview.Name)
        target_source[level] = tview


    floor_elements = {}

    # iterates through units and paste them
    for unit in unit_source:
        unit_matrix = matrix[unit]
        min_lvl = unit_matrix.min + 1
        max_lvl = unit_matrix.max

        for tgtv in target_source:
            if tgtv not in floor_elements:
                floor_elements[tgtv] = []

            if min_lvl <= tgtv <= max_lvl:
                floor_elements[tgtv].append(unit_source[unit])
    st_a2 = time.perf_counter()
    print(f"Setup time: {st_a2-st_a1} seconds.")
    
    count = 0

    # Iterates through each floor to paste their content
    start_time = time.perf_counter()
    for floorelem in floor_elements:

        floor_start_time = time.perf_counter()
        if not floor_elements[floorelem]: continue

        divided_by_source = {}
        for unit_src in floor_elements[floorelem]:
            view_id = unit_src.sview.Id.ToString()
            if view_id not in divided_by_source:
                divided_by_source[view_id] = []
            divided_by_source[view_id] += unit_src.elements_id
        
        print(floorelem, len(divided_by_source.keys()))

        pasted_elements = []
        for view_id in divided_by_source:
            copied_ids = ElementTransformUtils.CopyElements(
                get_element(view_id), 
                List[ElementId](divided_by_source[view_id]), 
                target_source[floorelem], 
                Transform.Identity,
                CopyPasteOptions()
            )
            pasted_elements += copied_ids

            # Set Element elevation
            copied_elements = [get_element(cid) for cid in copied_ids]
            for celem in copied_elements:
                if isinstance(celem, FamilyInstance): 
                    parameter = celem.LookupParameter("Schedule Level")
                    if parameter and not parameter.IsReadOnly:
                        parameter.Set(target_source[tgtv].GenLevel.Id)
            print(f"Pasted on floor: {floorelem}")

        # Create Group
        group = doc.Create.NewGroup(List[ElementId](pasted_elements))
        group.GroupType.Name = f"Dynamo Floor {floorelem}A Models"
        comments = group.LookupParameter("Comments")
        comments.Set("DYNAMOSCRIPTMODEL")
        floor_end_time = time.perf_counter()
        floor_paste_time = floor_end_time - floor_start_time
        print(f"Pasted on {floorelem} and grouped at time: {floor_paste_time} seconds")



    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")


@transaction
def delete_models():
    start_time = time.perf_counter()


    model_groups = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsNotElementType().ToElements()
    model_group_types = {}
    for grp in model_groups:
        comments = grp.LookupParameter("Comments")
        if comments.AsValueString() == "DYNAMOSCRIPTMODEL":
            print(grp.Name)
            grp_type_id = grp.GroupType.Id.ToString()
            if grp_type_id not in model_group_types:
                model_group_types[grp_type_id] = grp.GroupType
            doc.Delete(grp.Id)
    
    for i in model_group_types:

        doc.Delete(model_group_types[i].Id)


    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Delete time: {elapsed_time} seconds")

start_total = time.perf_counter()
delete_models()
start()
end_total = time.perf_counter()
print(f"Total time: {end_total-start_total} seconds.")


OUT = output.getvalue()
# OUT = filtered_views