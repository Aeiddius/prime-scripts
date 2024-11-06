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

def copy_to_plan(base_plan, target_level):
  t_plan = get_element(target_level)
  print(t_plan.Name)
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



proceed = UnwrapElement(IN[0])
base_plan_id = UnwrapElement(IN[1])
target_plans = UnwrapElement(IN[2])

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

  base_plan = get_element(base_plan_id)
  for plan in target_plans:
    copy_to_plan(base_plan, plan)


if proceed:
  print("Starting Script")
  start()
else:
  print("Script not enabled")

OUT = output.getvalue()