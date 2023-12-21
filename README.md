# Demoland engine

A predictive engine for the Alan Turing Institute project DemoLand

## Install

Either clone and pip install or pip install from git.

## Usage

See the notebooks in the `docs` folder.

## Generate data for a new area using the Demoland pipeline

The process of generating data for a new area is provided in the form of a Docker container.
You will need to provide four pieces of information:

- `AREA_NAME`: Name that will be visible in the app to the user.
- `NAME`: Name that is used as a key within the `demoland_engine`.
- `AOI_FILE_PATH`: Path to a file relative to the current working directory (avoid `../`) containing polygon geometries defining the extent of the area of interest. Can be any file readable by `geopandas.read_file`.
- `GTFS_FILE_PATH`: Zip file with GTFS data covering the region of interest. Go to https://data.bus-data.dft.gov.uk/downloads/, register, and download timetable data for your region. Pass the file without any changes.

The best option is to create a folder with the two required files, navigate to the folder and run the container.

Example:

```sh
docker pull ghcr.io/urban-analytics-technology-platform/demoland_pipeline:latest
docker run \
    --rm \
    -ti \
    -e AREA_NAME="Tyne and Wear" \
    -e NAME="tyne_and_wear_v1" \
    -e AOI_FILE_PATH="geography.geojson" \
    -e GTFS_FILE_PATH="itm_north_east_gtfs.zip" \
    -v ${PWD}:/app/data \
    --user=$UID \
    ghcr.io/urban-analytics-technology-platform/demoland_pipeline
```

The container generates two ZIP files. One shall be used in `demoland_engine`, and the
other shall be used to deploy the app.

### Building the container

To successfully build the container, navigate to the root of the repository and copy the
necessary data files there as well. The required files:

- `air_quality_model.joblib`
- `grid_adjacency_binary.parquet`
- `grid_complete.parquet`
- `house_price_model.joblib`

All four need to be present in the repository at the time of building as they are copied
to the container. You can then build the container and upload it to GHCR as:

```sh
docker build -t ghcr.io/urban-analytics-technology-platform/demoland_pipeline -f Dockerfile.pipe .
docker push ghcr.io/urban-analytics-technology-platform/demoland_pipeline:latest
```