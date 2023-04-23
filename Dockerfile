
# Install the base requirements for the app.
# This stage is to support development.



FROM python:3.8-slim-buster 
WORKDIR /Facial_Expression_Identification
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install -r requirements.txt  
COPY . .
# Make port 5000 available to the world outside this container
EXPOSE 5000
# Define environment variable
ENV FLASK_APP=backend.py
# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]


FROM node:14.17.0-alpine AS base
# Set the working directory to /app
WORKDIR /Facial_Expression_Identification
COPY package*.json ./
RUN npm install 
RUN npm install react-scripts@3.4.1 -g --silent
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
