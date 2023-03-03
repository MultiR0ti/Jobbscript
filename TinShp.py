'''****************************************************************************
Name: TinTriangle Example
Description: This script demonstrates how to use the 
             TinTriangle tool to extract triangles from each TIN in the 
             target workspace.
****************************************************************************'''
# Import system modules
import arcpy
from arcpy import env
import exceptions, sys, traceback

try:
    arcpy.CheckOutExtension("3D")
    # Set environment settings
    env.workspace = r"C:/Users/jdr/TinPython/TIN-filer" #/_9_5_Bunn_Geophysix" # the target workspace
    # Create list of TINs
    TINList = arcpy.ListDatasets("*", "Tin")
    # Verify the presence of TINs in the list
    if TINList:
        for dataset in TINList:
            # Set Local Variables
            TINList = arcpy.ListDatasets("*", "Tin")
            slopeUnits = "PERCENT"
            zfactor = 1
            hillshade = "HILLSHADE 300, 45" # defines hillshade azimuth & angle
            tagField = "Tag"
            Output = dataset + "_triangles.shp" # name of the output file
            #Execute TinTriangle
            arcpy.ddd.TinTriangle(dataset, Output, slopeUnits, zfactor,
                                  hillshade, tagField)
            print("Finished.")
    else:
        print("There are no TIN(s) in the " + env.workspace + " directory.")
    arcpy.CheckInExtension("3D")
except arcpy.ExecuteError:
    print(arcpy.GetMessages())
except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # Concatenate error information into message string
    pymsg = 'PYTHON ERRORS:\nTraceback info:\n{0}\nError Info:\n{1}'\
          .format(tbinfo, str(sys.exc_info()[1]))
    msgs = 'ArcPy ERRORS:\n {0}\n'.format(arcpy.GetMessages(2))
    # Return python error messages for script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)