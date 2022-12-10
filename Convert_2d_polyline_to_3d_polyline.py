import arcpy
from datetime import datetime
import os


# This is used to execute code if the file was run but not imported
if __name__ == '__main__':
    # Tool parameter accessed with GetParameter or GetParameterAsText
    x = arcpy.GetParameterAsText(0)
    y = arcpy.GetParameterAsText(1)
    output_fc = arcpy.GetParameterAsText(2)
    convert_to_nad_83 = arcpy.GetParameter(3)

    arcpy.env.overwriteOutput = True

    sr = arcpy.SpatialReference(4326)

    arcpy.env.outputCoordinateSystem = sr

    project_dir = os.path.dirname(os.path.realpath(__file__))

    now = datetime.now()

    wgs_84_output = ""

    # if no output specified create shp
    if output_fc == "":
        project_dir = os.path.dirname(os.path.realpath(__file__))
        wgs_84_output = project_dir + "/" + "wgs84_pnt_" + now.strftime("%d_%b_%Y_%H_%M_%S") + ".shp"
        output_fc = wgs_84_output

    pnt = arcpy.Point(float(x), float(y))

    pnt_geometry = arcpy.PointGeometry(pnt)

    if not convert_to_nad_83:
        arcpy.CopyFeatures_management(pnt_geometry, output_fc)
    else:
        # convert to NAD 83 datum
        tmp = project_dir + "/" + "tmp_pnt_" + now.strftime("%d_%b_%Y_%H_%M_%S") + ".shp"
        arcpy.CopyFeatures_management(pnt_geometry, tmp)
        sr_out_nad_83 = arcpy.SpatialReference(4269)
        sr = arcpy.SpatialReference(4269)
        if output_fc == wgs_84_output:
            output_fc = project_dir + "/" + "nad83_pnt_" + now.strftime("%d_%b_%Y_%H_%M_%S") + ".shp"
        arcpy.management.Project(tmp, output_fc, sr_out_nad_83,
                                 transform_method="WGS_1984_(ITRF00)_To_NAD_1983")
        try:
            arcpy.management.Delete(tmp)
        except:
            arcpy.AddWarning("Failed to delete temporary file: " + tmp)

    # add to map if map active
    aprx = arcpy.mp.ArcGISProject('CURRENT')
    try:
        active_map = aprx.activeMap.name
        aprxMap = aprx.listMaps(active_map)[0]
        aprxMap.addDataFromPath(output_fc)
    except:
        pass
    
