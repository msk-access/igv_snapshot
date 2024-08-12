
# Use an official OpenJDK runtime as a parent image
FROM eclipse-temurin:17-jdk AS base

# For ARM64 (Apple Silicon M1)
FROM base AS arm64
RUN uname -m | grep aarch64 && echo "Running on ARM64 architecture"

# For AMD64 (Linux and Intel/AMD Macs)
FROM base AS amd64
RUN uname -m | grep x86_64 && echo "Running on AMD64 architecture"

# Default build stage
FROM ${TARGETARCH:-amd64}


RUN apt-get update && \
    apt-get install -y wget unzip xvfb xorg python3 python3-pip python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories and set variables
RUN mkdir -p /igv_snapshot
ARG IGV_VERSION=2.18.0
ARG IGV_VERSION_MAJOR=2.18

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
RUN mkdir -p /igv_snapshot/java_prefs /igv_snapshot/system_pref
ENV PATH="/igv_snapshot/venv/bin:${PATH}"

# Set up environment variables, if needed
ENV JAVA_HOME /opt/java/openjdk


# Set a working directory (if necessary)
RUN chmod -R 777 /igv_snapshot
WORKDIR /igv_snapshot

# Set the default entry point to a shell
ENTRYPOINT ["/bin/bash"]