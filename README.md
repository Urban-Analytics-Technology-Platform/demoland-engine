# Demoland engine

A predictive engine for the Alan Turing Institute project DemoLand

## Install

Either clone and pip install or pip install from git.

## Usage

See the notebooks in the `docs` folder.


## Demoland pipeline

```sh
docker build -t demoland_pipeline -f Dockerfile.pipe .
docker run \
        --rm \
        -ti \
        -e AREA_NAME="Tyne and Wear" \
        -e NAME="tyne_and_wear_v1" \
        -e AOI_FILE_PATH="area_of_interest.geojson" \
        -e GTFS_FILE_PATH="itm_north_east_gtfs.zip" \
        -v /path/to/host/files:/app/data \
        demoland_pipeline
```

File paths are relative to the `/path/to/host/files`.