FROM node:22-alpine AS deps
WORKDIR /workspace
COPY package.json ./
COPY apps/web/package.json apps/web/package.json
COPY apps/admin/package.json apps/admin/package.json
RUN npm install

FROM node:22-alpine AS builder
WORKDIR /workspace
COPY --from=deps /workspace/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run admin:build

FROM node:22-alpine AS runner
WORKDIR /workspace
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3001
COPY --from=builder /workspace/node_modules ./node_modules
COPY --from=builder /workspace/package.json ./package.json
COPY --from=builder /workspace/apps/admin ./apps/admin
COPY --from=builder /workspace/apps/web/package.json ./apps/web/package.json
EXPOSE 3001
CMD ["npm", "--workspace", "@alap/admin", "run", "start"]
