import clr
import math
import sys
from io import StringIO
 
import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import CurveLoop, ElementId, Plane, BoundingBoxXYZ
from Autodesk.Revit.DB import ViewPlan, CurveLoop
from Autodesk.Revit.DB import DetailLine , ViewType
from Autodesk.Revit.DB.Architecture import Room

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import ViewDuplicateOption, Line, ViewFamily

 
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')
# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument


def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

def print_member(obj):
    for i in dir(obj):
        print(i)

def set_view_crop(view, curve):
    crop_manager = view.GetCropRegionShapeManager()
    crop_shape = crop_manager.GetCropShape()[0]
    crop_manager.SetCropShape(curve)

def get_room_curve(group_elements):
    room_curve = CurveLoop()
    for id in group_elements:
        e = doc.GetElement(id)
        if isinstance(e, DetailLine):
            line = e.GeometryCurve
            room_curve.Append(line)
    return room_curve
 
def duplicate_view(view, name):
    newId = view.Duplicate(ViewDuplicateOption.AsDependent)
    newView = doc.GetElement(newId)
    newView.CropBoxVisible = False
    newView.Name = name
    return newView
 
@transaction
def start():
    views = UnwrapElement(IN[0])
    # Get Variables
    print(views)
    for view in views:
        print(view)

    # group = UnwrapElement(IN[0])
    # group_elements = group.GetMemberIds()

    # # Extract Room and Room Curve
    # room_curve = get_room_curve(group_elements)

    # # Duplicate View as dependent
    # newView = duplicate_view(view, group.Name)

    # # Set view crop
    # set_view_crop(newView, room_curve)



start()

OUT = output.getvalue()


