FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --no-audit --no-fund --prefer-offline || npm install --no-audit --no-fund

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
