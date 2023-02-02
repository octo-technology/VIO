FROM node:12.2.0-alpine as build-stage

WORKDIR /edge_interface
COPY package*.json ./
RUN npm config set registry https://artifactory.michelin.com/artifactory/api/npm/npm-remote/
RUN npm install
COPY ./ .
RUN npm run build

FROM nginx as production-stage
RUN mkdir /edge_interface
COPY --from=build-stage /edge_interface/dist /edge_interface
COPY nginx.conf /etc/nginx/nginx.conf
