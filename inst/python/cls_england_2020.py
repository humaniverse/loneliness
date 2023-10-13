import sys
import tempfile
import zipfile
import os
import requests
import pandas as pd
import numpy as np
import pathlib

# URLs for Community Life Survey (CLS) and OAC'11 to OA'11 lookup
cls_url = "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1149882/Community_Life_Survey_-_Strength_of_community_variables_by_Output_Area_Classifications_2017_18_to_2020_21.ods"
oa = "https://www.ons.gov.uk/file?uri=/methodology/geography/geographicalproducts/areaclassifications/2011areaclassifications/datasets/2011oacclustersandnamescsvv3.zip"


def get_lookup_files():
    """
    Calls geographr_lookup_feather() from lookup_feather.R to save two geographr feather files.
    R project files are temporarily ignored as a workaround to rpy2's conflict with R project files.
    """
    # Ignore R project files
    r_files = [".RData", ".RHistory", ".RProfile"]
    for rf in r_files:
        p = pathlib.Path.cwd() / rf
        try:
            p.rename(p.with_suffix(".ignore"))
        except FileNotFoundError:
            pass

    # Load lookup_feather.R
    import rpy2
    from rpy2 import robjects

    with open("inst/r/lookup_feather.R", "r") as r_script_file:
        r_script = r_script_file.read()
    robjects.r(r_script)

    # Call geographr_lookup_feather()
    geographr_lookups_r = robjects.globalenv["geographr_lookup_feather"]
    geographr_lookups_r()

    # Check feather files have been created
    print(
        f"lookup_11.feather saved? {'lookup_11.feather' in os.listdir('inst/extdata')}"
    )
    print(
        f"lookup_21.feather saved? {'lookup_21.feather' in os.listdir('inst/extdata')}"
    )

    # Reinstate R project files
    for rf in r_files:
        p = pathlib.Path.cwd() / rf
        p = p.with_suffix(".ignore")
        try:
            p.rename(p.with_suffix(""))
        except FileNotFoundError:
            pass


def process_cls():
    """
    Downloads Community Life Survey into temp folder.
    Isolates 2020/21 loneliness score
    """
    # Download data into temp folder
    response = requests.get(cls_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        print("CLS downloaded to:", temp_file_path)
    else:
        print("CLS failed to download.")

    # Read relevant sheet and tidy df
    df = pd.read_excel(
        temp_file_path, engine="odf", sheet_name="A6", skiprows=26, nrows=1
    )
    df.drop(columns=df.columns[:3], axis=1, inplace=True)
    df = (df.T).reset_index()
    df.rename(columns={"index": "oac_11", 0: "perc"}, inplace=True)
    df.drop(index=df.index[-1], axis=0, inplace=True)
    df["oac_11"] = df.oac_11.str[-2:]
    df.loc[
        19, "perc"
    ] = np.nan  # Replace no data (due to insufficent data points) with np.nan

    os.remove(temp_file_path)
    print(f"CLS processed, shape: {df.shape}")
    return df


def map_oac11_oa11(df):
    """
    Maps 2011 Output Area Classifcations clusters to 2011 Output Areas.
    Uses the output from process_cls()
    """
    # Download data into temp folder
    response = requests.get(oa)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip_file:
            temp_zip_file.write(response.content)
            temp_zip_file_path = temp_zip_file.name
        with zipfile.ZipFile(temp_zip_file_path, "r") as zip_file:
            with zip_file.open("2011 OAC Clusters and Names Excel v3.csv") as csv_file:
                oa_df = pd.read_csv(csv_file)
        print("OAC - OA lookup unzipped and downloaded to:", temp_zip_file_path)
    else:
        print("OAC - OA failed to download.")

    # Tidy lookup DF
    oa11 = oa_df[["Output Area Code", "Group Code"]]
    oa11.rename(
        columns={"Group Code": "oac_11", "Output Area Code": "oa11_code"}, inplace=True
    )

    # Join to cls
    df_oa = oa11.merge(df, on="oac_11", how="left")
    print("OA11 mapped to OAC11.")

    os.remove(temp_zip_file_path)
    return df_oa


def map_oa11_lsoa11(df_oa):
    """
    Maps 2011 Output Areas to 2011 Lower Super Output Areas using the lookup table saved in inst/extdata/ from the geographr package.
    Uses the output from map_oac11_oa11().
    """
    lsoa11 = pd.read_feather("inst/extdata/lookup_11.feather")
    lookup_lsoa11 = lsoa11[["lsoa11_code", "oa11_code"]]

    # Filter for England and unique combos of oa11_code and lsoa11_code
    lookup_lsoa11 = lookup_lsoa11[lookup_lsoa11["lsoa11_code"].str.startswith("E")]
    lookup_lsoa11 = lookup_lsoa11.drop_duplicates(subset=["oa11_code", "lsoa11_code"])

    # Join to LSOA11 code and get average per LSOA11
    df_lsoa11 = lookup_lsoa11.merge(df_oa, on="oa11_code", how="left")
    df_lsoa11.perc = df_lsoa11.perc.astype(float)
    df_lsoa11 = df_lsoa11.groupby(["lsoa11_code"], as_index=False)["perc"].mean()
    print(
        f"OA11 mapped to LSOA11. Are there 32,844 LSOAs (2011)? {df_lsoa11.lsoa11_code.nunique() == 32844}"
    )
    return df_lsoa11


def map_lsoa11_lsoa21(df_lsoa11):
    """
    Maps 2011 Lower Super Output Areas to 2021 Lower Super Output Areas using the lookup table saved in inst/extdata/ from the geographr package.
    Saves output as csv in inst/extdata/.
    Uses the output from map_oa11_lsoa11.
    """
    # Filter for England and unique combos of oa11_code and lsoa11_code
    lsoa21 = pd.read_feather("inst/extdata/lookup_21.feather")
    lookup_lsoa21 = lsoa21[lsoa21["lsoa11_code"].str.startswith("E")]
    lookup_lsoa21 = lookup_lsoa21.drop_duplicates(subset=["lsoa11_code", "lsoa21_code"])

    # Join to LSOA21 code and get average per LSOA21
    lookup_lsoa21 = lookup_lsoa21[["lsoa11_code", "lsoa21_code"]]
    loneliness = pd.merge(df_lsoa11, lookup_lsoa21, on="lsoa11_code", how="left")
    loneliness = loneliness[["lsoa21_code", "perc"]]
    loneliness = loneliness.groupby("lsoa21_code", as_index=False).mean()

    print(
        f"LSOA11 mapped to LSOA21. Are there 33,755 LSOAs (2021)? {len(loneliness) == 33755}"
    )
    loneliness.to_csv("inst/extdata/england_cls_loneliness_lsoa.csv", index=False)
    print("Dataset saved inst/extdata/england_cls_loneliness_lsoa.csv")


if __name__ == "__main__":
    print("Running...")

    if sys.base_prefix != sys.prefix:
        venv_name = os.path.basename(sys.prefix)
        print(f"You are in a virtual environment - {venv_name}")
    else:
        print("You are not in a virtual environment. Activate your venv")

    get_lookup_files()
    df = process_cls()
    df = map_oac11_oa11(df)
    df = map_oa11_lsoa11(df)
    map_lsoa11_lsoa21(df)
