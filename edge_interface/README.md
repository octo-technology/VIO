# edge_interface

## Development setup
```
brew update
brew install node
```

## Project setup
```
cd edge_interface
npm install
```

Note: on macos (M1) before running npm script you need to set NODE_OPTIONS 
```
export NODE_OPTIONS=--openssl-legacy-provider
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

#### API customization
To set custom hostname and port you must create an `.env` file with this environment variables:
```
VUE_APP_API_PROTOCOL=
VUE_APP_API_HOSTNAME=
VUE_APP_API_PORT=
```
