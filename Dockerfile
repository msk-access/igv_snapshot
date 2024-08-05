# Docker container with the dependencies needed to run the IGV snapshot automator
FROM ubuntu:latest

ARG IGV_VERSION=2.18.0
ARG IGV_VERSION_MAJOR=2.18
ARG JDK_VERSION=17

RUN apt-get update && \
apt-get install -y wget unzip xvfb xorg openjdk-${JDK_VERSION}-jdk python3 python3-pip python3-venv

# add the source code for the repo to the container
ADD . /igv_snapshot
ENV PATH="/igv_snapshot/:/igv_snapshot/IGV_Linux_${IGV_VERSION}/:${PATH}"

# install IGV via the Makefile
# then make a dummy batch script in order to load the hg19 genome into the container
# https://software.broadinstitute.org/software/igv/PortCommands
# TODO igv version as a variable
# TODO most recent version
RUN cd /igv_snapshot && \
    wget https://data.broadinstitute.org/igv/projects/downloads/${IGV_VERSION_MAJOR}/IGV_${IGV_VERSION}.zip -O tmp && \
    mv tmp IGV_${IGV_VERSION}.zip && \
    unzip IGV_${IGV_VERSION}.zip && \
	rm -f IGV_${IGV_VERSION}.zip 

# IGV Arguments
ENV IGV_LIB_DIRECTORY="/igv_snapshot/IGV_${IGV_VERSION}/lib/"
ENV IGV_ARGS_FILE="/igv_snapshot/igv.args"

# Install Python Package
RUN cd /igv_snapshot && \
    python3 -m venv venv

ENV PATH="/igv_snapshot/venv/bin:${PATH}"

RUN cd /igv_snapshot && \
    pip install -r requirements.txt && \
    pip install . 
