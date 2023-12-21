#!/usr/bin/env python
# coding: utf-8

# # Workflow generating input for deployment of Demoland for a custom area in England
#
# Requires:
#
# - Area of interest defined in a GDAL-readable file. All geometries present in the file are considered a part of the AOI.
# - GTFS data file

# 1. Get the extent of AoI

import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile
from glob import glob
from itertools import product

import geopandas as gpd
import h3
import joblib
import numpy as np
import pandas as pd
import requests
import tracc
import xarray as xr
from demoland_engine.indicators import Accessibility, Model
from libpysal import graph
from r5py import TransportMode, TransportNetwork, TravelTimeMatrixComputer


def main():
    # ## Input

    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 5:
        print(
            "Incorrect input.",
            f"{len(sys.argv)} args given: {sys.argv}"
        )
        sys.exit(1)

    # Get input values from command-line arguments
    area_name = sys.argv[1]
    name = sys.argv[2]
    aoi_file_path = f"data/{sys.argv[3]}"
    gtfs_data_file_path = f"data/{sys.argv[4]}"

    print(f"""
    Generating demoland data for {area_name}

    name: {name}
    area of interest: {aoi_file_path}
    GTFS data: {gtfs_data_file_path}
    """)

    start = dt.datetime.now()

    # ## Pipeline
    #
    # Create folders
    print("1/13: Create temporary directories")
    app_folder = tempfile.mkdtemp()
    os.mkdir(f"{app_folder}/scenarios")
    engine_folder = tempfile.mkdtemp()
    os.mkdir(f"{engine_folder}/{name}")
    temp_folder = tempfile.mkdtemp()

    # Set date to the nearest monday in past (or today if monday is today)

    today = dt.datetime.now()
    days_to_monday = today.weekday() - 0  # Monday is 0
    if days_to_monday < 0:
        monday = today
    else:
        monday = today - dt.timedelta(days=days_to_monday)
    date_time = f"{monday.year},{monday.month},{monday.day},9,30"

    # Load the AOI
    print("2/13: Load AOI")
    aoi = gpd.read_file(aoi_file_path)
    aoi_poly = aoi.to_crs(27700).unary_union

    # 2. Get H3 grid with the data for the AoI

    # Read the full grid
    print("3/13: Read the full grid")
    grid = gpd.read_parquet("grid_complete.parquet")

    # Get a portion of the grid covering AoI.
    print("4/13: Get a portion of the grid covering AoI.")
    grid_aoi = grid.iloc[grid.sindex.query(aoi_poly, predicate="intersects")].copy()
    grid_aoi[["lat", "lon"]] = pd.DataFrame(
        grid_aoi.index.to_series().apply(h3.h3_to_geo).tolist(),
        columns=["lat", "lon"],
        index=grid_aoi.index,
    )

    grid_aoi = grid_aoi.dropna(subset="signature_type")

    # 3. Make predictive models ready
    #
    # Read the full matrix and subset it for AOI
    
    print("5/13: Read the full matrix and subset it for AOI")
    matrix = graph.read_parquet(
        "grid_adjacency_binary.parquet"
    ).transform("r")

    matrix_aoi = matrix.subgraph(grid_aoi.index)

    matrix_aoi.to_parquet(f"{engine_folder}/{name}/matrix.parquet")

    # 5. Make accessibility ready
    #     6. Get GTFS
    #
    # Go to https://data.bus-data.dft.gov.uk/downloads/, register and download timetable data for your region in GTFS data format.

    gtfs_data_file = gtfs_data_file_path

    # 7. Get network from OSM
    #
    # Download a fresh OSM snapshot for England.
    print("6/13: Download a fresh OSM snapshot for England.")
    r = requests.get(
        "http://download.geofabrik.de/europe/united-kingdom/england-latest.osm.pbf"
    )
    with open(f"{temp_folder}/england-latest.osm.pbf", "wb") as f:
        f.write(r.content)

    # Extract the AoI. We need a GeoJSON of the area.

    aoi.dissolve().to_file(f"{temp_folder}/aoi.geojson")

    # And then can use osmium to get an extract.
    print("7/13: Use osmium to get an extract.")
    # Define the command
    command = f"osmium extract -p {temp_folder}/aoi.geojson {temp_folder}/england-latest.osm.pbf -o {temp_folder}/aoi.osm.pbf"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

    # 8. Get OS Greenspace
    print("8/13: Get OS Greenspace")
    r = requests.get(
        "https://api.os.uk/downloads/v1/products/OpenGreenspace/downloads?area=GB&format=GeoPackage&redirect"
    )
    with open(f"{temp_folder}/opgrsp_gpkg_gb.zip", "wb") as f:
        f.write(r.content)

    # Read the file.

    with zipfile.ZipFile(f"{temp_folder}/opgrsp_gpkg_gb.zip", "r") as zip_ref:
        with zip_ref.open("Data/opgrsp_gb.gpkg") as gsp:
            f = gsp.read()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                
                greenspace_sites = gpd.read_file(
                    f, engine="pyogrio", layer="greenspace_site"
                )
                greenspace_access = gpd.read_file(f, engine="pyogrio", layer="access_point")

    # Extract the AoI

    greenspace_sites_aoi = greenspace_sites.iloc[
        greenspace_sites.sindex.query(aoi_poly, predicate="intersects")
    ]
    greenspace_access_aoi = greenspace_access.iloc[
        greenspace_access.sindex.query(aoi_poly, predicate="intersects")
    ]

    # 9. Process OS Greenspace
    print("9/13: Process OS Greenspace")
    greenspace_sites_select = greenspace_sites_aoi.query(
        "function!='Allotments Or Community Growing Spaces' & function!='Golf Course' & function!='Bowling Green'"
    )
    publicpark = greenspace_sites_select.query("function=='Public Park Or Garden'")
    playingfield = greenspace_sites_select.query("function=='Playing Field'")
    othersport = greenspace_sites_select.query("function=='Other Sports Facility'")
    therest = greenspace_sites_select.query(
        "function!='Playing Field' & function!='Public Park Or Garden' & function!='Other Sports Facility'"
    )

    # find 'therest' not included in the upper categories
    # we use sjoin to performe a spatial filter of 'therest' polygons contained in upper categories
    join11 = gpd.sjoin(therest, othersport, predicate="within", how="inner")
    join12 = gpd.sjoin(therest, playingfield, predicate="within", how="inner")
    join13 = gpd.sjoin(therest, publicpark, predicate="within", how="inner")

    # generate list of the IDs of 'therest' contained in upper categories, in order to eliminate the corresponding polygons from the layer
    list_for_diff11 = join11["id_left"].drop_duplicates().to_list()

    diff11 = therest[
        ~therest.id.isin(list_for_diff11)
    ]  # 1st difference layer # note the negation character ~ to take the polygons NOT included

    list_for_diff12 = join12["id_left"].drop_duplicates().to_list()
    diff12 = diff11[~diff11.id.isin(list_for_diff12)]  # 2nd difference layer

    list_for_diff13 = join13["id_left"].drop_duplicates().to_list()
    diff13 = diff12[
        ~diff12.id.isin(list_for_diff13)
    ]  # 3rd difference layer, this is for 'therest' categories

    # we repeat the same operation for subsequent categories:
    # find 'othersport' not included in the upper categories
    join21 = gpd.sjoin(othersport, playingfield, predicate="within", how="inner")
    join22 = gpd.sjoin(othersport, publicpark, predicate="within", how="inner")

    list_for_diff21 = join21["id_left"].drop_duplicates().to_list()
    diff21 = othersport[~othersport.id.isin(list_for_diff21)]

    list_for_diff22 = join22["id_left"].drop_duplicates().to_list()
    diff22 = diff21[~diff21.id.isin(list_for_diff22)]  # 'othersport' difference

    # find 'playing fields' not included in the upper categories (and viceversa?)
    join31 = gpd.sjoin(playingfield, publicpark, predicate="within", how="inner")

    list_for_diff31 = join31["id_left"].drop_duplicates().to_list()
    diff31 = playingfield[
        ~playingfield.id.isin(list_for_diff31)
    ]  # 'playingfield' difference

    # put together all the differences layers: (and should bring out to the desired output)
    together1 = pd.concat([diff13, diff22]).pipe(
        gpd.GeoDataFrame
    )  # 'therest' + 'othersport' differences
    together1.head()
    together2 = pd.concat([together1, diff31]).pipe(
        gpd.GeoDataFrame
    )  # last gdf + 'playingfield' difference
    together_again = gpd.GeoDataFrame(
        pd.concat([together2, publicpark]), crs=27700
    )  # last gdf + all the public parks)

    list_gs_id = together_again["id"].to_list()
    accesspoints_edge = greenspace_access_aoi[
        greenspace_access_aoi.ref_to_greenspace_site.isin(list_gs_id)
    ]
    accesspoints_edge = accesspoints_edge.to_crs(27700)

    together_again["area_m2"] = together_again["geometry"].area

    together_again.to_file(f"{temp_folder}/greenspace.gpkg", layer="sites")
    accesspoints_edge.to_file(f"{temp_folder}/greenspace.gpkg", layer="access_points")

    # 10. Create traveltime matrix (origins are cells, destinations are cells plus greenspace entrances)

    print("10/13: Create traveltime matrix")
    origins = grid_aoi.set_geometry(grid_aoi.centroid).to_crs(4326)
    origins["id"] = origins.index

    destinations = pd.concat(
        [
            origins[["id", "geometry"]],
            accesspoints_edge[["id", "geometry", "ref_to_greenspace_site"]].to_crs(
                4326
            ),
        ],
        ignore_index=True,
    )

    transport_network = TransportNetwork(f"{temp_folder}/aoi.osm.pbf", [gtfs_data_file])

    # generate dataframe with all from_id and all to_id pairs

    prod = product(origins["id"].unique(), destinations["id"].unique())
    empty_ttm = pd.DataFrame(prod)
    empty_ttm.columns = ["from_id", "to_id"]

    # defining variables
    max_time = dt.timedelta(seconds=900)  # SET TO 15 MIN
    walking_speed = 4.8
    cycling_speed = 16

    # dataframe to match legmode and transitmode objects (to be inputted in the ttm computer)

    modes_lut = pd.DataFrame(
        [
            ["transit", TransportMode.CAR, TransportMode.WALK],
            ["car", "", TransportMode.CAR],
            ["bicycle", "", TransportMode.BICYCLE],
            ["walk", "", TransportMode.WALK],
        ],
        columns=("Mode", "Transit_mode", "Leg_mode"),
    )

    # function to generate custom list of transit+transport mode for the parameter transport_modes in TravelTimeMatrixComputer
    def list_making(s, z):
        if s:
            return [s] + [z]
        return [z]

    ttm_complete = empty_ttm.copy()

    # loop to compute a ttm for all the modes and generate one single ttm table in output
    for row in modes_lut.itertuples():
        start_time = dt.datetime.now()
        mode = row.Mode
        transit_mode = row.Transit_mode
        leg_mode = row.Leg_mode
        transport_mode = list_making(
            transit_mode, leg_mode
        )  # creating list of objects for transport_modes parameter
        ttm_computer = TravelTimeMatrixComputer(
            transport_network,
            origins=origins,
            destinations=destinations,
            departure=dt.datetime.strptime(date_time, "%Y,%m,%d,%H,%M"),
            max_time=max_time,
            speed_walking=walking_speed,
            speed_cycling=cycling_speed,
            transport_modes=transport_mode,
        )

        ttm = ttm_computer.compute_travel_times()
        ttm = ttm.rename(
            columns={"travel_time": f"time_{mode}"}
        )  # renaming 'travel_time' column (automatically generated) to 'time_{mode of transport}'
        #  merging the empty table generated before (with all possible origins and destinations) with the ttm, per each mode adding a travel time column
        ttm_complete = ttm_complete.merge(
            ttm,
            how="outer",
            left_on=["from_id", "to_id"],
            right_on=["from_id", "to_id"],
        )

        end_time = dt.datetime.now()
        print(f"    Duration for {mode}: {end_time - start_time}")

    ttm_complete.to_parquet(f"{temp_folder}/ttm_complete.parquet")

    # Wrap to a demoland_engine accessibility
    print("11/13: Wrap to a demoland_engine accessibility")

    ttm = ttm_complete.set_index(["from_id", "to_id"])
    ttm.columns = ["transit", "car", "bike", "walk"]
    ttm.columns.name = "mode"
    ttm_arr = xr.DataArray.from_series(ttm.stack())
    ttm_15 = ttm_arr <= 15
    ttm_15.name = "ttm_15"

    wpz_population = grid_aoi[
        [
            "A, B, D, E. Agriculture, energy and water",
            "C. Manufacturing",
            "F. Construction",
            "G, I. Distribution, hotels and restaurants",
            "H, J. Transport and communication",
            "K, L, M, N. Financial, real estate, professional and administrative activities",
            "O,P,Q. Public administration, education and health",
            "R, S, T, U. Other",
        ]
    ].sum(axis=1)
    wpz_population.index.name = "to_id"

    da = xr.DataArray.from_series(wpz_population)
    da.name = "wpz_population"
    baseline = xr.merge([ttm_15, da])
    baseline["wpz_population"] = baseline["wpz_population"].fillna(0)

    # Load greenspace data.

    gs_sites = gpd.read_file(f"{temp_folder}/greenspace.gpkg", layer="sites").rename(
        columns={"id": "id_site"}
    )
    gs_entrances = gpd.read_file(f"{temp_folder}/greenspace.gpkg", layer="access_points").rename(
        columns={"id": "id_entrance"}
    )

    # associate park area to entrances
    gs_entrances_with_parkarea = pd.merge(
        gs_entrances[["id_entrance", "ref_to_greenspace_site"]],
        gs_sites[["id_site", "function", "area_m2"]],
        left_on="ref_to_greenspace_site",
        right_on="id_site",
        how="right",
    )

    ttm_greenspace = ttm_complete.copy()  # saving a copy of the matrix (the following operations will add columns to it, but we want to keep the original one also)

    ttm_gs_with_area = pd.merge(
        ttm_greenspace,
        gs_entrances_with_parkarea[
            ["id_entrance", "ref_to_greenspace_site", "area_m2"]
        ],
        left_on="to_id",
        right_on="id_entrance",
        how="left",
    )
    # generate tracc cost object
    ttm_gs_tracc = tracc.costs(ttm_gs_with_area)

    modes_list = ["transit", "car", "bicycle", "walk"]

    # empty dataframes to be filled up in the next for loop
    gs_acc = []

    for m in modes_list:
        # generate variable names to be used in the tracc function below
        cost_name = "time_" + m
        impedence_param = 15  # value for impedence function, to be changed as needed
        impedence_param_string = str(impedence_param)
        # name of the column
        cost_output = (
            "cum_" + impedence_param_string + "_" + m
        )  # naming depends on impedence function threshold
        area_column_name = "area_" + impedence_param_string + "_" + m
        # Computing impedence function based on a 15 minute travel time threshold.
        ttm_gs_tracc.impedence_calc(
            cost_column=cost_name,
            impedence_func="cumulative",
            impedence_func_params=impedence_param,  # to calculate opportunities in X min threshold
            output_col_name=cost_output,
            prune_output=False,
        )
        ttm_gs_df = ttm_gs_tracc.data
        # Setting up the accessibility object. This includes joining the destination data to the travel time data
        # this needed to be done differently for greenspace, as opportunity is sites's area cumulative sum
        # A. Filtering only rows with time travel within the threshold
        ttm_gs_tracc.data[area_column_name] = (
            ttm_gs_tracc.data["area_m2"] * ttm_gs_tracc.data[cost_output]
        )
        ttm_gs_df = ttm_gs_tracc.data

        # B. Filter entrances (only one per park)
        oneaccess_perpark = ttm_gs_df.sort_values(cost_name).drop_duplicates(
            ["from_id", "ref_to_greenspace_site"]
        )
        # C. Assign metric as sum[parks' area]
        # generate df with one row per OA centroid ('from_id') and sum of sites' areas - per each mode
        gs_metric_per_mode = oneaccess_perpark.groupby(["from_id"])[
            area_column_name
        ].sum()  # .reset_index()
        gs_acc.append(gs_metric_per_mode)
    gs_acc = pd.concat(gs_acc, axis=1)

    gs_acc.to_parquet(f"{temp_folder}/acc_greenspace_allmodes_15min.parquet")

    gs_acc.columns = ["transit", "car", "bike", "walk"]
    greenspace = xr.DataArray.from_series(gs_acc.stack()).rename({"level_1": "mode"})
    greenspace.name = "green_accessibility"

    baseline = xr.merge([baseline, greenspace])
    baseline["green_accessibility"] = baseline["green_accessibility"].fillna(0)

    # Create demoland class

    acc = Accessibility(baseline)

    with open(f"{engine_folder}/{name}/accessibility.joblib", "wb") as f:
        joblib.dump(acc, f, compress=True)

    # 12. Generate files for the app
    print("12/13: Generate files for the app")
    # Geography

    grid_aoi.geometry.to_crs(4326).to_frame().assign(id=range(len(grid_aoi))).to_file(
        f"{app_folder}/geography.json"
    )

    # Geo config

    bds = grid_aoi.to_crs(4326).total_bounds
    zoom_lon = np.log2(360 * 2.0 / (bds[2] - bds[0]))
    zoom_lat = np.log2(360 * 2.0 / (bds[3] - bds[1]))
    zoom = round(np.min([zoom_lon, zoom_lat]), 2)
    geo_config = {
        "featureIdentifier": "to_id",
        "initialLatitude": round(np.mean([bds[1], bds[3]]), 2),
        "initialLongitude": round(np.mean([bds[0], bds[2]]), 2),
        "initialZoom": zoom - 0.4,
        "areaName": area_name,
        "modelIdentifier": name,
    }
    with open(f"{app_folder}/geo_config.json", "w") as f:
        json.dump(geo_config, f)

    # Baseline

    with open("house_price_model.joblib", "rb") as f:
        hp_model = joblib.load(f)
    with open("air_quality_model.joblib", "rb") as f:
        aq_model = joblib.load(f)

    hp = Model(matrix_aoi, hp_model)
    aq = Model(matrix_aoi, aq_model)

    baseline_hp = hp.predict(
        grid_aoi.drop(
            columns=[
                "geometry",
                "air_quality_index",
                "house_price_index",
                "signature_type",
            ]
        )
    )
    baseline_aq = aq.predict(
        grid_aoi.drop(
            columns=[
                "geometry",
                "air_quality_index",
                "house_price_index",
                "signature_type",
            ]
        )
    )

    oa = pd.Series(0, index=grid_aoi.index, name="oa")
    oa.index.name = "to_id"

    baseline_ja = acc.job_accessibility(oa, "walk")
    baseline_ga = acc.greenspace_accessibility(oa, "walk")

    mapping = {
        "Wild countryside": 0,
        "Countryside agriculture": 1,
        "Urban buffer": 2,
        "Warehouse/Park land": 3,
        "Open sprawl": 4,
        "Disconnected suburbia": 5,
        "Accessible suburbia": 6,
        "Connected residential neighbourhoods": 7,
        "Dense residential neighbourhoods": 8,
        "Gridded residential quarters": 9,
        "Dense urban neighbourhoods": 10,
        "Local urbanity": 11,
        "Regional urbanity": 12,
        "Metropolitan urbanity": 13,
        "Concentrated urbanity": 14,
        "Hyper concentrated urbanity": 15,
    }
    baseline = pd.DataFrame(
        {
            "air_quality": pd.Series(baseline_aq, index=grid_aoi.index),
            "house_price": pd.Series(baseline_hp, index=grid_aoi.index),
            "job_accessibility": baseline_ja.to_series(),
            "greenspace_accessibility": baseline_ga.to_series()
        }
    ).reindex(grid_aoi.index)
    baseline["signature_type"] = grid_aoi.signature_type.map(mapping)

    with open(f"{app_folder}/scenarios/baseline.json", "w") as f:
        json.dump(
            {
                "metadata": {
                    "name": "baseline",
                    "short": "Baseline",
                    "long": "Baseline: Situation now",
                    "description": "The baseline reflects the situation as our models see it today. It shows what the four indicators are predicted to be using existing land use data.",
                },
                "changes": {},
                "values": baseline.to_dict(orient="index"),
            },
            f,
        )
        
    shutil.copyfile("index.ts", f"{app_folder}/scenarios/index.ts")

    # 13. Generate files to be uploaded to the data repository
    print("13/13: Generate files to be uploaded to the data repository")
    grid_aoi.drop(
        columns=["geometry", "air_quality_index", "house_price_index", "signature_type"]
    ).to_parquet(f"{engine_folder}/{name}/default_data.parquet")

    pd.DataFrame(
        index=grid_aoi.index,
        columns=["signature_type", "use", "greenspace", "job_types"],
    ).replace(np.nan, None).to_parquet(f"{engine_folder}/{name}/empty.parquet")

    pd.DataFrame({"area": grid_aoi.area}).to_parquet(f"{engine_folder}/{name}/oa_area.parquet")

    grid_aoi[["signature_type"]].rename(
        columns={"signature_type": "primary_type"}
    ).to_parquet(f"{engine_folder}/{name}/oa_key.parquet")

    # Generate sha256

    registry = {}
    for fp in glob(f"{engine_folder}/{name}/*"):
        with open(fp, "rb") as f:
            bytes = f.read()
            registry[fp.split("/")[-1]] = hashlib.sha256(bytes).hexdigest()
    with open(f"{engine_folder}/hashes.json", "w") as f:
        json.dump(registry, f)

    shutil.make_archive("data/app", "zip", app_folder)
    shutil.make_archive("data/engine", "zip", engine_folder)

    print(f"""
    PROCESSING FINISHED

    Time elapsed: {dt.datetime.now() - start}
    
    Next steps are manual.
    
    14. Take the folder with engine files and upload it to `Urban-Analytics-Technology-Platform/demoland-engine/data/`.
    15. Use the information in `sha256.py` to update `data.py` in the `demoland_engine` code.
    16. Take the folder with the app files and use it to generate the app.
    """)

if __name__ == "__main__":
    main()
