
import sys
from fractions import Fraction
from io import StringIO
output = StringIO()
sys.stdout = output


# dictionary
numerator = {
"0" : "⁰",
"1" : "¹",
"2" : "²",
"3" : "³",
"4" : "⁴",
"5" : "⁵",
"6" : "⁶",
"7" : "⁷",
"8" : "⁸",
"9" : "⁹",
}

denominator = {
"0" : "₀",
"1" : "₁",
"2" : "₂",
"3" : "₃",
"4" : "₄",
"5" : "₅",
"6" : "₆",
"7" : "₇",
"8" : "₈",
"9" : "₉",
}


# The inputs to this node will be stored as a list in the IN variables.
models = IN[0]


for model in models:
    
    # The inputs to this node will be stored as a list in the IN variables.
    numberStr = str(model.Value[0])
    print(model.Id, numberStr)
    
    # Split betwen whole and decimal
    numberStrList = numberStr.split(".")
    wholeNum = numberStrList[0]
    
    
    # Check if there's an inch
    if len(numberStrList) == 2 and numberStrList[1] != "0":
        
    
        decimalNum = float("." + numberStrList[1])
        decimalNumInch = decimalNum * 12
        
     
        # Get the Fraction
        fractional = Fraction(decimalNumInch).limit_denominator()
        improperNum = fractional.numerator
        improperDeno = fractional.denominator
        
        # Inches mixed number
        mixedWhole = improperNum // improperDeno
        mixedNum = improperNum % improperDeno
        
        # # Check if it has fractional inch
        if decimalNumInch % 1 != 0:
          
            superscript = ""
            for num in str(mixedNum):
                superscript += numerator[num]
            
            subscript = ""
            for num in str(improperDeno):
                subscript += denominator[num]
                        
            
            # Set the value override
            if mixedWhole == 0: 
                mixedWhole = ""

            
            value = f"{wholeNum}'-{mixedWhole}{superscript}⁄{subscript}''"
            
            model.SetValueOverride([value])
        else:
            value = f"{wholeNum}'-{mixedWhole}''"
            model.SetValueOverride([value])
    else:
        # Only a whole number
        value = f"{wholeNum}'-0''"
        
        model.SetValueOverride([value])
        print("THIRD")
OUT = output.getvalue()