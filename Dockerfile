# Docker container with the dependencies needed to run the IGV snapshot automator
FROM ubuntu:latest

ARG IGV_VERSION=2.18.0
ARG IGV_VERSION_MAJOR=2.18
ARG JDK_VERSION=17

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget unzip xvfb xorg openjdk-${JDK_VERSION}-jdk python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories and set permissions
RUN mkdir -p /igv_snapshot && \
    mkdir -p /root/.java/.userPrefs && \
    chmod -R 777 /igv_snapshot /root/.java

RUN mkdir -p /home/user/.java/.userPrefs /home/user/.cache/fontconfig && \
    chown -R user:user /home/user/.java /home/user/.cache

USER user
# Set JAVA_OPTS to specify preferences directory
ENV JAVA_OPTS="-Djava.util.prefs.userRoot=/root/.java"

# Create directories and set permissions
RUN mkdir -p /igv_snapshot && \
    chmod -R 777 /igv_snapshot

# Add the source code for the repo to the container
ADD . /igv_snapshot

# Install IGV
RUN cd /igv_snapshot && \
    wget https://data.broadinstitute.org/igv/projects/downloads/${IGV_VERSION_MAJOR}/IGV_${IGV_VERSION}.zip -O IGV_${IGV_VERSION}.zip && \
    unzip IGV_${IGV_VERSION}.zip && \
    rm -f IGV_${IGV_VERSION}.zip 

# IGV Arguments
ENV IGV_LIB_DIRECTORY="/igv_snapshot/IGV_${IGV_VERSION}/lib/"
ENV IGV_ARGS_FILE="/igv_snapshot/igv.args"

# Install Python Package
RUN cd /igv_snapshot && \
    python3 -m venv venv && \
    . /igv_snapshot/venv/bin/activate && \
    pip install -r requirements.txt && \
    pip install . 

# Create writable directories for Java preferences and fontconfig cache
RUN mkdir -p /igv_snapshot/java_prefs /igv_snapshot/fontconfig_cache

ENV PATH="/igv_snapshot/venv/bin:${PATH}"

# Set a working directory (if necessary)
WORKDIR /igv_snapshot