# small python image
FROM python:3.12-slim

# IN_DOCKER stops main.py trying to open a plot window
ENV PYTHONUNBUFFERED=1
ENV IN_DOCKER=1

WORKDIR /app

# install packages first so docker can cache this step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]