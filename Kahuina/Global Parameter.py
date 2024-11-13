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


def set_parameter(element, parameter_name, new_value):
    parameter = element.GetParameters(parameter_name)[0]
    parameter.SetValueString(new_value)

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
      if not param.IsReadOnly and value and value.startswith("GB: "):
          param_name = value.replace("GB:", "").strip()

          for gpm in global_parameters:
              if gpm.Name == param_name:
                gpm_value = gpm.GetValue().Value
                parameter = element.LookupParameter("Elevation from Level")

                if param.IsReadOnly: continue
                parameter.Set(gpm_value)

                print("Set: ", element.Name, element.Id, parameter.AsValueString())
start()

OUT = output.getvalue()