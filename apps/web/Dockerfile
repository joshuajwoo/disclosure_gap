FROM node:22.14.0-alpine AS dependencies

WORKDIR /workspace
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm ci

FROM dependencies AS dev
COPY apps/web ./apps/web
CMD ["npm", "run", "dev", "--workspace", "apps/web", "--", "--hostname", "0.0.0.0"]

FROM dependencies AS builder
ARG NEXT_PUBLIC_DEMO_MODE=true
ENV NEXT_PUBLIC_DEMO_MODE=$NEXT_PUBLIC_DEMO_MODE
COPY apps/web ./apps/web
RUN npm run build --workspace apps/web

FROM node:22.14.0-alpine AS production
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs
WORKDIR /workspace
COPY --from=builder --chown=nextjs:nextjs /workspace/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /workspace/apps/web/.next/static ./apps/web/.next/static
USER nextjs
EXPOSE 3000
WORKDIR /workspace/apps/web
CMD ["node", "server.js"]
