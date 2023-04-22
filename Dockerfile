# Install the base requirements for the app.
# This stage is to support development.

FROM node:14.17.0-alpine AS base
# Set the working directory to /app
WORKDIR /Facial_Expression_Identification
COPY package*.json ./
RUN npm install 
RUN npm install react-scripts@3.4.1 -g --silent
COPY . .

CMD ["npm", "start"]


FROM python:3.8-slim-buster AS base
WORKDIR /Facial_Expression_Identification
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install -r requirements.txt  

COPY . .

ENTRYPOINT [ "python" ]

CMD ["backend.py" ]