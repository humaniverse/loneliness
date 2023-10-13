import os
import sys
import pandas as pd
import requests
import scipy.stats as stats
import matplotlib.pyplot as plt
import zipfile as zp

# Load data containing conditions associated with loneliness and their respective medications
loneliness_conditions_drugs = pd.read_csv("inst/extdata/drug_list.csv")

# URLs to Prescribing Data (2022)
# https://nwssp.nhs.wales/ourservices/primary-care-services/general-information/data-and-publications/prescribing-data-extracts/general-practice-prescribing-data-extract/
pitc_urls = [
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-december-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-november-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-october-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-september-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-august-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-july-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-june-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-may-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-march-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-february-2022",
    "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/general-practice-prescribing-data-extract-docs/gp-data-extract-january-2022",
]

# URLs for list of GPs (2022)
# https://nwssp.nhs.wales/ourservices/primary-care-services/general-information/data-and-publications/prescribing-data-extracts/gp-practice-analysis/
gp_details_url = "https://nwssp.nhs.wales/ourservices/primary-care-services/primary-care-services-documents/gp-practice-analysis-docs/gp-practice-analysis-2022"


def code_condition(df):
    """
    Takes in the GP Prescribing Data dataframe and identifies loneliness related conditions based on prescription.
    Outputs a dataframe that multiplies loneliness related prescriptions by its count.
    Function is called in count_condition().
    """
    out = {}
    for illness in loneliness_conditions_drugs["illness"].unique():
        out[illness] = (
            df["BNFName"]
            .str.contains(
                "|".join(
                    loneliness_conditions_drugs[
                        loneliness_conditions_drugs["illness"] == illness
                    ]["medication"]
                ),
                case=False,
                regex=True,
            )
            .fillna(False)
            .astype("int16")
        )
    out = pd.DataFrame(out)
    return out.multiply(df["Items"], axis=0)


def count_condition():
    """
    Downloads each month of the prescribing zip folder into inst/extdata/pitc_wales/
    Iterates over the monthly prescribing data to count prescriptions and join GP postcodes to GP IDs.
    Outputs an aggregated dataframe that sums number of prescriptions by illness type, group by GP for the whole year of 2022.
    Runs code_condition().
    """

    # Download prescribing data into inst/extdata/pitc_wales/ folder
    destination_folder = "inst/extdata/pitc_wales/"
    os.makedirs(
        destination_folder, exist_ok=True
    )  # Create the destination folder if it doesn't exist

    for url in pitc_urls:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(url)
            file_path = os.path.join(destination_folder, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
                print(f"{filename} successfully saved")
        else:
            print(f"Failed to download {url}")

    # Define aggregation methods for use in loop
    agg_cols = {col: "sum" for col in loneliness_conditions_drugs["illness"].unique()}
    agg_cols["Items"] = "sum"
    for key in ["pcstrip", "Postcode"]:
        agg_cols[key] = "first"

    # Iterate over each zip folder; counts prescriptions and join to address file
    monthly_data = []
    for file in os.listdir(destination_folder):
        with zp.ZipFile(destination_folder + file) as zipf:
            zip_names = zipf.namelist()

            # Preprocess prescribing files
            prescribe_name = next(
                (filename for filename in zip_names if "GPData" in filename), None
            )
            prescribe = pd.read_csv(zipf.open(prescribe_name))
            prescribe.columns = prescribe.columns.str.strip()
            prescribe = prescribe[["PracticeID", "BNFName", "Items"]]
            ## Count prescriptions
            loneliness_prescribing = code_condition(prescribe[["BNFName", "Items"]])
            ## Merge dfs across the months
            prescribe = prescribe.merge(
                loneliness_prescribing, left_index=True, right_index=True
            )
            del loneliness_prescribing

            # Preprocess address files
            addr_name = next(
                (filename for filename in zip_names if "Address" in filename), None
            )
            addr = pd.read_csv(zipf.open(addr_name))
            addr = addr[["PracticeId", "Postcode"]]

            # Merge prescribing files and address files
            prescribe = prescribe.merge(
                addr, left_on="PracticeID", right_on="PracticeId"
            )
            del addr

            # Create uniform postcode field
            prescribe["pcstrip"] = prescribe["Postcode"].str.replace(" ", "")

            # Group by GP and sum prescriptions per month
            summary = prescribe.groupby("PracticeID", as_index=False).agg(agg_cols)
            del prescribe

            # Append each month to a list
            monthly_data.append(summary)
            print(f" Completed counting prescription and joining postcodes for {file}")

    # Concatenate all the monthly data together
    monthly_prescriptions = pd.concat(monthly_data, ignore_index=True)

    # Groupby practice ID to get sums across the year
    monthly_prescriptions = monthly_prescriptions.groupby(
        "PracticeID", as_index=False
    ).agg(agg_cols)

    print(
        f"All PITC monthly data successfully concatenated and grouped by practice, length of df {len(monthly_prescriptions)}"
    )
    # Uncomment line below to save intermediary output as csv for testing purposes
    # monthly_prescriptions.to_csv("monthly_prescriptions.csv", index=False)

    return monthly_prescriptions


def subset_gps(monthly_prescriptions):
    """
    Downloads list of GP codes and subsets the df output from count_condition() to include GPs only (excluding for e.g. pharmacies).
    """
    # Uncomment line below to read intermediary csv output for testing purposes
    # monthly_prescriptions = pd.read_csv("monthly_prescriptions.csv")

    # Download GP contact details data into inst/extdata/gp_details_wales/ folder
    destination_folder = "inst/extdata/gp_details_wales"
    os.makedirs(
        destination_folder, exist_ok=True
    )  # Create the destination folder if it doesn't exist

    response = requests.get(gp_details_url)
    if response.status_code == 200:
        filename = os.path.basename(gp_details_url)
        file_path = os.path.join(destination_folder, filename)
        with open(file_path, "wb") as file:
            file.write(response.content)
            print(f"{filename} successfully saved")
    else:
        print("Failed to download list of GPs")

    gp = pd.read_excel(file_path)
    gp_ids = gp.PracticeID.unique()
    prescriptions_gp = monthly_prescriptions[
        monthly_prescriptions["PracticeID"].isin(gp_ids)
    ].copy()
    print(
        f" Does length of the df equal unique number of practices? {len(prescriptions_gp) == gp.PracticeID.nunique()}"
    )

    # Uncomment line below to save intermediary output as csv for testing purposes
    # prescriptions_gp.to_csv("monthly_prescriptions_gps.csv", index=False)

    return prescriptions_gp


def illness_percentage(monthly_prescriptions_gps):
    """
    Creates columns in the DF per illness that is the percentage of drugs prescribed out of total drugs prescribed
    """
    # Uncomment line below to read intermediary csv output for testing purpose
    # monthly_prescriptions_gps = pd.read_csv("monthly_prescriptions_gps.csv")

    perc_cols = loneliness_conditions_drugs["illness"].unique()
    target_cols = perc_cols + "_perc"
    # Percentages for discrete illness groups out of total drugs prescribed
    monthly_prescriptions_gps[target_cols] = (
        monthly_prescriptions_gps[perc_cols].divide(
            monthly_prescriptions_gps["Items"], axis=0
        )
        * 100
    )
    print("Percentage calculations added")
    monthly_prescriptions_perc = monthly_prescriptions_gps

    # Uncomment line below to save intermediary output as csv for testing purposes
    # monthly_prescriptions_perc.to_csv("monthly_prescriptions_perc.csv", index=False)

    return monthly_prescriptions_perc


def standardise(monthly_prescriptions_perc):
    """
    Creates new columns that calculates the z-score per illness to standardise prescription relative to other practices.
    Creates a new column that sums each illness' z-score to compute a loneliness score.
    Creates a new column that ranks each postcode's loneliness score.
    Creates a new column that puts scores into deciles.
    Tidies up df.
    """
    # Uncomment line below to read intermediary csv output for testing purposes
    # monthly_prescriptions_perc = pd.read_csv("monthly_prescriptions_perc.csv")

    per_cols = [
        "depression_perc",
        "alzheimers_perc",
        "hypertension_perc",
        "diabetes_perc",
        "cardiovascular disease_perc",
        "insomnia_perc",
        "addiction_perc",
        "social anxiety_perc",
    ]

    for col in per_cols:
        col_zscore = col[:-5] + "zscore"
        monthly_prescriptions_perc[col_zscore] = stats.zscore(
            monthly_prescriptions_perc[col]
        )

    monthly_prescriptions_perc["loneliness_zscore"] = monthly_prescriptions_perc[
        [
            "depressionzscore",
            "alzheimerszscore",
            "hypertensionzscore",
            "diabeteszscore",
            "cardiovascular diseasezscore",
            "insomniazscore",
            "addictionzscore",
            "social anxietyzscore",
        ]
    ].sum(axis=1)
    monthly_prescriptions_perc.loneliness_zscore.hist(bins=100, figsize=(5, 2))
    plt.show()
    monthly_prescriptions_perc.rename(columns={"pcstrip": "postcode"}, inplace=True)
    loneliness_postcode = monthly_prescriptions_perc[["postcode", "loneliness_zscore"]]
    print(f"Loneliness z score added, shape of df {loneliness_postcode.shape}")
    return loneliness_postcode


def save_dataframe(loneliness_postcode):
    """
    Saves dataframe in extdata/ as csv
    """
    loneliness_postcode.to_csv("inst/extdata/wales_gp_2022.csv", index=False)
    print("Dataset saved as csv")


def build_preproc_wales_2022():
    """
    Runs all functions required to build and save pre-processed ni_gp_2022.csv in inst/extdata/.
    To be used as an input for scotland_idw_2022.py
    """
    monthly_prescriptions = count_condition()
    monthly_prescriptions_postcodes = subset_gps(monthly_prescriptions)
    monthly_prescriptions_perc = illness_percentage(monthly_prescriptions_postcodes)
    loneliness_postcode = standardise(monthly_prescriptions_perc)
    save_dataframe(loneliness_postcode)


if __name__ == "__main__":
    print("Running...")

    if sys.base_prefix != sys.prefix:
        venv_name = os.path.basename(sys.prefix)
        print(f"You are in a virtual environment - {venv_name}")
    else:
        print("You are not in a virtual environment. Activate your venev")

    # Uncomment to test specific functions

    # count_condition()
    # subset_gps()
    # illness_percentage()
    # standardise()
    build_preproc_wales_2022()
