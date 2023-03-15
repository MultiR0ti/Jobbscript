import pandas as pd
import numpy as np
import openpyxl
import sklearn
from sklearn import linear_model


class SndfilTilML:
    
    # Takes a SND_File and an excel file
    def __init__(self, snd_file, excel_file):
        self.snd_file = snd_file
        self.excel_file = excel_file
        self.borid = snd_file.split('.')[0]

        #self.exceldf = pd.read_excel(excel_file, self.borid , usecols="A:E")


    def clean_snd_df(self):
        #csv_file = 'SS-12026.SND'
        df0 = pd.read_csv(self.snd_file, encoding='unicode_escape')

        #Find out where the data starts
        startIndex = np.where(df0[df0.columns[0]].str.contains(self.borid))[0].item(0)
        df1 = df0.drop(df0.index[:startIndex+1])
        df1.reset_index(inplace=True)

        # Find out where data ends
        endIndex = np.where(df1[df1.columns[1]].str.contains('\*'))[0].item(0)
        df = df1.iloc[:endIndex,-1].to_frame()



        # Remove spaces
        df[df.columns[0]] = df[df.columns[0]].str.replace(" ","Z")
        df[df.columns[0]] = df[df.columns[0]].str.replace("ZZZZZ","Q")
        df[df.columns[0]] = df[df.columns[0]].str.replace("ZZZZ","Q")
        df[df.columns[0]] = df[df.columns[0]].str.replace("ZZZ","Q")
        df[df.columns[0]] = df[df.columns[0]].str.replace("ZZ","Q")
        df[df.columns[0]] = df[df.columns[0]].str.replace("Z","Q")
        df[df.columns[0]] = df[df.columns[0]].str.replace("Q"," ")

        # Make columns 
        dfs = df[df.columns[0]].str.split(' ', expand=True)
        dfs = dfs.iloc[:, 1:]



        columns = ['Dybde', 'Trykk', 'Bortid', 'Spyle']

        dfs.rename(columns={ dfs.columns[0]: 'Dybde', dfs.columns[1] : 'Trykk', dfs.columns[2] : 'Bortid', dfs.columns[3] : 'Spyle' }, inplace = True)

        #for i, col in enumerate(columns):
        #   print(col)
        #    dfs.rename(columns={ df.columns[i]: col }, inplace = True)


        # Find indexes for start and stop flushing etc.
        startY = []
        endY = []
        startS = []
        endS = []
        startR = []
        endR = []
        for col in dfs.columns:
            startY.extend(np.where(dfs[col].str.contains('Y1'))[0].tolist())
            endY.extend(np.where(dfs[col].str.contains('Y2'))[0].tolist())
            startS.extend(np.where(dfs[col].str.contains('S1'))[0].tolist())
            endS.extend(np.where(dfs[col].str.contains('S2'))[0].tolist())
            startR.extend(np.where(dfs[col].str.contains('R1'))[0].tolist())
            endR.extend(np.where(dfs[col].str.contains('R2'))[0].tolist())
        startY.sort()
        endY.sort()
        startS.sort()
        endS.sort()
        startR.sort()
        endR.sort()

        # Add binary values for hammering, rotation and flushing. 1 = on 0 = off.

        for spyl in range(len(endS)):           
            dfs.loc[startS[spyl]:endS[spyl],"S(spyling?)"] = '1'
        dfs.loc[startS[-1]:,"S(spyling?)"] = '1'

        for rot in range(len(endR)):
            dfs.loc[startR[rot]:endR[rot],"R(rotasjon?)"] = '1'
        dfs.loc[startR[-1]:,"R(rotasjon?)"] = '1'

        for slag in range(len(endY)):
            dfs.loc[startY[slag]:endY[slag],"Y(slag?)"] = '1'
        dfs.loc[startY[-1]:, "Y(slag?)"] = '1'

        dfs = dfs.fillna(0)
        dfs.replace(0, '0')
        
        # Returned dataframe
        newdf = dfs[['Dybde', 'Trykk', 'Bortid', 'Spyle', 'S(spyling?)', 'R(rotasjon?)', 'Y(slag?)']]
        newdf.insert(7, "Tolkning", "Tolkning")
        snddf = newdf.iloc[:-1 , :]

        # Dataframe for comments
        for i in range(5,10):
            dfs[i] = dfs[i].values.astype(str)
            dfs[i] = dfs[i].replace('0', '')
        dfs['kommentarer'] = dfs[[5, 6, 7, 8, 9]].agg(' '.join, axis=1)
        kommentarer = dfs['kommentarer'].to_frame()

        return snddf



    def to_ml_tolk(self, snddf):
        
        #wb = openpyxl.load_workbook(self.excel_file)
        #sheet = wb.active
        
        # Get layer type from excel sheets
        exceldf = pd.read_excel(self.excel_file, self.borid , usecols="A:E")
        for i in range(len(exceldf['Start'])):
            snddf.loc[exceldf.loc[i]['Start']*40:exceldf.loc[i]['End']*40,'Tolkning'] = exceldf.loc[i]['Geology']
            



        # THIS ONLY WORKS IF THERE IS ONLY 1 SND FILE BECAUSE LAYERS CAN BE MISSING E.G. IN OTHER FILES
        '''
        tolkdict = {}
        layers = pd.unique(exceldf['Geology'])
        for i, layer in enumerate(layers):
            tolkdict[layer] = i
       '''
        tolkdict1 = {
            'Topplag' : 0,
            'Leire' : 1,
            'Morene' : 2,
            'Sand' : 3,
            'Berg' : 4
        }


        # Convert layer type to integers so that the ML can learn.
        for item in tolkdict1:
            snddf['Tolkning'] = snddf['Tolkning'].replace(item, tolkdict1[item])



        return snddf, tolkdict1


    # Translate back to layers
    def to_human_tolk(self, snddf, tolkdict):
        for i, item in enumerate(tolkdict):
            snddf['Tolkning'] = snddf['Tolkning'].replace(i, list(tolkdict.keys())[list(tolkdict.values()).index(i)])
            

        soil_layers = snddf[snddf["Tolkning"].shift() != snddf["Tolkning"]]
        max_depth = snddf['Dybde'].iat[-1]

        layers = soil_layers['Tolkning'].reset_index(drop=True)
        starts = soil_layers['Dybde'].reset_index(drop=True)
        ends = starts.iloc[1:].to_frame().reset_index(drop=True)
        ends.loc[len(ends.index)] = max_depth

        data = pd.DataFrame(starts, columns=['Start'])
        data['Start'] = starts
        data['Ends'] = ends
        data['Geology'] = layers


        return snddf, data

bornr12027 = SndfilTilML('SS-12027.SND', 'TestTolkning.xlsx')

snddf12027 = bornr12027.clean_snd_df()
ml_tolk12027 = bornr12027.to_ml_tolk(snddf12027)[0]
layers_dict = bornr12027.to_ml_tolk(snddf12027)[1]
#print(layers_dict)
#human_tolk = snddfOOP.to_human_tolk(ml_tolk, layers_dict)

bornr12021 = SndfilTilML('SS-12021.SND', 'TestTolkning.xlsx')
snddf12021 = bornr12021.clean_snd_df()
ml_tolk12021 = bornr12021.to_ml_tolk(snddf12021)[0]
#print(snddf12021)





samlet = [ml_tolk12021, ml_tolk12027]
samsamlet = pd.concat(samlet)

samsamlet.to_excel('TestTolkning1.xlsx', 'SS-12021', startcol=2)

predict = 'Tolkning'
x_data = np.array(samsamlet.drop(columns=[predict]))
y_fasit = np.array(samsamlet[predict])
x_data_train, x_data_test, y_fasit_train, y_fasit_test = sklearn.model_selection.train_test_split(x_data, y_fasit, test_size= 0.25)

linear = linear_model.LinearRegression()
linear.fit(x_data_train, y_fasit_train)
acc = linear.score(x_data_test, y_fasit_test)

print(acc)

predictions = linear.predict(x_data_test)

for x in range(len(predictions)):
    print(round(predictions[x]), x_data_test[x], y_fasit_test[x])

#print(snddf12021)

predictionsNewProfile = linear.predict(np.array(snddf12021.drop(columns=[predict]))).round()

snddf12021['Tolkning'] = pd.DataFrame(predictionsNewProfile)

print(bornr12021.to_human_tolk(snddf12021, layers_dict))

print(bornr12021.to_human_tolk(snddf12021, layers_dict)[1])

#bornr12021.to_human_tolk(snddf12021, layers_dict).to_excel('TestTolkning1.xlsx', 'SS-12021', startcol=6)





