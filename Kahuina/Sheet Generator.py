import clr
import math, sys
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet,Viewport, BuiltInCategory, ElementTransformUtils, FamilyInstance

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ, ViewPlan, ElementId, Electrical

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

def get_num(str):
  res = ''.join(char for char in str if char.isdigit())
  if res:
    return int(res)
  else: return None

def get_view_range(view_group, target_view_type, target_family_type, range_value=None):
    result = []
    view_list = FilteredElementCollector(doc).OfClass(ViewPlan).ToElements()
    for view in view_list:
        if view.IsTemplate == True: continue

        
        if view.LookupParameter("View Group").AsValueString() != view_group: continue

        if view.LookupParameter("View Type").AsValueString() != target_view_type: continue

        if view.LookupParameter("Type").AsValueString() != target_family_type: continue

        if range_value:
          min_range = range_value[0]
          max_range = range_value[1]

          level = get_num(view.Name)
          if min_range <= level <= max_range:
              result.append(view)
              continue
          
        else:
          result.append(view)
          continue
          
    return result


@transaction 
def start():
    # titleblock_id = ElementId(2276743)
    # view_id = ElementId(2637110)
    # new_sheet = ViewSheet.Create(doc, titleblock_id)
    # new_sheet.LookupParameter("Sheet Group").Set("Unit Plan")

    # new_sheet.LookupParameter("Sheet Type").Set("Floor A4")

    # new_sheet.LookupParameter("Sheet Sub-Type").Set("0402 A-2A")

    # return
    # pt_cros = XYZ(-0.15,0.75,0)
    # vp = Viewport.Create(doc, new_sheet.Id, view_id, pt_cros)
    vp = get_element(3777011) # Lighhtibng
    vp = get_element(3933291) # Device
    # print_member(vp)
    vp_bbox = vp.GetBoxOutline()
    max_p = vp_bbox.MaximumPoint
    min_p = vp_bbox.MinimumPoint
    
    val = max_p.Subtract(min_p)
    current_center = vp.GetBoxCenter()

    # vp.SetBoxCenter(XYZ(96.7,26.5,0))
    # vp.SetBoxCenter(XYZ(0,0,0))
    # vp.SetBoxCenter(XYZ(2.975649178, 1.864583333, 0.000000000))
    new_x = (val.X/2) + 0.4
    new_y = (val.Y/2) + 0.15
    # new_x = (val.X/2) 
    # new_y = (val.Y/2) 

    vp.SetBoxCenter(XYZ(new_x, new_y, 0))
    # vp.SetBoxCenter(XYZ(0, 0, 0))

    # print("Min= ", bottom_left)
    # print_member(vp_min)


start()

OUT = output.getvalue()