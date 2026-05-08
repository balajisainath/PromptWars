package handlers

import (
	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus"
	"go.uber.org/zap"
)

type Handler struct {
	rdb           *redis.Client
	logger        *zap.Logger
	googleMapsKey string
	apiCalls      *prometheus.CounterVec
	cacheHit      *prometheus.GaugeVec
}

func New(
	rdb *redis.Client,
	logger *zap.Logger,
	googleMapsKey string,
	apiCalls *prometheus.CounterVec,
	cacheHit *prometheus.GaugeVec,
) *Handler {
	return &Handler{
		rdb:           rdb,
		logger:        logger,
		googleMapsKey: googleMapsKey,
		apiCalls:      apiCalls,
		cacheHit:      cacheHit,
	}
}
