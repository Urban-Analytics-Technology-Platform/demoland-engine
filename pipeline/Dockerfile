FROM mambaorg/micromamba:1.5.5
COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

RUN mkdir app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY ../pyproject.toml /app/pyproject.toml
COPY ../demoland_engine /app/demoland_engine

# Install any needed packages specified in requirements.txt
# (You may need to adjust this depending on the requirements of your Python script)
RUN pip install --no-deps .

# Define environment variables
ENV AREA_NAME=""
ENV NAME=""
ENV AOI_FILE_PATH=""
ENV GTFS_FILE_PATH=""

# Run the Python script when the container launches
CMD python pipeline.py $AREA_NAME $NAME $AOI_FILE_PATH $GTFS_FILE_PATH
