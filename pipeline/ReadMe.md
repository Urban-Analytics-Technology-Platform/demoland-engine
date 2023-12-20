```sh
docker build -t demoland_pipeline .
docker run \
        --rm \
        -ti \
        -e AREA_NAME="Tyne and Wear" \
        -e NAME="tyne_and_wear_v1" \
        -e AOI_FILE_PATH="/area_of_interest.geojson" \
        -e GTFS_FILE_PATH="/itm_north_east_gtfs.zip" \
        -v /path/to/host/files:/app \
        demoland_pipeline
```