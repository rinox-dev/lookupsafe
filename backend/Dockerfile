FROM node:24-bookworm-slim

WORKDIR /workspace
COPY backend/package.json backend/package-lock.json ./backend/
RUN npm ci --prefix backend
COPY backend ./backend
COPY shared ./shared

WORKDIR /workspace/backend
EXPOSE 8787
ENTRYPOINT ["sh", "./start-container.sh"]
