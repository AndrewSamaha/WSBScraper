# Use an official Python runtime as a parent image
FROM mongo
LABEL Author=andrew.samaha@gmail.com

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip
#RUN apt-get -y install python3.7-dev
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 27017
