import clr
import math
import re
from io import StringIO

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


def get_view_range(target_view_type, target_discipline):
    filtered_list = []
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()

    for view in view_list:

        view_type = view.LookupParameter("View Type").AsValueString()
        if view_type != target_view_type: continue

        discipline = view.LookupParameter("Type").AsValueString()
        if discipline != target_discipline: continue

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
    # Filter Elements
    for e in elements_source:
        category = e.Category
        if not category: continue

        if not category or (category and category.Id.IntegerValue in exception_categories):
            continue
        if category.Id.IntegerValue == int(BuiltInCategory.OST_IOSModelGroups):
        
            ids = e.GetMemberIds()
            for id in ids:
                filtered_elements.append(get_element(id))
            continue

        if isinstance(e, FamilyInstance):
            if isinstance(e.MEPModel, ElectricalEquipment):
                filtered_elements.append(e)
            continue

        filtered_elements.append(e)
        # print(e, e.Name)
        
    return filtered_elements

def filter_source_elements2(base_view):
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
        self.sview = view
        self.elements_list = List[ElementId]([e.Id for e in self.elements])


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

min = 5
max = 43



@transaction
def start2():
    source_views = get_view_range("Working Views", target_discipline)
    
    for view in source_views:
        if "Level 4A" in view.Name: continue


        unit_name = re.search(r"\((.*?)\)", view.Name).group(1)
        filtered_elements = filter_source_elements2(view)
        # level = get_num(view.LookupParameter("Associated Level").AsValueString())
        # view_level = re.findall(r"\s\d{4}\s", view.Name)

        if "Dependent " in view.LookupParameter("Dependency").AsValueString():
            unit_source[unit_name] = Source(get_element(view.GetPrimaryViewId()), filtered_elements)
        else:
            unit_source[unit_name] = Source(view, filtered_elements)


    # Get Target views in a neat dictionary
    target_views = get_view_range("Presentation Views", target_discipline)
    target_source = {}
    for tview in target_views:
        if "Dependent " in tview.LookupParameter("Dependency").AsValueString():
            continue
        level = get_num(tview.Name)
        target_source[level] = tview


    # iterates through units
    for unit in unit_source:
        print
        unit_matrix = matrix[unit]
        min_lvl = unit_matrix.min
        max_lvl = unit_matrix.max

        for tgtv in target_source:
            # Places only in where they are applicable
            if min_lvl <= tgtv <= max_lvl:
                # print(f"{min_lvl} | {max_lvl} | Current: {tgtv}")
                
                # for i in unit_source[unit].elements:
                #     print(i)
                # break  
                # print("SUPPIOSED: ", unit_source[unit].sview.Id)
                # for i in unit_source[unit].elements:
                #     print(i.OwnerViewId)
                # break
                copied_ids = ElementTransformUtils.CopyElements(
                    unit_source[unit].sview, 
                    unit_source[unit].elements_list, 
                    target_source[tgtv], 
                    Transform.Identity,
                    CopyPasteOptions()
                )
                xids = []
                for i in copied_ids:
                    xids.append(i.ToString())
                print(f"{unit}:  {xids}\n")
                copied_elements = [get_element(cid) for cid in copied_ids]

                for celem in copied_elements:
                    if isinstance(celem, FamilyInstance): 
                        parameter = celem.LookupParameter("Schedule Level")
                        if parameter and not parameter.IsReadOnly:
                            parameter.Set(target_source[tgtv].GenLevel.Id)
        

        


@transaction 
def start():
    source_views = get_view_range("Working Views", target_discipline)

    for view in source_views:
        filtered_elements = filter_source_elements(view)
        level = get_num(view.LookupParameter("Associated Level").AsValueString())
        view_level = re.findall(r"\s\d{4}\s", view.Name)
        if view_level != []:
            unit_source[view_level[0]] = Source(view, filtered_elements)
        else:
            unit_source[level] = Source(view, filtered_elements)

    target_views = get_view_range("Presentation Views", target_discipline)
    

    for tview in target_views:
        level = get_num(tview.Name)

        if "Dependent " in tview.LookupParameter("Dependency").AsValueString():
            continue
        
        if 5 <= level <= 31:
            print(level, tview.Name)
            copied_ids = ElementTransformUtils.CopyElements(
                unit_source[4].sview, 
                unit_source[4].elements_list, 
                tview, 
                Transform.Identity,
                CopyPasteOptions()
            )


            copied_elements = [get_element(cid) for cid in copied_ids]

            for celem in copied_elements:
                if isinstance(celem, FamilyInstance): 
                    parameter = celem.LookupParameter("Schedule Level")
                    if parameter and not parameter.IsReadOnly:
                        parameter.Set(tview.GenLevel.Id)
     
                    # if "UNIT" in celem.Name:
                    #     print("UNITT" , celem.Name, celem.Id)

            # copied_tag_ids = ElementTransformUtils.CopyElements(
            #     unit_source[4].sview, 
            #     unit_source[4].tag_list, 
            #     tview, 
            #     Transform.Identity,
            #     CopyPasteOptions()
            # )

            break
            # for i in elems:
            #     print(i)


start2()

OUT = output.getvalue()
# OUT = filtered_views