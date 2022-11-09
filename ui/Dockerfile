FROM node:12.2.0-alpine as build-stage

WORKDIR /ui
COPY package*.json ./
RUN npm install
COPY ./ .
RUN npm run build

FROM nginx as production-stage
RUN mkdir /ui
COPY --from=build-stage /ui/dist /ui
COPY nginx.conf /etc/nginx/nginx.conf
