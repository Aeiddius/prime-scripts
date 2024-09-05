import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ViewPlacementOnSheetStatus, Dimension
from Autodesk.Revit.DB import Point, ViewType
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ


clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')
# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
elements = UnwrapElement(IN[0])

base_view_model = UnwrapElement(IN[1])


def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper
result = []

@transaction
def start():
    for i in elements:
        if i.Name == base_view_model: continue
        sheet_status = i.GetPlacementOnSheetStatus()
        if sheet_status == ViewPlacementOnSheetStatus.NotApplicable:
            print("Not Applicable")
            result.append(i)
        if sheet_status == ViewPlacementOnSheetStatus.NotPlaced:
            print("Not Placed")
            result.append(i)
        if sheet_status == ViewPlacementOnSheetStatus.PartiallyPlaced:
            print("Partially Placed")
        if sheet_status == ViewPlacementOnSheetStatus.CompletelyPlaced:
            print("Completely Placed")

start()

# OUT = output.getvalue()
OUT = result
