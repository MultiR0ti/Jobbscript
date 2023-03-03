import pandas as pd

class TotfilTilML:

    def clean_tot_df(csvfile):
        df = pd.read_csv(csvfile, encoding='unicode_escape', skiprows=1).loc['#':].iloc[1:]
        newdf = df[df.columns[0]].str.split('=', expand=True)[1]
        
        for col in df.columns[1:10]:
            splitdf = df[col].str.split('=', expand=True)
            newdf = pd.concat([newdf, splitdf[1]], axis=1)

        newdf.columns = ['Dybde(D)', 'Matekraft(A)', 'Bortid(B)', 'Slag(AP)', 'Rotasjonshastighet(R)', 'P', 'Spyletrykk(I)', 'SP', 'J', 'T']    
        newdf.insert(10, "Tolkning", "Tolkning")

        return newdf


    def tolkning(df):
        df.loc[0:40,'Tolkning'] = 'Tørrskorpe'
        df.loc[40:140,'Tolkning'] = 'Leire'
        df.loc[140:340,'Tolkning'] = 'Morene'
        df.loc[340:580,'Tolkning'] = 'Sand'
        df.loc[580:620,'Tolkning'] = 'Morene'
        df.loc[620:736,'Tolkning'] = 'Berg'
        df.loc[737,'Tolkning'] = 'Stopp'
        return df

