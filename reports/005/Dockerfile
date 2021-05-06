# using old ubuntu as Strabo is tested with it, see https://github.com/spatial-computing/strabo-text-recognition-deep-learning#i-installation
FROM ubuntu:20.04

# Avoid interactive input for tzdata
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /strabo

COPY StraboDependency.zip StraboDependency.zip
RUN apt-get update && \
  apt-get install -y \
    unzip \
    git \
  software-properties-common && \
  unzip StraboDependency.zip

#COPY install.sh install.sh
# BASED ON INSTALL.SH FROM STRABO
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y unzip \
    python3.6-dev \
    python3-pip \
    # https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo#47114731
    libsm6 libxrender1 libfontconfig1 \
    libgeos-dev && \
    python3.6 -m pip install --upgrade pip
RUN python3.6 -m pip install -r text-detection-requirements.txt

#E: Version '4.0.*' for 'tesseract-ocr' was not found
#E: Version '4.0.*' for 'libtesseract-dev' was not found
#E: Version '1.76.*' for 'libleptonica-dev' was not found
#The command '/bin/sh -c add-apt-repository -y ppa:alex-p/tesseract-ocr &   apt-get update &   apt-get install -y tesseract-ocr=4.0.* libtesseract-dev=4.0.* libleptonica-dev=1.76.*' returned a non-zero code: 100
#RUN add-apt-repository -y ppa:alex-p/tesseract-ocr & \
# install from regular sources
RUN apt-get update && \
  #apt-get install -y tesseract-ocr=4.0.* libtesseract-dev=4.0.* libleptonica-dev=1.76.*
  apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev tesseract-ocr-deu
RUN python3.6 -m pip install git+https://github.com/spatial-computing/tesserocr

RUN git clone https://github.com/spatial-computing/strabo-text-recognition-deep-learning.git && \
  cd strabo-text-recognition-deep-learning/lanms && \
  sed -i 's/{python3-config}/{python3.6-config}/' Makefile && \
  #rm adaptor.so && \
  make

RUN apt-get update && \
  apt-get install -y libtiff-tools

ENV LC_ALL=C

WORKDIR /labelextraction