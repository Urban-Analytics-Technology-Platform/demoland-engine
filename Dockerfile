FROM python:3.11

WORKDIR /code

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
    setuptools_scm

COPY ./demoland_engine /code/demoland_engine
COPY ./pyproject.toml /code/pyproject.toml
COPY ./api /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
