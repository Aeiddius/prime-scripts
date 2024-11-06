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


mode = UnwrapElement(IN[0])
# 2680980



@transaction  
def start():
  global_parameters = FilteredElementCollector(doc).OfClass(GlobalParameter)

  collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
  matching_elements = []

  # Iterate through each element in the collection
  for element in collector:
      param = element.LookupParameter("Comments")
      if not param: continue
      value = param.AsValueString()
      if param and value:
          print(param.AsValueString())
      #     x = comments_param.AsString()
      #     print(x)
          # if comments_param.AsString() == "GB: Sconce":
          #     # If it matches, add the element to the list
          #     matching_elements.append(element)

  # Extract the names of all global parameters
  for gpm in global_parameters:
      value = gpm.GetValue().Value
      print(gpm.Name, value)

start()

OUT = output.getvalue()