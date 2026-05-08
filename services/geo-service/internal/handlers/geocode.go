package handlers

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"github.com/gin-gonic/gin"
)

type GeocodeResult struct {
	Lat     float64 `json:"lat"`
	Lng     float64 `json:"lng"`
	Address string  `json:"address"`
	PlaceID string  `json:"place_id"`
}

func (h *Handler) Geocode(c *gin.Context) {
	q := c.Query("q")
	if q == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "query parameter 'q' is required"})
		return
	}

	cacheKey := fmt.Sprintf("geo:geocode:%x", sha256.Sum256([]byte(q)))
	ctx := context.Background()

	if cached, err := h.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
		h.cacheHit.WithLabelValues("geocode").Set(1)
		var result GeocodeResult
		if json.Unmarshal(cached, &result) == nil {
			c.JSON(http.StatusOK, result)
			return
		}
	}
	h.cacheHit.WithLabelValues("geocode").Set(0)

	if h.googleMapsKey == "" {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "geocoding not configured"})
		return
	}

	h.apiCalls.WithLabelValues("geocode").Inc()
	apiURL := fmt.Sprintf(
		"https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s",
		url.QueryEscape(q), h.googleMapsKey,
	)

	resp, err := http.Get(apiURL)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "geocoding request failed"})
		return
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)

	var gResp map[string]interface{}
	if err := json.Unmarshal(body, &gResp); err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "geocoding parse failed"})
		return
	}

	results, ok := gResp["results"].([]interface{})
	if !ok || len(results) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "no results found"})
		return
	}

	first := results[0].(map[string]interface{})
	geometry := first["geometry"].(map[string]interface{})
	location := geometry["location"].(map[string]interface{})

	result := GeocodeResult{
		Lat:     location["lat"].(float64),
		Lng:     location["lng"].(float64),
		Address: first["formatted_address"].(string),
		PlaceID: first["place_id"].(string),
	}

	if data, err := json.Marshal(result); err == nil {
		h.rdb.SetEX(ctx, cacheKey, data, 24*time.Hour)
	}

	c.JSON(http.StatusOK, result)
}
