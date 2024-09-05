import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension
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

view_type = IN[1]

result = []

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

@transaction
def start():
    for i in elements:
        if view_type == "Floor Plan" and i.ViewType == ViewType.FloorPlan:
            result.append(i)
            continue
        if view_type == "Ceiling Plan" and i.ViewType == ViewType.CeilingPlan:
            result.append(i)
            continue

start()

# OUT = output.getvalue()
OUT = result