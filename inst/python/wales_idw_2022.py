import os
import sys
import tempfile
import zipfile
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.cm as cm
import geopandas as gpd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import mean_squared_error
from shapely.geometry import Point
import rasterio as rst
from rasterstats import zonal_stats

# Load loneliness scores by GP created by wales_prescription_preproc_2022.py
gp_postcode = pd.read_csv("inst/extdata/wales_gp_2022.csv")

# URL to National Statistics Postcode Lookup (NSPL)
nspl_url = "https://www.arcgis.com/sharing/rest/content/items/9ac0331178b0435e839f62f41cc61c16/data"

# URL to LSOA shape files
lsoa_boundaries_url = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LSOA_Dec_2021_Boundaries_Generalised_Clipped_EW_BGC_2022/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"


def create_gp_coordinate_geoframe():
    """
    Downloads National Statistics Postcode Lookup.
    Joins to gp_postcode to get coordinates per GP surgery.
    Returns a geoframe gp_geo used in subsequent functions.
    """
    # Download NSPL into temp folder and select relevant columns
    # print("Downloading NSPL...")
    # response = requests.get(nspl_url)
    # if response.status_code == 200:
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip_file:
    #         temp_zip_file.write(response.content)
    #         temp_zip_file_path = temp_zip_file.name
    #     with zipfile.ZipFile(temp_zip_file_path, "r") as zip_file:
    #         with zip_file.open("Data/NSPL_MAY_2022_UK.csv") as csv_file:
    #             nspl = pd.read_csv(csv_file, low_memory=False)
    #     print("NSPL unzipped and downloaded to:", temp_zip_file_path)
    # else:
    #     print("NSPL failed to download.")

    nspl = pd.read_csv(
        "C:/Users/JennaTan/Downloads/NSPL_MAY_2022_UK.csv", low_memory=False
    )

    nspl = nspl[["pcds", "oseast1m", "osnrth1m", "lsoa11", "msoa11"]]
    nspl["pcds"] = nspl.pcds.str.replace(" ", "")

    # Join gp_postcode to nspl
    gp_postcode.rename(columns={"postcode": "pcds"}, inplace=True)
    gp_coordinates = gp_postcode.merge(nspl, on="pcds", how="left")
    gp_coordinates.dropna(inplace=True)

    # Read df as Geodataframe
    gp_geo = gpd.GeoDataFrame(
        data=gp_coordinates,
        crs="epsg:27700",  # EPSG 27700 == British National Grid coords
        geometry=gp_coordinates.apply(
            lambda geom: Point(geom["oseast1m"], geom["osnrth1m"]), axis=1
        ),  # New column, "geometry" is created
    )
    print("gp_geo geodataframe created.")

    # Plot loneliness scores - check it is evenly distributed across Wales; note clusters around cities
    # gp_geo.plot(
    #     column="loneliness_zscore", scheme="quantiles", cmap="Blues", marker="."
    # )
    # plt.title(
    #     "Loneliness score by GP - evenly distributed; cluster around cities. Dark = high loneliness."
    # )
    # plt.show()

    return gp_geo


def create_idw_model(k, p):
    """
    Instantiates a KNN regressor as an IDW interpolater.
    k = no. of neighbours, p = power for idw calculation.
    Function is called in find_best_params() and predict_scores().
    Returns an instatiated model.
    """

    def _inv_distance_index(weights, index=p):
        """
        Weights set as distance from the input points and neighbour, with an inverse calculation of (1/dist**power).
        Values not dividable by 0 are ignored.
        """
        with np.errstate(divide="ignore", invalid="ignore"):
            safe_weights = 1.0 / weights**index
        return np.nan_to_num(safe_weights, posinf=0)  # ignore weights that are negative

    model = KNeighborsRegressor(k, weights=lambda x: _inv_distance_index(x, index=p))
    print("Model instantiated")

    return model


def find_best_params(gp_geo):
    """
    Finds best values of k and p for IDW model using Grid Search.
    Compares the mean squared error of predicted values for best values with default values of k and p.
    Takes gp_geo created in create_gp_coordinate_geoframe() as input and calls create_idw_model().
    Returns a dict of best k and best p value.
    """
    idw_model_params = create_idw_model(1, 1)
    print("IDW model instatiated with dummy variables")

    # Get existing point locations and values to fit the model from gp_geo
    points = gp_geo[["oseast1m", "osnrth1m"]].values
    vals = gp_geo["loneliness_zscore"].values
    print(np.isnan(points).sum(), np.isnan(vals).sum())
    print(len(vals), len(points))

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(
        points, vals, test_size=0.2, random_state=42
    )
    print(pd.isna(X_train).sum())
    print(pd.isna(y_train).sum())

    # Find best params
    param_grid = {"n_neighbors": [5, 8, 10], "p": [1, 1.5, 2]}
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(idw_model_params, param_grid, cv=kf, error_score="raise")
    grid_search.fit(X_train, y_train)

    best_k = grid_search.best_params_["n_neighbors"]
    best_p = grid_search.best_params_["p"]
    print("Best k:", best_k)
    print("Best p:", best_p)

    # Compare the MSE of the best params with the default params (k = 5, p = 2)
    grid = create_idw_model(best_k, best_p).fit(X_train, y_train)
    default = create_idw_model(5, 2).fit(X_train, y_train)
    y_pred_grid = grid.predict(X_test)
    y_pred_default = default.predict(X_test)
    print(f" Grid Search MSE: {mean_squared_error(y_test, y_pred_grid)}")
    print(f" Default params MSE: {mean_squared_error(y_test, y_pred_default)}")
    best_params = {"best_k": best_k, "best_p": best_p}
    return best_params


def create_grid(gp_geo):
    """
    Creates an evenly spaced grid of all possible x and y coords within the bounds of the data used for prediction.
    Ensures even spacing for uniform coverage of the surface for estimation.
    Takes gp_geo created in create_gp_coordinate_geoframe() as input.
    Returns xy grid array and xx, xmin and ymax - grid coordinates used for inputs in subsequent functions.
    """
    xmin_coords = gp_geo["oseast1m"].min()
    xmax_coords = gp_geo["oseast1m"].max()
    ymin_coords = gp_geo["osnrth1m"].min()
    ymax_coords = gp_geo["osnrth1m"].max()
    cellsize = 250

    # Adjust x and y ranges to be perfectly divisible by cellsize using floor and ceiling division, ensuring even spacing
    xmin = (xmin_coords // cellsize) * cellsize
    xmax = -(-xmax_coords // cellsize) * cellsize
    ymin = (ymin_coords // cellsize) * cellsize
    ymax = -(-ymax_coords // cellsize) * cellsize

    # Generate coords within adjusted min/max range with regular spacing determined by cellsize
    x = np.linspace(xmin, xmax, int((xmax - xmin) / cellsize))
    y = np.linspace(ymin, ymax, int((ymax - ymin) / cellsize))

    # Create grid structure of all possible x and y points, returns two 2D arrays
    xx, yy = np.meshgrid(x, y)

    # Reshape xx,yy into a single xy array by individually flattening  xx and yy into (1,n); converting to (n,1) then appending
    xy = np.append(xx.ravel()[:, np.newaxis], yy.ravel()[:, np.newaxis], 1)

    return xy, xx, xmin, ymax


def predict_scores(gp_geo, xy, xx, best_params):
    """
    Generate loneliness scores for values in the xy grid.
    Calls create_idw_model() using best_params from find_best_params().
    Takes output coords from create_grid() and gp_geo created in create_gp_coordinate_geoframe() as inputs.
    Returns predictions in a 2D array.
    """
    points = gp_geo[["oseast1m", "osnrth1m"]].values
    vals = gp_geo["loneliness_zscore"].values

    # Train and fit the idw model with best params
    best_model = create_idw_model(best_params["best_k"], best_params["best_p"])
    best_model.fit(points, vals)

    # Predict loneliness scores for coords in grid; returns 1D array (n,1)
    scores = best_model.predict(xy)

    # Reshape predictions to 2D array to align with xx,yy meshgrid
    scores_reshaped = np.flip(scores.reshape(np.shape(xx)), 0)
    print(scores_reshaped.shape)
    return scores_reshaped


def map_scores_to_lsoa(xmin, ymax, scores_reshaped):
    """
    Downloads LSOA boundaries shape file.
    Maps loneliness scores to LSOAs.
    Ranks LSOA and puts into deciles.
    Generates a map of Scotland, by deciles.
    Takes coordinates from create_grid() and scores_reshaped from predict_scores().
    Returns geo df with scores, rank and decile by lsoa.

    """
    # Download LSOA boundaries for England and Wales
    lsoa_coords = gpd.read_file(lsoa_boundaries_url)
    # Project coordinates onto British National Grid
    lsoa_coords.to_crs("epsg:27700")
    # Filter for Wales only
    lsoa_coords = lsoa_coords[lsoa_coords.LSOA21CD.str.startswith("W")]

    print(f"Are there 1,917 lsoas? lsoas: {lsoa_coords.LSOA21CD.nunique()}")

    # Define transformation to map row and columns from IDW model estimates to spatial coordinates
    trans = rst.Affine.from_gdal(xmin - 125, 250, 0, ymax + 125, 0, -250)

    # Get the mean predicted score based on MSOA polygon shape, returns a dictionary
    lsoa_score = zonal_stats(
        lsoa_coords["geometry"],
        scores_reshaped,
        affine=trans,
        stats="mean",
        nodata=np.nan,
    )

    # Extract score from dictionary, turn into a list and add as col in geodf
    lsoa_coords["loneliness_zscore"] = list(map(lambda x: x["mean"], lsoa_score))

    # Check histogram is normally distributed
    lsoa_coords["loneliness_zscore"].hist(bins=100, figsize=(5, 3))
    plt.title("Hist of Loneliness Score, averaged per lsoa - normally distributed")
    plt.show()

    # Create rank and decile columns
    lsoa_coords["rank"] = lsoa_coords["loneliness_zscore"].rank()
    lsoa_coords["deciles"] = pd.qcut(
        lsoa_coords["loneliness_zscore"], q=10, labels=False
    )

    # Generate map of Scotland with decile colours to check
    decile_values = lsoa_coords["deciles"].unique()
    cmap = cm.get_cmap(
        "YlGn", len(decile_values)
    )  # Generate colours based on number of decile values

    handles = []  # Create legend handles for each decile range
    for i, decile in enumerate(decile_values):
        col = cmap(i)
        handles.append(Patch(facecolor=col, label=f"Decile {decile}"))
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.axis("off")
    lsoa_coords.plot(column="deciles", ax=ax, legend=True)
    plt.title("Loneliness Decile by lsoa - 3 values missing")
    plt.show()

    print("lsoas without score do not have GP postcodes within its boundary.")

    return lsoa_coords


def save_geodataframe(lsoa_coords):
    """
    Save geodf as csv and geojson in inst/extdata/.
    """
    # Tidy geodf for csv
    lsoa_csv = lsoa_coords[["LSOA21CD", "loneliness_zscore", "rank", "deciles"]]
    lsoa_csv.rename(columns={"LSOA21CD": "lsoa21_code"}, inplace=True)
    lsoa_csv.to_csv("inst/extdata/ni_clinical_loneliness_lsoa.csv", index=False)
    print("CSV saved in inst/extdata.")

    # # Tidy geodf for geojson
    # iz_geojson = lsoa_coords[
    #     ["lsoa2021_cd", "loneliness_zscore", "rank", "deciles", "geometry"]
    # ]
    # iz_geojson.rename(columns={"lsoa2021_cd": "lsoa21_code"}, inplace=True)
    # iz_geojson.to_file(
    #     "inst/extdata/ni_clinical_loneliness_lsoa.geojson", driver="GeoJSON"
    # )


if __name__ == "__main__":
    print("Running...")

    if sys.base_prefix != sys.prefix:
        venv_name = os.path.basename(sys.prefix)
        print(f"You are in a virtual environment - {venv_name}")
    else:
        print("You are not in a virtual environment. Activate your venev")

    # gp_geo = create_gp_coordinate_geoframe()
    # best_params = find_best_params(gp_geo)
    # xy, xx, xmin, ymax = create_grid(gp_geo)
    # scores_reshaped = predict_scores(gp_geo, xy, xx, best_params)
    # lsoa_coords = map_scores_to_lsoa(xmin, ymax, scores_reshaped)
    # save_geodataframe(lsoa_coords)

    lsoa_coords = gpd.read_file(lsoa_boundaries_url)
    print(lsoa_coords.head(2))
    # Project coordinates onto British National Grid
    # lsoa_coords = lsoa_coords.to_crs(27700)
    print(lsoa_coords.head(2))
    # Filter for Wales only
    lsoa_coords = lsoa_coords[lsoa_coords.LSOA21CD.str.startswith("W")]
    print(lsoa_coords.head(5))
    print(lsoa_coords.columns)
    print(f"Are there 1,917 lsoas? lsoas: {lsoa_coords.LSOA21CD.nunique()}")
