import pandas as pd
import pandasql as ps
import math
import re
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# propertyDF = pd.read_csv("property-tax-report.csv", sep=";")
# addressDF = pd.read_csv("property-addresses.csv", sep=";")
# censusDF = pd.read_csv("CensusLocalAreaProfiles2016.csv", encoding="ISO-8859-1")
# propertyDF2011 = pd.read_csv("property-tax-report-2006-2013.csv", sep=";")
census2006 = pd.read_csv("CensusLocalAreaProfiles2006.csv", encoding="ISO-8859-1")
census2011 = pd.read_csv("CensusLocalAreaProfiles2011.csv", encoding="ISO-8859-1")
# subset = propertyDF.sample(200000)
# addr_subset = addressDF.head(100000)
# prop2011subset = propertyDF2011.head(500000)


def mergePropTax(prop2016subset, prop2011subset):
    # defining the columns we will be keeping in the 2006-2013 property tax dataset
    cols_to_keep = ['PID', 'CURRENT_LAND_VALUE', 'CURRENT_IMPROVEMENT_VALUE', 'REPORT_YEAR' ]
    prop2011subset = prop2011subset[cols_to_keep]

    # dropping all columns where the years are not 2011 and 2016, respectively, in both property tax datasets
    temp_2011 = prop2011subset.drop(prop2011subset.loc[prop2011subset['REPORT_YEAR'] != 2011].index, inplace=False)
    temp_2016 = prop2016subset.drop(prop2016subset.loc[prop2016subset['REPORT_YEAR'] != 2016].index, inplace=False)
    # merging the two datasets on PID
    mergedPropertyDF = temp_2011.merge(temp_2016, on='PID', how='inner')
    mergedPropertyDF.dropna(axis=0, subset=['PID'], inplace=False)


    # getting the delta values by subtracting the two datasets (Note: the 2006-2013 property tax report dataset does not have any previous land value
    # or previous improvement value entries
    mergedPropertyDF['CURRENT_LAND_VALUE'] = mergedPropertyDF['CURRENT_LAND_VALUE_y'] - mergedPropertyDF['CURRENT_LAND_VALUE_x']
    mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE'] = mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE_y'] - mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE_x']
    mergedPropertyDF.reset_index(inplace=True, drop=True)
    return mergedPropertyDF


#mergePropTax(subset, prop2011subset)
def addCensus(data):
    mandarinColumn = []
    avgIncomeColumn = []
    lowIncomeColumn = []
    bachelorsDegreeColumn = []
    totalLabourForceColumn = []
    fullTimeWorkersColumn = []
    for row in data.itertuples():
        # i have no idea why region is _2
        # region also has trailing whitespace for some reason
        if row._2 is not None:
            region = row._2 + ' '

            # Mother tongue for mandarin is row 730 or id = 712
            num_mandarin = censusDF.iloc[728][region]
            mandarinColumn.append(num_mandarin)

            # Average income is row 1883, id = 1858, but need to go back 2? Using row 1881.
            num_income = censusDF.iloc[1881][region]
            avgIncomeColumn.append(num_income)

            # in low income is row 2506
            low_income = censusDF.iloc[2504][region]
            lowIncomeColumn.append(low_income)

            # bachelors degree is row 4254
            bachelors_degree = censusDF.iloc[4252][region]
            bachelorsDegreeColumn.append(bachelors_degree)

            # total labour force over the age of 15 is row 2233
            totalLabour_force = censusDF.iloc[2231][region]
            totalLabourForceColumn.append(totalLabour_force)

            #total people that worked full time in 2015 is row 2204
            fullTimeWorkers = censusDF.iloc[2202][region]
            fullTimeWorkersColumn.append(fullTimeWorkers)


        else:
            mandarinColumn.append(0)
            avgIncomeColumn.append(0)
            lowIncomeColumn.append(0)
            bachelorsDegreeColumn.append(0)
            totalLabourForceColumn.append(0)
            fullTimeWorkersColumn.append(0)

    data['native-mandarin'] = mandarinColumn
    data['avg-income'] = avgIncomeColumn
    data['low-income'] = lowIncomeColumn
    data['bachelors-degree'] = bachelorsDegreeColumn
    data['total-labour-force'] = totalLabourForceColumn
    data['full-time-workers'] = fullTimeWorkersColumn

    return

# pass in the dataframe and the year that you want to filter by
def filterByYear(df, year):
    filterYear = year
    df.drop(df.loc[df['REPORT_YEAR'] != filterYear].index, inplace=True)
    df.drop(df.loc[df['Geo Local Area'] == 0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return

def dropColumns(df):
    df.drop(['NARRATIVE_LEGAL_LINE1'], inplace=True, axis=1)
    df.drop(['NARRATIVE_LEGAL_LINE2'], inplace=True, axis=1)
    df.drop(['NARRATIVE_LEGAL_LINE3'], inplace=True, axis=1)
    df.drop(['NARRATIVE_LEGAL_LINE4'], inplace=True, axis=1)
    df.drop(['NARRATIVE_LEGAL_LINE5'], inplace=True, axis=1)
    df.drop(['BLOCK'], inplace=True, axis=1)
    df.drop(['DISTRICT_LOT'], inplace=True, axis=1)
    df.drop(['LOT'], inplace=True, axis=1)
    df.drop(['FROM_CIVIC_NUMBER'], inplace=True, axis=1)
    df.drop(['TO_CIVIC_NUMBER'], inplace=True, axis=1)
    df.drop(['NEIGHBOURHOOD_CODE'], inplace=True, axis=1)
    # df.drop(['PID'], inplace=True, axis=1)
    df.drop(['FOLIO'], inplace=True, axis=1)
    df.drop(['ZONE_NAME'], inplace=True, axis=1)
    df.drop(['PLAN'], inplace=True, axis=1)
    df.drop(['CIVIC_NUMBER'], inplace=True, axis=1)
    df.drop(['Geom'], inplace=True, axis=1)
    df.drop(['P_PARCEL_ID'], inplace=True, axis=1)
    df.drop(['PCOORD'], inplace=True, axis=1)
    df.drop(['SITE_ID'], inplace=True, axis=1)
    df.drop(['LAND_COORDINATE'], inplace=True, axis=1)
    df.drop(['STD_STREET'], inplace=True, axis=1)


def hotEncode(old_data):
    data_subset = pd.DataFrame()
    counter = 0
    for i in old_data:
        if (old_data[i].dtype == 'object' or len(old_data[i].unique()) < 20):
            encode = pd.get_dummies(old_data[i])
            for j in range(len(encode.columns)):
                encoded_name = encode.columns.values[j]
                encoded_columns_name = str(i) + "_" + str(encoded_name)
                data_subset.insert(counter + j, column=encoded_columns_name, value=encode[encoded_name], allow_duplicates=True)
            counter += len(encode.columns)
        else:
            data_subset.insert(counter, column=i, value=old_data[i])
            counter += 1
    return data_subset

def mergePropTax2006_2011(prop2011subset):
    # Making two subsets, one for data from 2006 and one for data from 2011
    subset_2011 = prop2011subset.drop(prop2011subset.loc[~prop2011subset['REPORT_YEAR'].isin([2011])].index, inplace=False)
    subset_2006 = prop2011subset.drop(prop2011subset.loc[~prop2011subset['REPORT_YEAR'].isin([2006])].index, inplace=False)

    # only keeping the columns we care about comparing between the years
    cols_to_keep = ['PID', 'CURRENT_LAND_VALUE', 'CURRENT_IMPROVEMENT_VALUE', 'REPORT_YEAR']
    subset_2006 = subset_2006[cols_to_keep]

    # merging the two datasets on PID
    mergedPropertyDF = subset_2006.merge(subset_2011, on='PID', how='inner')

    # getting the delta values by subtracting the two datasets
    mergedPropertyDF['CURRENT_LAND_VALUE'] = mergedPropertyDF['CURRENT_LAND_VALUE_y'] - mergedPropertyDF['CURRENT_LAND_VALUE_x']
    mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE'] = mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE_y'] - mergedPropertyDF['CURRENT_IMPROVEMENT_VALUE_x']

    print(mergedPropertyDF.shape)
    return mergedPropertyDF

def deltaCensus2006_2011(census2006, census2011):
    census2011.drop(['Vancouver CSD (City)'], inplace=True, axis=1)
    census2011.drop(['CMA of Vancouver'], inplace=True, axis=1)
    census2006.drop(['Vancouver CSD (City of Vancouver)'], inplace=True, axis=1)
    census2006.drop(['Vancouver CMA  (Metro Vancouver)'], inplace=True, axis=1)

    #population
    population2006 = (census2006.iloc[1,1:].str.replace(',','').to_frame().T).astype(int)
    population2011 = (census2011.iloc[0, 1:].str.replace(',','').to_frame().T).astype(int)

    deltaCensus = population2011.combine_first(population2006)
    deltaCensus.loc['deltaPopulation'] = deltaCensus.iloc[0] - deltaCensus.iloc[1]
    
    #married 
    married2006 = (census2006.iloc[76,1:].str.replace(',','').to_frame().T).astype(int)
    married2011 = (census2011.iloc[80, 1:].str.replace(',','').to_frame().T).astype(int)

    deltaCensus.loc['deltaMarried'] = married2011.iloc[0] - married2006.iloc[0]

    print(deltaCensus)
    # joinDF.to_csv(r'C:\Users\David\Desktop\ML\Van-Tax-Prop\test.csv')
    pass

deltaCensus2006_2011(census2006, census2011)

# merged_2006_2011 = mergePropTax2006_2011(prop2011subset)
# merged_2011_2016 = mergePropTax(subset, prop2011subset)

# sqlcode2 = '''
# select *
# from addr_subset
# inner join merged_2006_2011 on merged_2006_2011.LAND_COORDINATE=addr_subset.PCOORD
# '''
# newdf2 = ps.sqldf(sqlcode2, locals())

# sqlcode = '''
# select *
# from addr_subset
# inner join merged_2011_2016 on merged_2011_2016.LAND_COORDINATE=addr_subset.PCOORD
# '''
# newdf = ps.sqldf(sqlcode, locals())


# addCensus(newdf)
# dropColumns(newdf)
# newdf = pd.get_dummies(newdf, columns = ['ZONE_CATEGORY', 'Geo Local Area', 'LEGAL_TYPE'],
#                              prefix=['ZONE_CATEGORY', 'REGION', 'LEGAL_TYPE'])
