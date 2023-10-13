import os
import sys
import pandas as pd
import requests
import scipy.stats as stats
import matplotlib.pyplot as plt

# Load data containing conditions associated with loneliness and their respective medications
loneliness_conditions_drugs = pd.read_csv("inst/extdata/drug_list.csv")

# URLs to GP Prescribing Data (2022)
# https://www.data.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/gp-prescribing-data
pitc_urls = [
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/6d56613a-968b-4ebb-97f2-e19b637744a1/download/gp-prescribing---december-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/968d637e-073a-4b1a-a3e1-be9050c0fb36/download/08.-gp-prescribing---november-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/6b2b80a6-ea5d-419b-a7a3-89267c37c5c3/download/gp-prescribing---october-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/fb419ac5-21aa-4daf-b1a5-3f08d1339a09/download/gp-prescribing---september-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/93517fa2-1cd3-4640-a64f-c747748e3fce/download/gp-prescribing---august-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/9be6af28-ec9f-4b25-8760-19d439ec45cd/download/gp-prescribing---july-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/ceb972fd-1576-4738-a416-0f5a0f8e2927/download/gp-prescribing---june-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/c6647529-298f-49b3-a1bb-4d1b3bdcd315/download/gp-prescribing---may-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/2d8ade34-6ed0-4d9b-a909-7c3c738320c3/download/gp-prescribing-march-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/486c153c-a2dc-4275-994f-21c01763f4f6/download/gp-prescribing-february-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/a7b76920-bc0a-48fd-9abf-dc5ad0999886/resource/d255072d-58fe-4658-8180-86fee053e240/download/gp-prescribing-january-2022-v2.csv",
]

# URLs for GP Practice Contact Details and List Sizes csv files (2022)
# https://www.data.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/gp-practice-list-sizes
gp_details_ni = [
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/d8e77f57-120c-44d9-b360-f52e74ea4add/download/gp-practice-reference-file---october-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/5311b385-0551-4494-a3ac-cbbc5f84289c/download/gp-practice-reference-file--july-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/8f910a09-3cb6-4071-85c3-0e7677965de2/download/gp-practice-reference-file--april-2022.csv",
    "https://admin.opendatani.gov.uk/dataset/3d1a6615-5fc9-4f0e-ab2a-d2b0d71fb9ed/resource/80b06a43-2d1f-47c2-9142-7f46e9ea6e8b/download/gp-practice-reference-file--january-2022.csv",
]


def code_condition(df):
    """
    Takes in the GP Prescribing Data dataframe and identifies loneliness related conditions based on prescription.
    Outputs a dataframe that multiplies loneliness related prescriptions by its count.
    Function is called in count_condition().
    """
    out = {}
    for illness in loneliness_conditions_drugs["illness"].unique():
        out[illness] = (
            df["VTM_NM"]
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
    return out.multiply(df["Total Items"], axis=0)


def count_condition():
    """
    Downloads each month of the prescribing data CSV into a inst/extdata/pitc_ni/
    Iterates over the monthly prescribing data to output an aggregated dataframe that sums number of prescriptions by illness type.
    Dataframe is grouped by GP practice.
    Runs code_condition().
    """

    # Download prescribing data into inst/extdata/pitc_ni/ folder
    destination_folder = "inst/extdata/pitc_ni"
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
        prescribe = pd.read_csv(
            os.path.join(destination_folder, file),
            encoding="ISO-8859-1",
            low_memory=False,
        )
        prescribe.columns = prescribe.columns.str.strip()
        prescribe = prescribe[["Practice", "VTM_NM", "Total Items"]]
        print(f" Proccessing {file}")

        # Count prescriptions
        loneliness_prescribing = code_condition(prescribe[["VTM_NM", "Total Items"]])
        prescribe = prescribe.merge(
            loneliness_prescribing, left_index=True, right_index=True
        )
        del loneliness_prescribing

        # Group by Practice and sum prescriptions across the year
        summary = prescribe.groupby("Practice", as_index=False).agg(sum)
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

    # Download GP contact details data into inst/extdata/gp_details_ni/ folder
    destination_folder = "inst/extdata/gp_details_ni"
    os.makedirs(
        destination_folder, exist_ok=True
    )  # Create the destination folder if it doesn't exist

    for url in gp_details_ni:
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
        gp_data = gp_data.rename(columns={"PracNo": "Practice"})
        gp_combine.append(gp_data[["Practice", "Postcode"]])
    gp_data = pd.concat(gp_combine, ignore_index=True)
    print(f"GP contact details processed. Shape {gp_data.shape}")

    # Drop duplicates as contact details will be repeated across quarters
    gp_data = gp_data.drop_duplicates()

    # Subset monthly prescription data with GP practices that appear in the gp_data df as
    # monthly_prescription includes non GP practices e.g. pharamcies
    gp_ids = gp_data["Practice"].unique()
    monthly_prescriptions = monthly_prescriptions[
        monthly_prescriptions["Practice"].isin(gp_ids)
    ].copy()
    print(
        f"Shape of monthly_prescription once subsetted with GPs only: {monthly_prescriptions.shape}"
    )

    # Join GP details to prescription data
    monthly_prescriptions_postcodes = monthly_prescriptions.merge(
        gp_data, how="left", on="Practice"
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
        ~monthly_prescriptions_postcodes.duplicated(subset="Practice", keep="first")
        | ~monthly_prescriptions_postcodes["Practice"].isin(
            [2412, 6516, 6432, 900, 828]
        )
    ]
    monthly_prescriptions_postcodes = monthly_prescriptions_postcodes.drop(
        columns=["Postcode", "Practice", "VTM_NM"]
    )
    print(
        f"Postcodes added to monthly prescriptions. Number of  postcodes in merged df {len(monthly_prescriptions_postcodes)}"
    )
    # Uncomment line below to save intermediary output as csv for testing purposes
    # monthly_prescriptions_postcodes.to_csv(
    #     "monthly_prescriptions_postcodes.csv", index=False
    # )
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
            monthly_prescriptions_postcodes["Total Items"], axis=0
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
    loneliness_postcode.to_csv("inst/extdata/ni_gp_2022.csv", index=False)
    print("Dataset saved as csv")


def build_preproc_ni_2022():
    """
    Runs all functions required to build and save pre-processed ni_gp_2022.csv in inst/extdata/.
    To be used as an input for scotland_idw_2022.py
    """
    monthly_prescriptions = count_condition()
    monthly_prescriptions_postcodes = add_postcode(monthly_prescriptions)
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
    # add_postcode()
    # illness_percentage()
    # standardise()
    build_preproc_ni_2022()
