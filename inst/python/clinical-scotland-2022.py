import os
import tempfile
import pandas as pd
import requests
import scipy.stats as stats

# Load loneliness related illness and medication data
drug_data = pd.read_csv("inst/extdata/drug_list.csv")

# URLs to Prescription in the Community csv files
pitc_urls = [
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/00213ffa-941e-4389-9e6f-3bca8067da8c/download/pitc202212.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/023986c0-3bb2-43cb-84e8-2e0b3bb1f55f/download/pitc202211.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/bd7bc2cf-4de5-4711-bd5a-9e3b77305453/download/pitc202210.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/9d0a518d-9d9c-4bcb-afd8-51f6abb7edf1/download/pitc202209.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/49fa5784-be06-4015-bc6d-9b5db8726473/download/pitc202208.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/26ce66f1-e7f2-4c71-9995-5dc65f76ecfb/download/pitc202207.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/debeadd8-2bbb-4dd3-82de-831531bab2cb/download/pitc202206.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/1b4e3200-b6e6-415f-b19a-b9ef927db1ab/download/pitc202205.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/7de8c908-86f8-45ac-b6a4-e21d1df30584/download/pitc202204.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/a0ec3bf2-7339-413b-9c66-2891cfd7919f/download/pitc202203.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/bd7aa5c9-d708-4d0b-9b28-a9d822c84e34/download/pitc202202.csv",
    "https://www.opendata.nhs.scot/dataset/84393984-14e9-4b0d-a797-b288db64d088/resource/53a53d61-3b3b-4a12-888b-a788ce13db9c/download/pitc202201.csv",
]

# URLs for GP contact details csv files
gp_details = [
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1a15cb34-fcf9-4d3f-ad63-1ba3e675fbe2/download/practice_contactdetails_oct2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/5273d444-5a79-4fad-a518-119a368e2161/download/practice_contactdetails_jul2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/8175c9ac-6953-4636-b151-f3946ef0fb80/download/practice_contactdetails_apr2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1f76c338-7890-4ee7-b1bd-4d837cc1d50a/download/practice_contactdetails_jan2022.csv",
]

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
    for illness in drug_data["illness"].unique():
        out[illness] = (
            df[col_bnfname]
            .str.contains(
                "|".join(drug_data[drug_data["illness"] == illness]["medication"]),
                case=False,
                regex=True,
            )
            .fillna(False)
            .astype("int16")
        )
    out = pd.DataFrame(out)
    # Add loneliness related disease binary - avoids double counting some drugs
    out["loneliness"] = (
        df[col_bnfname]
        .str.contains(
            "|".join(drug_data["medication"].unique()), case=False, regex=True
        )
        .fillna(False)
        .astype("int16")
    )
    return out.multiply(df[col_items], axis=0)


def aggregation_cols():
    """
    Makes a dictionary of aggregation functions per column in DF.
    Function is called in count_illness().
    """
    agg_cols = {col: "sum" for col in drug_data["illness"].unique()}
    agg_cols[col_items] = "sum"
    agg_cols["loneliness"] = "sum"
    for key in ["Date", "HBT"]:
        agg_cols[key] = "first"
    return agg_cols


def count_illness():
    """
    Downloads each month of the prescription in the community CSV into a temp folder.
    Iterates over the monthly prescribing data to output an aggregated dataframe that sums number of prescriptions by illness type.
    Dataframe is grouped by GP practice.
    Runs code_illness() and aggregation().
    """

    # Download prescribing data into temp folder
    temp_dir_pitc = tempfile.mkdtemp()
    for url in pitc_urls:
        filename = url.split("/")[-1]
        csv_path = os.path.join(temp_dir_pitc, filename)
        response = requests.get(url)
        if response.status_code == 200:
            with open(csv_path, "wb") as file:
                file.write(response.content)
            print(f"CSV file saved successfully in: {csv_path}")
        else:
            print(f"Failed to download {url}")

    # Iterate over each monthly csv to count prescriptions
    monthly_data = []
    for file in os.listdir(temp_dir_pitc):
        prescribe = pd.read_csv(csv_path)
        prescribe.columns = prescribe.columns.str.strip()
        prescribe.rename(columns={"PaidDateMonth": "Date"}, inplace=True)
        print(f" Proccessing {file}")

        # Count prescriptions
        loneliness_prescribing = code_illness(prescribe[[col_bnfname, col_items]])
        prescribe = prescribe.merge(
            loneliness_prescribing, left_index=True, right_index=True
        )
        del loneliness_prescribing

        # Group by GPPractice
        summary = prescribe.groupby("GPPractice", as_index=False).agg(
            aggregation_cols()
        )
        monthly_data.append(summary)
        print(f" Completed processing {file}")

    # concatenate all the monthly data together
    data = pd.concat(monthly_data, ignore_index=True)
    print(f"All PITC monthly data successfully concatenated, length of df {len(data)}")
    return data


def add_postcode(data):
    """
    Iterates over quarterly GP contact details files and combines them.
    Takes in the df output from count_illness() and subsets it according to unique codes for GP surgeries.
    Joins this with the GP contact details to output a df with prescription details and postcodes.
    Dataframe is grouped by postcode.
    """
    # Download GP data into temp folder
    temp_dir_gp = tempfile.mkdtemp()
    for url in gp_details:
        filename = url.split("/")[-1]
        csv_path = os.path.join(temp_dir_gp, filename)
        response = requests.get(url)
        if response.status_code == 200:
            with open(csv_path, "wb") as file:
                file.write(response.content)
            print(f"CSV file saved successfully in: {csv_path}")
        else:
            print(f"Failed to download {url}")

    # Iterate over GP files and combines them
    gp_combine = []
    for file in os.listdir(temp_dir_gp):
        gp_data = pd.read_csv(csv_path)
        gp_data = gp_data.rename(columns={"PracticeCode": "GPPractice"})
        gp_combine.append(gp_data[["GPPractice", "Postcode"]])
    gp_data = pd.concat(gp_combine, ignore_index=True)
    print("GP contact details processed")

    # Get the unique codes for GP surgeries and subset the prescribing data according to these codes.
    gp_ids = gp_data["GPPractice"].unique()
    data = data[data["GPPractice"].isin(gp_ids)].copy()

    data = data.merge(gp_data, how="left", on=["GPPractice"])
    data["pcstrip"] = data["Postcode"].str.replace("\s", "").str.replace(" ", "")
    data = data.drop(columns=["Date", "HBT", "Postcode", "GPPractice"])
    data = data.groupby(["pcstrip"], as_index=False).sum()
    print("Postcode added and df grouped by postcode")
    return data


def illness_percentage(data):
    """
    Creates columns in the DF per illness that is the percentage of drugs prescribed out of total drugs prescribed
    """
    perc_cols = drug_data["illness"].unique()
    target_cols = perc_cols + "_perc"
    # Percentages for discrete illness groups out of total drugs prescribed
    data[target_cols] = data[perc_cols].divide(data[col_items], axis=0) * 100

    # Overall percentage for loneliness realted disease prescribing out of total drugs prescribed
    data["loneliness_perc"] = data["loneliness"].divide(data[col_items], axis=0) * 100
    print(f"Percentage calculations added")
    return data


def standardise(data):
    """
    Creates new columns that calculates the z-score per illness.
    Creates a new column that sums each illness' z-score to compute a loneliness score.
    Creates a new column that ranks each postcode's loneliness score.
    Creates a new column that puts scores into deciles.
    Tidies up df.
    """
    per_cols = [
        "depression_perc",
        "alzheimers_perc",
        "blood pressure_perc",
        "hypertension_perc",
        "diabeties_perc",
        "cardiovascular disease_perc",
        "insomnia_perc",
        "addiction_perc",
        "social anxiety_perc",
    ]

    for col in per_cols:
        col_zscore = col[:-5] + "zscore"
        data[col_zscore] = stats.zscore(data[col])

    data["loneliness_zscore"] = data[
        [
            "depressionzscore",
            "alzheimerszscore",
            "blood pressurezscore",
            "hypertensionzscore",
            "diabetieszscore",
            "cardiovascular diseasezscore",
            "insomniazscore",
            "addictionzscore",
            "social anxietyzscore",
        ]
    ].sum(axis=1)
    data["ranked"] = data["loneliness_zscore"].rank()
    data["deciles"] = pd.qcut(data["loneliness_zscore"], q=10, labels=False)
    data.rename(columns={"pcstrip": "postcode"}, inplace=True)
    data = data[["postcode", "loneliness_zscore", "ranked", "deciles"]]
    print("Standardisation measures added")
    return data


def save_dataframe(data):
    """
    Saves dataframe in extdata folder as csv
    """
    data.to_csv("inst/extdata/clinical_scotland_2022.csv", index=False)
    print("Dataset saved as csv")


def build_scotland2022():
    """
    Runs all functions required to build and save Scotland 2022 loneliness index in inst/extdata/folder.
    """
    df_illness = count_illness()
    df_illness_postcode = add_postcode(df_illness)
    df_percentage = illness_percentage(df_illness_postcode)
    df_final = standardise(df_percentage)
    save_dataframe(df_final)


if __name__ == "__main__":
    print("Running...")
    # aggregation_cols()
    # count_illness()
    # add_postcode()
    # illness_percentage()
    # standardise()
    build_scotland2022()
