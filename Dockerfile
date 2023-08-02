FROM python:3.11

WORKDIR /code

RUN pip install --no-cache-dir --upgrade \
    fastapi \
    pydantic \
    uvicorn \
    joblib \
    pandas \
    libpysal \
    xarray \
    pyarrow \
    scikit-learn \
    setuptools_scm

COPY ./demoland_engine /code/demoland_engine
COPY ./pyproject.toml /code/pyproject.toml
COPY ./api /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
