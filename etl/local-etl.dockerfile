FROM apache/airflow:slim-2.6.1-python3.10

USER root

# install grype
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | \
    sh -s -- -b /opt/grype v0.59.0 &&  \
    ls /opt/grype/grype # check if grype is installed


COPY .grype.yaml /opt/grype/.grype.yaml

# install valint
RUN curl -sSfL https://get.scribesecurity.com/install.sh | \
    sh -s -- -t valint:0.2.0 -b /opt/valint && ls /opt/valint/valint

# install skopeo
RUN apt-get update && \
    apt-get install -y jq skopeo

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# internal-api
COPY ./internal-api/app /internal-api/code/app
