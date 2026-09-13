FROM node:24-alpine AS build

WORKDIR /prawobiorca-frontend

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
COPY pnpm-workspace.yaml* ./

RUN pnpm install --frozen-lockfile

COPY . .

ENV VITE_PRAWOBIORCA_API_URL=/api
RUN pnpm run build


FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /prawobiorca-frontend/dist /usr/share/nginx/html

EXPOSE 8000

CMD ["nginx", "-g", "daemon off;"]
