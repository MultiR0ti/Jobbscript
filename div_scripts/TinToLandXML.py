import sys
import os
import shapefile
import lxml.etree as ET


# Input polygon shapefile converted from TIN surface
tin_shp = r'\\nsv2-nasuni-01\Prosjekt\O10223\10223695-11\10223695-11-03 ARBEIDSOMRAADE\10223695-11 RIG\10223695-11-05 MODELLER\TIN\Gjerdrum_kyken_2023_0505_tin_triangles.shx'

# Outputs
out_xml = os.path.splitext(tin_shp)[0]+'_Surface.xml'
surf_name = os.path.splitext(os.path.basename(tin_shp))[0]

# Reading input TIN shapefile using PyShp
in_shp = shapefile.Reader(tin_shp)
shapeRecs = in_shp.shapeRecords()

# Initializing landxml surface items
landxml = ET.Element('LandXML')
units = ET.SubElement(landxml, 'Units')
surfaces = ET.SubElement(landxml, 'Surfaces')
surface = ET.SubElement(surfaces, 'Surface', name=surf_name)
definition = ET.SubElement(surface, 'Definition',
                           surfType="TIN")
pnts = ET.SubElement(definition, 'Pnts')
faces = ET.SubElement(definition, 'Faces')


# Change units here if using meters or international feet
unit_metric = ET.SubElement(units,
                              'Metric',
                              areaUnit="squareMeter",
                              linearUnit="meter",
                              volumeUnit="cubicMeter",
                              temperatureUnit="celcius",
                              pressureUnit="mmHG")

# Initializing output variables
pnt_dict = {}
face_list = []
cnt = 0

# Creating reference point dictionary/id for each coordinate
# As well as LandXML points, and list of faces
for sr in shapeRecs:
    shape_pnt_ids = []   # id of each shape point

    # Each shape should only have 3 points
    for pnt in range(3):   
        # Coordinate with y, x, z format
        coord = (sr.shape.points[pnt][1],
                 sr.shape.points[pnt][0],
                 sr.shape.z[pnt])

        # If element is new, add to dictionary and
        # write xml point element
        if coord not in pnt_dict:
            cnt+=1
            pnt_dict[coord] = cnt

            shape_pnt_ids.append(cnt)  # Add point id to list 

            # Individual point landxml features
            pnt_text = f'{coord[0]:.5f} {coord[1]:.5f} {coord[2]:.3f}'
            pnt = ET.SubElement(pnts, 'P', id=str(cnt)).text = pnt_text

        # If point is already in the point dictionary, append existing point id
        else:
            shape_pnt_ids.append(pnt_dict[coord])

    # Reference face list for each shape
    face_list.append(shape_pnt_ids)

# Writing faces to landxml
for face in face_list:
    ET.SubElement(faces, 'F').text = f'{face[0]} {face[1]} {face[2]}'


# Writing output
tree = ET.ElementTree(landxml)
tree.write(out_xml, pretty_print=True, xml_declaration=True, encoding="iso-8859-1")