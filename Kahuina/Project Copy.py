import clr
import math
from io import StringIO
import sys

import Autodesk
import RevitServices
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Electrical, IndependentTag,BuiltInParameter, BuiltInCategory, ElementTransformUtils, FamilyInstance

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


# active_view = doc.ActiveView

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper


def gen_transaction(func):
    def wrapper(*args, **kwargs):
            t = Transaction(doc, 'Copy Elements C: Between Projects')
            t.Start()
            func(*args, **kwargs)
            t.Commit()
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

exception_categories = [
  int(BuiltInCategory.OST_RvtLinks),
  int(BuiltInCategory.OST_Grids),
  int(BuiltInCategory.OST_SectionBox),
  int(BuiltInCategory.OST_Cameras),
  int(BuiltInCategory.OST_Elev),
  int(BuiltInCategory.OST_Viewers),
  int(BuiltInCategory.OST_Viewers),
  int(BuiltInCategory.OST_IOSModelGroups),
  int(BuiltInCategory.OST_ElectricalEquipmentTags)
]


ui_app = DocumentManager.Instance.CurrentUIApplication
app = ui_app.Application

doc = DocumentManager.Instance.CurrentDBDocument
all_docs = list(app.Documents)

doc_A = all_docs[1] # Lighting
doc_B = all_docs[3] # Consolidated

elements = UnwrapElement(IN[1])

@transaction 
def start():

  # print(all_docs)
  # print(elements)

  # print(doc_A, doc_A.Title)

  filtered_list = []
  for e in elements:
    if e.ViewSpecific: continue
    category = e.Category
    if not category or (category and category.Id.IntegerValue in exception_categories):
      continue

    # if isinstance(e, FamilyInstance):
    filtered_list.append(e.Id)
  
  elementsToCopy = List[ElementId](filtered_list)

  transform    = Transform.Identity
  opts         = CopyPasteOptions()




  ElementTransformUtils.CopyElements(doc_A,
                                elementsToCopy,
                                doc_B,
                                transform,
                                opts)

start()

# OUT = output.getvalue()