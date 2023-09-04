FROM python:3.11-bookworm

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app
# Copy project
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

# runs the production server
ENTRYPOINT ["gunicorn", "kioskadmin.wsgi"]