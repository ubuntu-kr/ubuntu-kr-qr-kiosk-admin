FROM ubuntu:24.04 
# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app
# Copy project
COPY . .
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 ca-certificates fonts-noto-cjk python3 python3-pip python3-venv \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /app/static \
    && python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["./run.sh"]
# runs the production server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "kioskadmin.wsgi"]