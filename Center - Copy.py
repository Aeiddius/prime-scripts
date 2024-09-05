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

# Import model  

def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper


import math

def calculate_angle(x1, y1, x2, y2):
    # Calculate the differences
    delta_x = x2 - x1
    delta_y = y2 - y1
    
    # Compute the angle in radians
    angle_radians = math.atan2(delta_y, delta_x)
    
    # Convert the angle to degrees
    angle_degrees = angle_radians * (180 / math.pi)
    
    return angle_degrees

def move_point(x, y, distance, angle):
    # Convert angle from degrees to radians
    angle_rad = math.radians(angle)
    
    # Calculate the movement in the x and y directions
    delta_x = distance * math.sin(angle_rad)
    delta_y = distance * math.cos(angle_rad)
    
    # Move the point
    return [x + delta_x, y + delta_y]

def check_dim_dir(dimension):
    dim_curve = dimension.Curve

    dir = [float(a.strip()) for a in str(dim_curve.Direction).strip().replace("(", "").replace(")", "").split(",")]
    # print(dir, dimension.TextPosition)
    angle = calculate_angle(dir[0], dir[1], 0, 0)
    new_Angle = round(angle) if angle < 180 and angle >=0 else round(abs(abs(angle) - 180))
    print(new_Angle)

    coords = dimension.Origin

    new_pos = move_point(coords.X, coords.Y, 1, new_Angle)
    print(coords, new_pos)
    return new_pos
    
    # if dir[0] == 1 and dir[1] == 0 and dir[2] == 0:
    #     # print("Straight Horizontal")
    #     return {"dir": "horizontal", "val": dir}
    # elif dir[0] == 0 and (dir[1] == -1 or dir[1] == 1) and dir[2] == 0:
    #     print("Straight Vertical")
    #     return {"dir": "vertical", "val": dir}
    
    # return {"dir": "angled", "val": dir}


def modify(model):
    res = check_dim_dir(model)
    a = model.Origin


    model.TextPosition = XYZ(res[0], res[1], a.Z)


    # a = model.Origin
    # hori = -1
    # vert = 0.8
    # angl = -1
    # if res["dir"] == "horizontal":
    #     model.TextPosition = XYZ(a.X, a.Y + hori, a.Z)
    #     # print("----horizontal done")
    # elif res["dir"] == "vertical":
    #     model.TextPosition = XYZ(a.X + vert, a.Y, a.Z)
    #     # print("----vertical done")
    # elif res["dir"] == "angled":
    #     model.TextPosition = XYZ(a.X + (res["val"][1]),
    #                              a.Y + angl + (res["val"][1]),
    #                              a.Z)
    #     # model.TextPosition = XYZ(a.X, a.Y + angl, a.Z)

    #     # print("----angled done")

@transaction
def reset(model):
    size = model.Segments.Size
    if size == 0:
        try:
            model.ResetTextPosition()
        except:
            # print("FUCK: ")
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

        # try:
        #     modify(model)
        # except:
        #     # print("FUCKss: ")
        #     pass
    else:
        for i in range(0, size):
            dim = model.Segments[i]
            modify(dim)


# collector = FilteredElementCollector(doc).OfClass(Dimension)
# models = list(collector)

res = True
res = False

time = IN[1]

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
