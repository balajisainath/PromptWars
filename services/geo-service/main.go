package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"

	"github.com/travelai/geo-service/internal/handlers"
	"github.com/travelai/geo-service/internal/middleware"
)

var (
	requestDuration = prometheus.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "geo_request_duration_seconds",
		Help:    "Request duration in seconds",
		Buckets: prometheus.DefBuckets,
	}, []string{"method", "path", "status"})

	googleAPICalls = prometheus.NewCounterVec(prometheus.CounterOpts{
		Name: "geo_google_api_calls_total",
		Help: "Total Google API calls",
	}, []string{"endpoint"})

	cacheHitRatio = prometheus.NewGaugeVec(prometheus.GaugeOpts{
		Name: "geo_cache_hit_ratio",
		Help: "Cache hit ratio by endpoint",
	}, []string{"endpoint"})
)

func init() {
	prometheus.MustRegister(requestDuration, googleAPICalls, cacheHitRatio)
}

func getEnv(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	redisAddr := fmt.Sprintf("%s:%s",
		getEnv("REDIS_HOST", "redis"),
		getEnv("REDIS_PORT", "6379"),
	)
	rdb := redis.NewClient(&redis.Options{Addr: redisAddr})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := rdb.Ping(ctx).Err(); err != nil {
		logger.Warn("Redis not available, continuing without cache", zap.Error(err))
	}

	googleMapsKey := getEnv("GOOGLE_MAPS_API_KEY", "")
	h := handlers.New(rdb, logger, googleMapsKey, googleAPICalls, cacheHitRatio)

	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Recovery())
	r.Use(middleware.RequestID())
	r.Use(middleware.Logger(logger, requestDuration))

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "geo-service"})
	})
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))

	geo := r.Group("/geo")
	geo.POST("/distance-matrix", h.DistanceMatrix)
	geo.POST("/route-feasibility", h.RouteFeasibility)
	geo.GET("/geocode", h.Geocode)

	port := getEnv("GEO_SERVICE_PORT", "8080")
	logger.Info("geo-service starting", zap.String("port", port))
	if err := r.Run(":" + port); err != nil {
		logger.Fatal("server failed", zap.Error(err))
	}
}
