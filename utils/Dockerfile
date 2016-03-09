FROM java:8-jre
MAINTAINER Dedo Cibula <dedo.cibula@gmail.com>

RUN apt-get update && apt-get install -y \
	build-essential \
	curl \
	fish \
	git \
	htop \
	mediainfo \
	openssh-server \
	software-properties-common \
	tree \
	unzip \
	vim \
	wget \
	zsh
RUN apt-get update -y
RUN apt-get upgrade -y

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install -y \
	libcap-dev \
	libhdf5-dev \
	python-dev \
	python-h5py \
	python-numpy \
	python-nose \
	python-pycurl \
	python-scipy
RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py
RUN python get-pip.py && pip install boto3 pika xmltodict requests && rm get-pip.py

ENV BENCHMARK_HOME /vt-fedora-benchmark/experiments
ENV BENCHMARK_URL https://DedoCibula@bitbucket.org/DedoCibula/vt-fedora-benchmark.git
ENV FITS_URL http://projects.iq.harvard.edu/files/fits/files/fits-0.9.0.zip?m=1449588471

RUN git clone "$BENCHMARK_URL" vt-fedora-benchmark
RUN cd "$BENCHMARK_HOME" && wget -q "$FITS_URL" -O fits-0.9.0.zip && unzip -q fits-0.9.0.zip && chmod +x fits-0.9.0/fits.sh
ENV PATH "$PATH:${BENCHMARK_HOME}/fits-0.9.0/"

WORKDIR $BENCHMARK_HOME
CMD ["python"]