FROM python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
RUN pip install --no-cache-dir numpy==2.5.4 onnxruntime==1.31.1 tokenizers==0.23.3 "psycopg[binary]==3.3.6"
WORKDIR /bench
COPY backend/evals/local_cpu/run.py backend/evals/local_cpu/download.py backend/evals/local_cpu/verify.py /bench/
CMD ["python", "-u", "run.py"]
