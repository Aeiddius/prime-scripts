import clr
import math, sys
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, IndependentTag,FilledRegion, CurveLoop, DetailLine, BuiltInCategory 

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
  if isinstance(id, str) or isinstance(id, int):
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


def get_room_curve(group_elements):
  room_curve = CurveLoop()
  for id in group_elements:
    e = doc.GetElement(id)
    if isinstance(e, DetailLine):
      line = e.GeometryCurve
      room_curve.Append(line)
  return room_curve
 



floor_views = {}

@transaction 
def start():
  base_floor = active_view

  detail_groups = FilteredElementCollector(doc, base_floor.Id).OfCategory(BuiltInCategory.OST_IOSDetailGroups).ToElements()

  for dg in detail_groups: 
    dg_ids = dg.GetMemberIds()

    room_curve = get_room_curve(dg_ids)
    print(dg.Name, room_curve)



    filled_region_id = ElementId(3786335)
    filled_region = FilledRegion.Create(doc, filled_region_id, base_floor.Id, [room_curve])
    filled_region.LookupParameter("Comments").Set(dg.Name)
    doc.Delete(dg.Id)

start()
print("\n\n\n")

OUT = output.getvalue()