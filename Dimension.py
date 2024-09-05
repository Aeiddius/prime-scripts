import clr
from io import StringIO

import Autodesk
import RevitServices
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import FilteredElementCollector, Dimension

from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")


# For Outputting print to watch node
output = StringIO()
sys.stdout = output

# Import model
# models = UnwrapElement(IN[0])        # Autodesk.Revit.DB.Dimension
# modelRaw = IN[0]                    # Dimension

# Import unicode tables
numerator = IN[0]['numerator']
denominator = IN[0]['denominator']

is_reset = IN[1]

# Get doc variable
doc = DocumentManager.Instance.CurrentDBDocument


def transaction(func):
    """
    Decorator to ensure that a Revit transaction is started and completed 
    around the execution of the given function.

    Parameters:
    func (function): The function to be wrapped within a transaction.
    
    Returns:
    function: A wrapper function that executes the original function within a transaction.
    """
    def wrapper(*args, **kwargs):
            TransactionManager.Instance.EnsureInTransaction(doc)
            func(*args, **kwargs)
            TransactionManager.Instance.TransactionTaskDone()
    return wrapper


def fraction_converter(inch_num: str, inch_denom: str):
    """
    Converts inch fractions into a stacked unicode format using provided 
    numerator and denominator mappings.

    Parameters:
    inch_num (str): The numerator part of the inch fraction.
    inch_denom (str): The denominator part of the inch fraction.
    
    Returns:
    str: A string representing the fraction in stacked unicode format.
    """
    res = {"super": "", "subs": ""}

    for num in inch_num:
        res["super"] += numerator[num]

    for denom in inch_denom:
        res["subs"] += denominator[denom]
    
    return f"{res['super']}⁄{res['subs']}"


def change_format(dimension: Autodesk.Revit.DB.Dimension, value_string: str):
    """
    Formats the dimension's value string into a tighter and more visually appealing format.
    Handles both whole numbers and fractions, converting fractions to a stacked unicode format.

    Parameters:
    dimension (Autodesk.Revit.DB.Dimension): The dimension element whose value will be formatted.
    value_string (str): The original value string of the dimension to be formatted.
    
    Returns:
    None
    """
    divided = ""
    try:
        divided = value_string.split("-")

    except:
        print("WEIRD: ", value_string, dimension)
        return
    feet = ""
    inch = ""
    try:
        feet = divided[0].strip()
        inch = divided[1].strip().split(" ")
    except:
        print(value_string)
        return
    if len(inch) == 1:
        return
        value = f"{feet}-{inch[0]}"
        set_override_value(dimension, "")
        set_override_value(dimension, value)
    else:
        inchWhole = inch[0]
        inchFrac = inch[1].replace("'", '"')

        # Split the inch numerator and denominator into index 0 and 1
        inchFracSplit = inchFrac.split("/")

        # Converts into fractional unicode format
        fraction = fraction_converter(inchFracSplit[0], inchFracSplit[1][:-1])
        
        # Applies the value
        value = f"{feet}-{inchWhole}{fraction}\""
        set_override_value(dimension, "")
        set_override_value(dimension, value)
        
def set_override_value(dimension: Autodesk.Revit.DB.Dimension, new_value: str):
    """
    Overrides the value of a dimension element with a new value.

    Parameters:
    dimension (Autodesk.Revit.DB.Dimension): The dimension element whose value will be overridden.
    new_value (str): The new value to override the dimension with.
    
    Returns:
    None
    """
    dimension.ValueOverride = new_value
    
@transaction
def start(model: Autodesk.Revit.DB.Dimension):
    """
    Applies formatting to the dimension values in a Revit model. If the dimension
    is segmented, the formatting is applied to each segment individually.

    Parameters:
    model (Autodesk.Revit.DB.Dimension): The dimension element or model to be formatted.
    
    Returns:
    None
    """
    size = model.Segments.Size

    if size == 0:
        change_format(model, model.ValueString)
        # print("Single: ", model.ValueString)
    else:
        for i in range(0, size):
            dim = model.Segments[i]
            change_format(dim, dim.ValueString)
            # print("Segmented: ", dim.ValueString)


@transaction
def reset(model: Autodesk.Revit.DB.Dimension):
    """
    Resets the value override of a dimension element, effectively clearing any custom
    formatting or values applied. If the dimension is segmented, resets each segment.

    Parameters:
    model (Autodesk.Revit.DB.Dimension): The dimension element or model to be reset.
    
    Returns:
    None
    """
    size = model.Segments.Size
    if size == 0:

        set_override_value(model, "")
    else:
        for i in range(0, size):
            dim = model.Segments[i]
            set_override_value(dim, "")
            
collector = FilteredElementCollector(doc).OfClass(Dimension)
models = list(collector)
for i in models:
    reset(i)


if not is_reset:
    for i in models:
        start(i)

OUT = output.getvalue()
