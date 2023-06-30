import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.stats as stats

# Path to files
path = "data-raw/data-raw/Scotland/"

# Load drug illness and medication data
drug_data = pd.read_csv("data-raw/drug_list.csv")

# Column names
col_bnfname = "BNFItemDescription"
col_items = "NumberOfPaidItems"

def code_illness(df):
    """
    Takes in a prescription dataframe and identifies loneliness related illnesses based on prescription. 
    Outputs a dataframe that multiplies loneliness related prescriptions by its count.
    Function is called in count_illness().
    """
    out = {}
    for illness in drug_data['illness'].unique():
        out[illness] = df[col_bnfname].str.contains("|".join(drug_data[drug_data['illness'] == illness]['medication']), case=False, regex=True).fillna(False).astype('int16')
    out = pd.DataFrame(out)
    # Add loneliness related disease binary - avoids double counting some drugs
    out['loneliness'] = df[col_bnfname].str.contains("|".join(drug_data['medication'].unique()), case = False, regex = True).fillna(False).astype('int16')
    return out.multiply(df[col_items], axis=0)

def aggregation_cols():
    """ 
    Makes a dictionary of aggregation functions per column in DF.
    Function is called in count_illness(),
    """
    agg_cols = {col : 'sum' for col in drug_data['illness'].unique()}
    agg_cols[col_items] = 'sum'
    agg_cols['loneliness'] = 'sum'
    for key in ['Date', 'HBT']:
        agg_cols[key] = 'first'
    return agg_cols

def count_illness():
    """
    Iterates over the monthly prescribing data to output an aggregated dataframe that sums number of prescriptions by illness type. 
    Dataframe is grouped by GP practice. 
    Runs code_illness() and aggregation().
    """
    monthly_data = []

    #for file in os.listdir(path + "Prescriptions"):
    for file in ['pitc202201.csv', 'pitc202202.csv']:
        prescribe = pd.read_csv(path + "Prescriptions/" + file)
        prescribe.columns = prescribe.columns.str.strip()
        prescribe.rename(columns = {'PaidDateMonth': 'Date'}, inplace = True) 
        print(f' Proccessing {file}')
        
        # Count prescriptions
        loneliness_prescribing = code_illness(prescribe[[col_bnfname, col_items]])
        prescribe = prescribe.merge(loneliness_prescribing, left_index=True, right_index=True)
        del loneliness_prescribing

        # Group by GPPractice
        summary = prescribe.groupby('GPPractice', as_index=False).agg(aggregation_cols())
        monthly_data.append(summary)
        print(f' Completed {file}')

    # concatenate all the monthly data together
    data = pd.concat(monthly_data, ignore_index = True)
    print('DF concatenated')
    return data

def add_postcode(data):
    """
    Iterates over quarterly GP contact details files and combines them. 
    Takes in the df output from count_illness() and subsets it according to unique codes for GP surgeries.
    Joins this with the GP contact details to output a df with prescription details and postcodes.
    Dataframe is grouped by postcode.
    """
    gp_combine = []

    for file in os.listdir(path + "GP data"):
        gp_data = pd.read_csv(path + "GP data\\" + file)
        gp_data = gp_data.rename(columns = {'PracticeCode': 'GPPractice'})
        gp_combine.append(gp_data[['GPPractice','Postcode']])
    gp_data = pd.concat(gp_combine, ignore_index = True)
    
    # Get the unique codes for GP surgeries and subset the prescribing data according to these codes.
    gp_ids = gp_data['GPPractice'].unique()
    data = data[data['GPPractice'].isin(gp_ids)].copy()

    # Merge on the basis GPPractice code
    data = data.merge(gp_data, how = 'left', on = ['GPPractice'])
    data['pcstrip'] = data['Postcode'].str.replace("\s","").str.replace(" ","")
    data = data.drop(columns = ['Date','HBT','Postcode','GPPractice'])
    data = data.groupby(['pcstrip'], as_index = False).sum()
    print("Postcode added and DF grouped by postcode")
    return data

def illness_percentage(data):
    """
    Creates columns in the DF per illness that is the percentage of drugs prescribed out of total drugs prescribed
    """
    perc_cols = drug_data['illness'].unique()
    target_cols = perc_cols + '_perc'
    # Percentages for discrete illness groups out of total drugs prescribed
    data[target_cols] = data[perc_cols].divide(data[col_items], axis=0) * 100

    # Overall percentage for loneliness realted disease prescribing out of total drugs prescribed
    data['loneliness_perc'] = data['loneliness'].divide(data[col_items], axis=0) * 100
    print(data.head(2))
    print(f'Column names of the df: {data.columns}')
    return data

def standardise(data):
    """
    Creates new columns that calculates the z-score per illness.
    Creates a new column that sums each illness' z-score to compute a loneliness score.
    Creates a new column that ranks each postcode's loneliness score.
    Creates a new column that puts scores into deciles.
    Tidies up df.
    """
    per_cols = ['depression_perc', 'alzheimers_perc', 'blood pressure_perc', 'hypertension_perc', 
            'diabeties_perc', 'cardiovascular disease_perc', 'insomnia_perc', 'addiction_perc',
            'social anxiety_perc']

    for i, col in enumerate(per_cols):
        col_zscore = col[:-5] + 'zscore'  # New column name for Z-scores
        data[col_zscore] = stats.zscore(data[col])
    
    data['loneliness_zscore'] = data[[ 'depressionzscore', 'alzheimerszscore',
       'blood pressurezscore', 'hypertensionzscore', 'diabetieszscore',
       'cardiovascular diseasezscore', 'insomniazscore', 'addictionzscore', 
       'social anxietyzscore']].sum(axis=1)
    data['ranked'] = data['loneliness_zscore'].rank()
    data['deciles'] = pd.qcut(data['loneliness_zscore'], q=10, labels=False)
    data.rename(columns={'pcstrip':'postcode'}, inplace = True)
    data = data[['postcode','loneliness_zscore','ranked','deciles']]
    print(data.head(10))
    return data

def save_dataframe(data):
    """
    Saves dataframe in data folder.
    """
    data.to_csv("data/scotland_loneliness_2022.csv")
    print('Dataset saved')

def build_scotland2022():
    """
    Runs all functions required to build and save Scotland 2022 loneliness index in data/ folder.
    """
    df_illness = count_illness()
    df_illness_postcode = add_postcode(df_illness)
    df_percentage = illness_percentage(df_illness_postcode)
    df_final = standardise(df_percentage)
    save_dataframe(df_final)

if __name__ == "__main__":
    print('Testing...')
    #aggregation_cols()
    #count_illness()
    #add_postcode()
    #illness_percentage()
    #standardise()
    build_scotland2022()

