module.exports = {
  root: true,
  env: {
    es6: true,
    node: true
  },
  extends: ['plugin:vue/essential', '@vue/standard', '@vue/airbnb', 'plugin:prettier/recommended'],
  rules: {
    'import/no-extraneous-dependencies': 'off',
    'no-shadow': 'off',
    'class-methods-use-this': 'off',
    'no-plusplus': 'off',
    'import/extensions': 'off',
    'prettier/prettier': [
      'error',
      {
        endOfLine: 'auto',
        singleQuote: true,
        printWidth: 120,
        semi: false,
        tabWidth: 2
      }
    ],
    'no-param-reassign': [
      'error',
      {
        props: true,
        ignorePropertyModificationsFor: ['state']
      }
    ]
  },
  overrides: [
    {
      files: ['*.spec.js'],
      env: {
        jest: true
      }
    }
  ],
  parserOptions: {
    parser: 'babel-eslint'
  }
}
