import clr
import math
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import Dimension, Line, XYZ

clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")


# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
time = IN[1]

# Import model  

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

def calculate_angle(x1, y1, x2, y2):
    # Calculate the differences
    delta_x = x2 - x1
    delta_y = y2 - y1
    
    # Compute the angle in radians
    angle_radians = math.atan2(delta_y, delta_x)
    
    # Convert the angle to degrees
    angle_degrees = angle_radians * (180 / math.pi)
    
    return angle_degrees


def create_incrementer(value, increment=0.05, threshold=10):

    thresholds_crossed = value // threshold
    
    # Calculate the incremented value
    incremented_value = thresholds_crossed * increment
    
    return incremented_value


def check_dim_dir(dimension, dim_curve_segment):
    dim_curve = 0
    if dim_curve_segment:
        dim_curve = dim_curve_segment
    else:
        dim_curve = dimension.Curve
    dir = [float(a.strip()) for a in str(dim_curve.Direction).strip().replace("(", "").replace(")", "").split(",")]



    if dir[0] == 1 and dir[1] == 0 and dir[2] == 0:
        return {"dir": "horizontal", "val": dir}
    elif dir[0] == 0 and (dir[1] == -1 or dir[1] == 1) and dir[2] == 0:
        return {"dir": "vertical", "val": dir}
    
    angle = calculate_angle(dir[0], dir[1], 0, 0)
    new_Angle = round(angle) if angle < 180 and angle >=0 else round(abs(abs(angle) - 180))

    if new_Angle > 90:
        return {"dir": "angled-op", "val": dir, "angle": new_Angle}
    return {"dir": "angled", "val": dir, "angle": new_Angle}


def modify(model, dim_curve=None):
    res = check_dim_dir(model, dim_curve)

    a = model.Origin
    hori = -1
    vert = 0.8
    angl = -1.5
    if res["dir"] == "horizontal":
        model.TextPosition = XYZ(a.X, a.Y + hori, a.Z)
    elif res["dir"] == "vertical":
        model.TextPosition = XYZ(a.X + vert, a.Y, a.Z)
    elif res["dir"] == "angled":
        inc = create_incrementer(res["angle"], 0.1)

        model.TextPosition = XYZ(a.X + (res["val"][1]),
                                 a.Y + angl + inc + (res["val"][1]),
                                 a.Z)
        print("inc: ", inc)
    elif res["dir"] == "angled-op":
        inc = create_incrementer(res["angle"], 0.1)
        model.TextPosition = XYZ(a.X + (res["val"][1]),
                                 a.Y - angl -inc + (res["val"][1]),
                                 a.Z)
        
        print("inc: ", inc)

@transaction
def reset(model):
    size = model.Segments.Size
    if size == 0:
        try:
            model.ResetTextPosition()
        except:
            pass
    else:
        for i in range(0, size):
            dim = model.Segments[i]
            dim.ResetTextPosition()


@transaction
def start(model):
    size = model.Segments.Size
    if size == 0:
        modify(model)
    else:
        dim_curve = model.Curve
        for i in range(0, size):
            dim = model.Segments[i]
            modify(dim, dim_curve)


# collector = FilteredElementCollector(doc).OfClass(Dimension)
# models = list(collector)

res = True
res = False


models = UnwrapElement(IN[0])
if isinstance(models, list):
    dimensions = [elem for elem in models if isinstance(elem, Dimension)]
    for model in dimensions:
        if res:
            reset(model)
        else:
            start(model)
else:
    if res:
        reset(models)
    else:
        start(models)


OUT = output.getvalue()
