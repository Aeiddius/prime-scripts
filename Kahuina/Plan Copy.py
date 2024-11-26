import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, Group, ElementId, Electrical

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

def get_element(id_str):
  return doc.GetElement(ElementId(id_str))

def copy_to_plan(base_plan, t_plan, collection_elements, options_dict):

  # Copy the Elemetns
  copied_ids = ElementTransformUtils.CopyElements(base_plan, collection_elements, t_plan, Transform.Identity, CopyPasteOptions())
  copied_elements = [doc.GetElement(cid) for cid in copied_ids]
  
  for celem in copied_elements:
    if isinstance(celem, FamilyInstance): 
      
      parameter = celem.LookupParameter("Schedule Level")
      if parameter and not parameter.IsReadOnly:
        parameter.Set(t_plan.GenLevel.Id)

    # Panel reName
    if options_dict["prename"] == true:
      if isinstance(celem, FamilyInstance) and celem.Category.Id.IntegerValue == int(BuiltInCategory.OST_ElectricalEquipment):
        print(celem.Name, type(celem))

        param_panel = celem.LookupParameter("Comments")
        param_panel_value = param_panel.AsValueString()
        if param_panel_value == "Panel":
          param_panel_name = celem.LookupParameter("Panel Name")
          raw_name = param_panel_name.AsValueString().strip().split(" ", 1) #    ["A2", "[Unit 401]"]
          real_pname = raw_name[0]                               #     "A2"
          unit_no = raw_name[1].replace("]", "").replace("[", "").split(" ")[1].replace("4", "", 1) #     "01"
          
          floor_no = t_plan.Name.replace("LEVEL", "").strip()[0:-1]
          final_name = f'{real_pname} [UNIT {floor_no}{unit_no}]'
          print("St: ", final_name)
          param_panel_name.Set(final_name)

          celem.LookupParameter("Mark").Set(real_pname)


  group = doc.Create.NewGroup(List[ElementId](copied_ids))
  group.GroupType.Name = f"{t_plan.Name} Models"


def delete_group_plan(t_plan):
  elems = FilteredElementCollector(doc, t_plan.Id).OfCategory(BuiltInCategory.OST_IOSModelGroups).ToElements()
  group_types = []
  for grp in elems:
    group_types.append(grp.GroupType)
    doc.Delete(grp.Id)
  
  for e in group_types:
    doc.Delete(e.Id)

def get_options(options):
  diction = {}
  diction["prename"] = options[0]
  return diction

mode = UnwrapElement(IN[0])
proceed = UnwrapElement(IN[1])
base_plan_id = UnwrapElement(IN[2])
target_plans = UnwrapElement(IN[3])
options = UnwrapElement(IN[4])

# 2680980


@transaction 
def start():
  print("Current Mode: ", mode)
  base_plan = get_element(base_plan_id)
  target_plans_elems = [get_element(e) for e in target_plans]
  options_dict = get_options(options)

  # Delete
  if mode == False:
    for tar_plan in target_plans_elems:
      delete_group_plan(tar_plan)

  # Copy
  elif mode == True:
    # Get All elements in base view plan
    elements_source = FilteredElementCollector(doc, base_plan.Id).WhereElementIsNotElementType().ToElements()
    filtered_elements = []

    # Filter Elements
    for e in elements_source:
      category = e.Category

      if not category or (category and category.Id.IntegerValue in exception_categories):
        continue

      filtered_elements.append(e.Id)


    # Creat c# compatible list
    collection = List[ElementId](filtered_elements)

    # apply copy to every target plan
    for tar_plan in target_plans_elems:
      copy_to_plan(base_plan, tar_plan, collection, options_dict)


if proceed:
  print("Starting Script")
  start()
else:
  print("Script not enabled")

OUT = output.getvalue()