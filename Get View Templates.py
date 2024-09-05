import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import CurveLoop, ElementId, Plane, BoundingBoxXYZ
from Autodesk.Revit.DB import View, CurveLoop
from Autodesk.Revit.DB import DetailLine , ViewType
from Autodesk.Revit.DB.Architecture import Room

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import FilteredElementCollector, Line, ViewFamily


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


@transaction
def start():
    collector = FilteredElementCollector(doc)
    view_templates = collector.OfClass(View)
    for vt in view_templates:
        if vt.IsTemplate:
            print(vt.Id, vt.Name)
            continue


    # for view in view_templates:
    #     if isinstance(view, View) and view.IsTemplate:
    #         view_templates[view.Id] = view.Name
    #     print(view_templates)

start()

OUT = output.getvalue()


