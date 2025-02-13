FROM --platform=$TARGETPLATFORM node:lts-alpine AS builder
ARG TARGETPLATFORM

RUN apk add g++ make py3-pip

WORKDIR /edge_interface

COPY package*.json ./
COPY ./ .

# NODE_OPTIONS is needed on macos M1 to run any npm script
ENV NODE_OPTIONS --openssl-legacy-provider

RUN npm install
RUN npm run build


FROM --platform=$TARGETPLATFORM nginx AS production-stage
ARG TARGETPLATFORM

WORKDIR /edge_interface

COPY --from=builder /edge_interface/dist /edge_interface
COPY nginx.conf /etc/nginx/nginx.conf
