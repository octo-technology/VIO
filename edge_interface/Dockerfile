FROM node:lts-alpine as build-stage
RUN apk add g++ make py3-pip
WORKDIR /edge_interface
COPY package*.json ./
RUN npm install
COPY ./ .
# NODE_OPTIONS is needed on macos M1 to run any npm script
ENV NODE_OPTIONS --openssl-legacy-provider
RUN npm run build

FROM nginx as production-stage
RUN mkdir /edge_interface
COPY --from=build-stage /edge_interface/dist /edge_interface
COPY nginx.conf /etc/nginx/nginx.conf
