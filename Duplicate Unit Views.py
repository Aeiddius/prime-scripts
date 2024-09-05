import clr
import math
from io import StringIO
import inspect
import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ViewDuplicateOption, Dimension
from Autodesk.Revit.DB import ViewFamilyType, ViewType
from Autodesk.Revit.DB import FilteredElementCollector, Line, XYZ
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

from Revit.Elements import Element

clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')
# For Outputting print to watch node
output = StringIO()
sys.stdout = output

doc = DocumentManager.Instance.CurrentDBDocument
elements = UnwrapElement(IN[0])



def transaction(func):
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper

def print_member(obj):
    for i in dir(obj):
        print(i)

def duplicate_view(view, name, view_type):
    newId = view.Duplicate(ViewDuplicateOption.Duplicate)
    newView = doc.GetElement(newId)
    newView.CropBoxVisible = False
    newView.Name = name
    newView.ViewType = view_type
    return newView


def change_view_type(plan_view, view_type):
    Element.SetParameterByName(plan_view, "Type", view_type)


def get_elementType(doc, view_type_name):
    view_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    for vt in view_types:
        if vt.get_Name() == view_type_name:
            return vt
    return None

def replace_text_at_end(s, old_suffix, new_suffix):
    if s.endswith(old_suffix):
        return s[:-len(old_suffix)] + new_suffix
    return s.strip()

floor_type = "Architectural Unit Plan"

exists = []

@transaction
def start():
    


    x = get_elementType(doc, floor_type)
    for i in elements:
        change_view_type(i, x)

    
    #     if i.Name.endswith("-U"):
    #         exists.append(i.Name)
    

    # for i in elements:
    #     # change_view_type(i, new_view_type)
    #     if i.Name.endswith("-U"): continue
    #     if i.Name + "-U" in exists:
    #         to_change.append(i)
    #     #     change_view_type(i, new_view_type)
    #     # duplicate_view(i, i.Name + "-U", new_view_type)
start()


# OUT = result

        # duplicate_view(i, i.Name + "-U", new_view_type)

start()

OUT = output.getvalue()
