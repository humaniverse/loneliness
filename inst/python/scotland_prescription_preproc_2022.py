import os
import pandas as pd
import requests
import scipy.stats as stats
import matplotlib.pyplot as plt

# Load data containing conditions associated with loneliness and their respective medications
loneliness_conditions_drugs = pd.read_csv("inst/extdata/drug_list.csv")

# URLs to Prescription in the Community csv files (2022)
# https://www.opendata.nhs.scot/dataset/prescriptions-in-the-community
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

# URLs for GP contact details csv files (2022)
# https://www.opendata.nhs.scot/dataset/gp-practice-contact-details-and-list-sizes
gp_details = [
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1a15cb34-fcf9-4d3f-ad63-1ba3e675fbe2/download/practice_contactdetails_oct2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/5273d444-5a79-4fad-a518-119a368e2161/download/practice_contactdetails_jul2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/8175c9ac-6953-4636-b151-f3946ef0fb80/download/practice_contactdetails_apr2022-open-data.csv",
    "https://www.opendata.nhs.scot/dataset/f23655c3-6e23-4103-a511-a80d998adb90/resource/1f76c338-7890-4ee7-b1bd-4d837cc1d50a/download/practice_contactdetails_jan2022.csv",
]


def code_condition(df):
    """
    Takes in the prescription in the community (pitc) dataframe and identifies loneliness related conditions based on prescription.
    Outputs a dataframe that multiplies loneliness related prescriptions by its count.
    Function is called in count_condition().
    """
    out = {}
    for illness in loneliness_conditions_drugs["illness"].unique():
        out[illness] = (
            df["BNFItemDescription"]
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
    return out.multiply(df["NumberOfPaidItems"], axis=0)


def count_condition():
    """
    Downloads each month of the prescription in the community CSV into a inst/extdata/pitc/
    Iterates over the monthly prescribing data to output an aggregated dataframe that sums number of prescriptions by illness type.
    Dataframe is grouped by GP practice.
    Runs code_condition().
    """

    # Download prescribing data into inst/extdata/pitc/ folder
    destination_folder = "inst/extdata/pitc"
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

    # Iterate over each monthly csv to count prescriptions
    monthly_data = []
    for file in os.listdir(destination_folder):
        prescribe = pd.read_csv(os.path.join(destination_folder, file))
        prescribe.columns = prescribe.columns.str.strip()
        prescribe = prescribe[["GPPractice", "BNFItemDescription", "NumberOfPaidItems"]]
        print(f" Proccessing {file}")

        # Count prescriptions
        loneliness_prescribing = code_condition(
            prescribe[["BNFItemDescription", "NumberOfPaidItems"]]
        )
        prescribe = prescribe.merge(
            loneliness_prescribing, left_index=True, right_index=True
        )
        del loneliness_prescribing

        # Group by GPPractice and sum prescriptions across the year
        summary = prescribe.groupby("GPPractice", as_index=False).agg(sum)
        monthly_data.append(summary)
        print(f" Completed processing {file}")

    # Concatenate all the monthly data together
    monthly_prescriptions = pd.concat(monthly_data, ignore_index=True)

    # Drop the duplicated entries
    monthly_prescriptions = monthly_prescriptions.drop_duplicates()
    print(
        f"All PITC monthly data successfully concatenated, length of df {len(monthly_prescriptions)}"
    )
    # Uncomment line below to save intermediary output as csv for testing purposes
    # monthly_prescriptions.to_csv("monthly_prescriptions.csv", index=False)

    return monthly_prescriptions


def add_postcode(monthly_prescriptions):
    """
    Iterates over quarterly GP contact details files and combines them.
    Takes in the df output from count_condition().
    Joins this with the GP contact details to output a df with prescription details that is summed by postcodes.
    """
    # Uncomment line below to read intermediary csv output for testing purposes
    # monthly_prescriptions = pd.read_csv("monthly_prescriptions.csv")

    # Download GP contact details data into inst/extdata/gp_details/ folder
    destination_folder = "inst/extdata/gp_details"
    os.makedirs(
        destination_folder, exist_ok=True
    )  # Create the destination folder if it doesn't exist

    for url in gp_details:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.basename(url)
            file_path = os.path.join(destination_folder, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
                print(f"{filename} successfully saved")
        else:
            print(f"Failed to download {url}")

    # Iterate over GP files and combine them
    gp_combine = []
    for file in os.listdir(destination_folder):
        gp_data = pd.read_csv(os.path.join(destination_folder, file))
        gp_data = gp_data.rename(columns={"PracticeCode": "GPPractice"})
        gp_combine.append(gp_data[["GPPractice", "Postcode"]])
    gp_data = pd.concat(gp_combine, ignore_index=True)
    print(f"GP contact details processed. Shape {gp_data.shape}")

    # Drop duplicates as contact details will be repeated across quarters
    gp_data = gp_data.drop_duplicates()

    # Subset monthly prescription data with GP practices that appear in the gp_data df as
    # monthly_prescription includes non GP practices e.g. pharamcies
    gp_ids = gp_data["GPPractice"].unique()
    monthly_prescriptions = monthly_prescriptions[
        monthly_prescriptions["GPPractice"].isin(gp_ids)
    ].copy()
    print(
        f"Shape of monthly_prescription once subsetted with GPs only: {monthly_prescriptions.shape}"
    )

    # Join GP details to prescription data
    monthly_prescriptions_postcodes = monthly_prescriptions.merge(
        gp_data, how="left", on="GPPractice"
    )
    monthly_prescriptions_postcodes["pcstrip"] = monthly_prescriptions_postcodes[
        "Postcode"
    ].str.replace(" ", "")

    # Sum values by postcode, to get the total prescriptions across the year
    monthly_prescriptions_postcodes = monthly_prescriptions_postcodes.groupby(
        ["pcstrip"], as_index=False
    ).sum()

    # Drop second instance of the two GP practices with two postcodes asigned to them
    monthly_prescriptions_postcodes = monthly_prescriptions_postcodes[
        ~monthly_prescriptions_postcodes.duplicated(subset="GPPractice", keep="first")
        | ~monthly_prescriptions_postcodes["GPPractice"].isin([2910096, 258060])
    ]
    monthly_prescriptions_postcodes = monthly_prescriptions_postcodes.drop(
        columns=["Postcode", "GPPractice", "BNFItemDescription"]
    )
    print(
        f"Postcodes added to monthly prescriptions. Number of  postcodes in merged df {len(monthly_prescriptions_postcodes)}"
    )
    # Uncomment line below to save intermediary output as csv for testing purposes
    # monthly_prescriptions_postcodes.to_csv("monthly_prescriptions_postcodes.csv", index=False)
    return monthly_prescriptions_postcodes


def illness_percentage(monthly_prescriptions_postcodes):
    """
    Creates columns in the DF per illness that is the percentage of drugs prescribed out of total drugs prescribed
    """
    # Uncomment line below to read intermediary csv output for testing purposes
    # monthly_prescriptions_postcodes = pd.read_csv("monthly_prescriptions_postcodes.csv")

    perc_cols = loneliness_conditions_drugs["illness"].unique()
    target_cols = perc_cols + "_perc"
    # Percentages for discrete illness groups out of total drugs prescribed
    monthly_prescriptions_postcodes[target_cols] = (
        monthly_prescriptions_postcodes[perc_cols].divide(
            monthly_prescriptions_postcodes["NumberOfPaidItems"], axis=0
        )
        * 100
    )
    print("Percentage calculations added")
    monthly_prescriptions_perc = monthly_prescriptions_postcodes

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
        monthly_prescriptions_perc[col_zscore] = stats.zscore(
            monthly_prescriptions_perc[col]
        )

    monthly_prescriptions_perc["loneliness_zscore"] = monthly_prescriptions_perc[
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
    loneliness_postcode.to_csv("inst/extdata/scotland_gp_2022.csv", index=False)
    print("Dataset saved as csv")


def build_preproc_scotland_2022():
    """
    Runs all functions required to build and save pre-processed scotland_gp_2022.csv in inst/extdata/.
    To be used as an input for scotland_idw_2022.py
    """
    monthly_prescriptions = count_condition()
    monthly_prescriptions_postcodes = add_postcode(monthly_prescriptions)
    monthly_prescriptions_perc = illness_percentage(monthly_prescriptions_postcodes)
    loneliness_postcode = standardise(monthly_prescriptions_perc)
    save_dataframe(loneliness_postcode)


if __name__ == "__main__":
    print("Running...")
    # Uncomment to test specific functions

    # count_condition()
    # add_postcode()
    # illness_percentage()
    # standardise()
    build_preproc_scotland_2022()
