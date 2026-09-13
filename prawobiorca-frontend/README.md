# Prawobiorca Frontend

Frontend application for **Prawobiorca** --- a project developed within
the **WMS_DEV** science club at the **Wrocław University of Science and
Technology**.

Prawobiorca aims to help students defend and assert their rights by
making legal and university regulations easier to search, understand,
and use.

This repository contains the **frontend layer** of the application

## Recommended IDE
It is recommended to use a JetBrains IDE, preferably PyCharm, with frontend plugins.
For students, PyCharm Professional is free for non-commercial use.

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
pnpm install
```

### Compile and Hot-Reload for Development

```sh
pnpm dev
```

### Type-Check, Compile and Minify for Production

```sh
pnpm build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
pnpm test:unit
```

### Lint with [ESLint](https://eslint.org/)

```sh
pnpm lint
```
