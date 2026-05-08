FROM golang:1.22-alpine AS builder

WORKDIR /build
RUN apk add --no-cache git ca-certificates

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o geo-service .

FROM alpine:3.19

RUN apk add --no-cache ca-certificates wget
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=builder /build/geo-service .
RUN chown appuser:appgroup geo-service

USER appuser
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["./geo-service"]
