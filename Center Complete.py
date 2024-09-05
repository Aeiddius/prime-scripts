import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import CurveLoop, ElementId, Plane, BoundingBoxXYZ
from Autodesk.Revit.DB import ViewPlan, CurveLoop
from Autodesk.Revit.DB import DetailLine , XYZ
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

def get_midpoint(point1, point2):

    # Calculate the midpoint coordinates
    midpoint_x = (point1.X + point2.X) / 2
    midpoint_y = (point1.Y + point2.Y) / 2
    midpoint_z = (point1.Z + point2.Z) / 2
    # Return a new XYZ point representing the midpoint
    return XYZ(midpoint_x, midpoint_y, midpoint_z)

def midshit(xyz):
     return XYZ(0, xyz.Normalize().Y, 0)

@transaction
def start():
    element = UnwrapElement(IN[0])
    # element.TextPosition = element.Origin.Add(XYZ(0,-0.6,0))

    size = element.Segments.Size

    if size == 0:
        element.TextPosition = element.Origin.Add(XYZ(0,-0.6,0))
        # print("Single: ", model.ValueString)
    else:
        for i in range(0, size):
            dim = element.Segments[i]
            dim.TextPosition = dim.Origin.Add(XYZ(0,-0.6,0))

start()

OUT = output.getvalue()


