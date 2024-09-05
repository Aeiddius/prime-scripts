
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
t = Transaction(doc, "Dimensions")

t.Start()
sel = selection[0]
for i in sel.Segments:
	x = i.Origin.X
	y = i.Origin.Y
	z = i.Origin.Z
	i.TextPosition = XYZ(x+1, y-1, z)
	
t.Commit()