'''MIT License

Copyright (c) 2018 David Hostetler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

import sys
import os
import shapefile
import lxml.etree as ET
import argparse

# Argument to provide help with Command Line arguments
parser = argparse.ArgumentParser(description='Creates a LandXML surface file ' \
                                 'based on reference polygon shapefile. ' \
                                 '\nPolgon shapefile should be created from' \
                                 'ESRI TIN Triangle tool.')
parser.add_argument('TIN_shp',help='Input polygon shapefile based on ESRI TIN')
parser.add_argument('Units',
                    choices=['ft','m','ft-int'],
                    help=('Input polygon shapefile units. Options are \n' \
                          'us survey feet (ft), meters (m) or ' \
                          'international feet (ft-int).'))
parser.parse_args()

tin_shp = sys.argv[1]
unit_len = sys.argv[2]

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

# Dictionary to define correct units based on input
unit_opt = {'ft':('Imperial', 'squareFoot', 'USSurveyFoot',
                  'cubicFeet', 'fahrenheit', 'inHG'),
            'm': ('Metric', 'squareMeter', 'meter',
                  'cubicMeter', 'celsius', 'mmHG'),
            'ft-int': ('Imperial', 'squareFoot', 'foot',
                       'cubicFeet', 'fahrenheit', 'inHG')}

# Define units here. Has not been tested with metric.
unit = ET.SubElement(units,
                     unit_opt[unit_len][0],
                     areaUnit=unit_opt[unit_len][1],
                     linearUnit=unit_opt[unit_len][2],
                     volumeUnit=unit_opt[unit_len][3],
                     temperatureUnit=unit_opt[unit_len][4],
                     pressureUnit=unit_opt[unit_len][5])

# Initializing output variables
pnt_dict = {}
face_list = []
cnt = 0

print('Processing...')

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

    # Check if too many or too few points created
    if len(shape_pnt_ids) != 3:
        print('Error - check input shapefile. '\
              'Must be a polygon with only three nodes for each shape.')
        sys.exit(0)

    # Reference face list for each shape
    face_list.append(shape_pnt_ids)

# Writing faces to landxml
for face in face_list:
    ET.SubElement(faces, 'F').text = f'{face[0]} {face[1]} {face[2]}'

# Writing output
tree = ET.ElementTree(landxml)
tree.write(out_xml, pretty_print=True, xml_declaration=True, encoding="iso-8859-1")
print(f'Successfully created {out_xml}. Check file output.')