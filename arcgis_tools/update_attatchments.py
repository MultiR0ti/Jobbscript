import pandas as pd
import numpy as np
import datetime as dt
import typing as t
from arcgis.features import GeoAccessor, FeatureLayer
from arcgis.gis import GIS
import arcpy

from pathlib import Path
import os

pgis = GIS("pro")

# Mappe
#png_folder = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-04 TEGNINGER\Kritiske profiler etter GRUS\PDF'

# Finds out which profiles are changed and returns a list of Sone name and profile number
def img_folder_items(png_folder):
    '''
    Returns a list of dictionaries that contains which profiles have new pictures
    '''
    items = []
    for item in os.listdir(png_folder):
        arcpy.AddMessage(item)
        # To fix Some weird bug 
        if 'pdf' in item:
            continue
        if item.split('.')[-1] == 'png':
            profilnr = item.split('_')[-1].split('.')[0]
            # If sone like 81_Brotnu_1.png
            if len(item.split('_')) < 4:
                sonenavn = item.split('_')[-2]
                sonedict = {
                    'profilnr': profilnr,
                    'sonenavn': sonenavn,
                    'attachment': png_folder+r'\\'+item
                    }
                items.append(sonedict)
            # If sone like 113_Holum_Nordre_4.png
            else:
                sonenavn = item.split('_')[-3] + '_'+ item.split('_')[-2] 
                sonedict = {
                    'profilnr': profilnr,
                    'sonenavn': sonenavn,
                    'attachment': png_folder + '\\' + item
                    }
                items.append(sonedict)

    return items

# Returns a list of objectid of which profiles that is going to update picture and the picture
def get_objectid(fl_hf, profiler):
    fl_features = fl_hf.query().features
    objectsandattachments = []
    for profil in profiler:
        nr, navn, attachment = profil.get('profilnr'), profil.get('sonenavn'), profil.get('attachment')
        arcpy.AddMessage(f'Finner profil {navn}_{nr}')
        # try:
        edit_feature = [f for f in fl_features if f.attributes['Profil_Sone'] == navn and f.attributes['Profil_Profilnummer'] == nr][0]
        # except Exception as e:
        # arcpy.AddMessage(f'Sammensvarer profil navn og nummer på bildet med linjenavnet i GIS? Bildet skal hete sonenr_sonenavn_profilnr, {type(e)}')

        print(edit_feature.attributes.get('OBJECTID'))
        oid = edit_feature.attributes.get('OBJECTID')
    
        updated_feature = edit_feature
        updated_feature.attributes['Layer'] = 'Oppdatert'
        update_res = fl_hf.edit_features(updates=[updated_feature])

        objectsandattachmentdict = {
            'objectid': oid,
            'attachment': attachment
                        }
        objectsandattachments.append(objectsandattachmentdict)
    return objectsandattachments


def update_attachments(feature_layer, objectsandattachments):
    arcpy.ResetProgressor()
    arcpy.SetProgressor('step', 'Processing features...', 0, len(objectsandattachments), 1)
    a_counter = 0
    #print(objectids[0], objectids[1])
    for odict in objectsandattachments:
        oid = odict.get('objectid')
        print(odict)
        attachment = odict.get('attachment')

        existing_attachments = feature_layer.attachments.get_list(oid=oid)
        if existing_attachments:
            for a in existing_attachments:
                a_id = a['id']
                a_counter += 1
                feature_layer.attachments.delete(oid, a_id)
                arcpy.AddMessage(f'Update attachement {a["name"]}')
                # Update the progressor label
                arcpy.SetProgressorLabel(f"Processing {oid}, {a_id}...")
                # Update the progressor position
                arcpy.SetProgressorPosition()
        else:
            arcpy.AddMessage(f'No attachement {oid}')
            
        feature_layer.attachments.add(oid, attachment)
        arcpy.AddMessage(f'Attachments updated: {a_counter}')



def main():
    input_lyr = arcpy.GetParameter(0)
    png_folder = arcpy.GetParameterAsText(1)

    service_url = input_lyr.connectionProperties["connection_info"]["url"]
    fl_url = service_url + "/" + input_lyr.connectionProperties["dataset"]
    fl_hf = FeatureLayer(fl_url)
    print(fl_hf)
    #fl_features = fl_hf.query().features

    #png_folder = r'\\nsv2-nasuni-01\Prosjekt\O10244\10244558-01\10244558-01-03 ARBEIDSOMRAADE\10244558-01 RIG\10244558-01-04 TEGNINGER\Kritiske profiler etter GRUS\PDF\images'
    #hf_ID = '65bd4723a3444a28adf20299799138c8'
    #fs_hf = pgis.content.get(hf_ID)
    #fl_hf = fs_hf.layers[0]

    items = img_folder_items(png_folder)
    print(items)
    objectsandattachments = get_objectid(fl_hf, items)
    update_attachments(fl_hf, objectsandattachments)
    

if __name__ == "__main__":
    main()