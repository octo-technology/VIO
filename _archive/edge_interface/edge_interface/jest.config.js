module.exports = {
  verbose: true,
  setupFiles: ['jest-localstorage-mock'],
  setupFilesAfterEnv: ['jest-extended'],
  testURL: 'http://localhost',
  moduleFileExtensions: ['js', 'json', 'vue'],
  transform: {
    '^.+\\.vue$': 'vue-jest',
    '.+\\.(css|styl|less|sass|scss|png|jpg|ttf|woff|woff2)$': 'jest-transform-stub',
    '^.+\\.jsx?$': 'babel-jest'
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  testPathIgnorePatterns: ['node_modules'],
  // transformIgnorePatterns: ['node_modules/(?!(instantsearch\\.js|vue-json-tree))'],
  snapshotSerializers: ['jest-serializer-vue'],
  testMatch: ['(**/*.spec.js)'],
  collectCoverage: false,
  collectCoverageFrom: [
    'src/**/*.{vue,js}',
    '!src/{components,views,presenters}/**/*.js',
    '!src/plugins/**/*',
    '!src/main.js',
    '!src/router.js',
    '!src/config*.js',
    '!src/App.js'
  ]
}
