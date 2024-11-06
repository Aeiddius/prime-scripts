import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, Group, ElementId

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

def copy_to_plan(base_plan, t_plan):
  elements_in_source_view = FilteredElementCollector(doc, base_plan.Id).WhereElementIsNotElementType().ToElements()

  processed_elems = []

  for e in elements_in_source_view:
    category = e.Category

    if not category or (category and category.Id.IntegerValue in exception_categories):
      continue
    
    processed_elems.append(e.Id)
    print(f'[{e.Name}], [{e.Id}]')

  filtered = List[ElementId](processed_elems)

  copied_element = ElementTransformUtils.CopyElements(base_plan, filtered, t_plan, Transform.Identity, CopyPasteOptions())
  print("Copied Elements: ", copied_element)

def delete_group_plan(t_plan):
    elems = FilteredElementCollector(doc, t_plan.Id).OfCategory(BuiltInCategory.OST_IOSModelGroups).ToElements()
    for i in elems:
       doc.Delete(i.Id)


mode = UnwrapElement(IN[0])
proceed = UnwrapElement(IN[1])
base_plan_id = UnwrapElement(IN[2])
target_plans = UnwrapElement(IN[3])

# 2680980

exception_categories = [
   int(BuiltInCategory.OST_RvtLinks),
   int(BuiltInCategory.OST_Grids),
   int(BuiltInCategory.OST_SectionBox),
   int(BuiltInCategory.OST_Cameras),
   int(BuiltInCategory.OST_Elev),
   int(BuiltInCategory.OST_Viewers),
]

@transaction 
def start():
  print("Current Mode: ", mode)
  base_plan = get_element(base_plan_id)
  target_plans_elems = [get_element(e) for e in target_plans]
  if mode == "Delete":
    for tar_plan in target_plans_elems:
      delete_group_plan(tar_plan)

  elif mode == "Copy":
    for tar_plan in target_plans_elems:
      copy_to_plan(base_plan, tar_plan)


if proceed:
  print("Starting Script")
  start()
else:
  print("Script not enabled")

OUT = output.getvalue()