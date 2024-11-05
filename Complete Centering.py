import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension
from Autodesk.Revit.DB import Dimension, Line, XYZ, Transform
from Autodesk.Revit.UI import TaskDialog

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")


# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument

# Import model  

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper


def print_member(obj):
    for i in dir(obj):
        print(i)

def normalize_vector(vector: XYZ):
    x, y = vector.X, vector.Y
    length = math.sqrt((x)**2 + (y)**2)
    x_new = x/length
    y_new = y/length
    return x_new, y_new
    
def get_downward_xyz(current_pos: XYZ, direction: XYZ, h: float):
    x, y = normalize_vector(direction)
    print(x, y)
    x1 = -x * h
    y1 = -y * h
    
    x_new = x1 + current_pos.X
    y_new = y1 + current_pos.Y
    return XYZ(x_new, y_new, 0.0)
    

@transaction
def start():
    TaskDialog.Show("Revit",  "Hello")
    element = UnwrapElement(IN[0])
    line = element.get_Curve()

    # bo = element.GetParameters("Baseline Offset")[0]


    # val = element.GetParameters("Value")[0]

    element.ResetTextPosition()
    element.TextPosition = get_downward_xyz(element.TextPosition, 
                                            element.TextPosition,
                                            1)

    print(line.Direction)
    
    # bo.Set(1.0)
    # element.TextPosition = line.Origin
    
    
    # for i in line.get_ParametersMap():
    #     defi = i.Definition
    #     print(defi.Name, i.StorageType)

start()
OUT = output.getvalue()
