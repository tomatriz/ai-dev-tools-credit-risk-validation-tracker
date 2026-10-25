FROM node:22-alpine AS build
WORKDIR /app
ARG VITE_API_URL=/api/v1
ARG VITE_API_BASE_URL=
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ENV BACKEND_HOSTPORT=backend:8000
ENV NGINX_ENVSUBST_FILTER=BACKEND_HOSTPORT
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
