FROM python:3.11

WORKDIR /code

# SSH
COPY entrypoint.sh ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd \
    && chmod u+x ./entrypoint.sh
COPY sshd_config /etc/ssh/
EXPOSE 8000 2222
EXPOSE 80 80

# Python
RUN pip install --no-cache-dir --upgrade \
    fastapi \
    pydantic \
    uvicorn \
    joblib==1.2.0 \
    pandas==1.5.3 \
    libpysal==4.7.0 \
    xarray==2023.1.0 \
    pyarrow==11.0.0 \
    scikit-learn==1.2.0 \
    setuptools_scm \
    pooch

COPY ./demoland_engine /code/demoland_engine
COPY ./pyproject.toml /code/pyproject.toml
COPY ./api /code

ENTRYPOINT ["./entrypoint.sh"]
