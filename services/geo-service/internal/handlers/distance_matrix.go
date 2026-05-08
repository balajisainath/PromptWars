package handlers

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"net/url"
	"time"

	"github.com/gin-gonic/gin"
)

type Coordinate struct {
	Lat float64 `json:"lat"`
	Lng float64 `json:"lng"`
}

type DistanceMatrixRequest struct {
	Coordinates []Coordinate `json:"coordinates" binding:"required,min=2"`
}

type MatrixCell struct {
	DistanceM   int    `json:"distance_m"`
	DurationSec int    `json:"duration_sec"`
	Status      string `json:"status"`
}

type DistanceMatrixResponse struct {
	Matrix [][]MatrixCell `json:"matrix"`
}

func (h *Handler) DistanceMatrix(c *gin.Context) {
	var req DistanceMatrixRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	cacheKey := h.matrixCacheKey(req.Coordinates)
	ctx := context.Background()

	if cached, err := h.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
		h.cacheHit.WithLabelValues("distance_matrix").Set(1)
		var resp DistanceMatrixResponse
		if json.Unmarshal(cached, &resp) == nil {
			c.JSON(http.StatusOK, resp)
			return
		}
	}
	h.cacheHit.WithLabelValues("distance_matrix").Set(0)

	resp := h.buildDistanceMatrix(req.Coordinates)
	if data, err := json.Marshal(resp); err == nil {
		h.rdb.SetEX(ctx, cacheKey, data, 24*time.Hour)
	}
	c.JSON(http.StatusOK, resp)
}

func (h *Handler) matrixCacheKey(coords []Coordinate) string {
	data, _ := json.Marshal(coords)
	return fmt.Sprintf("geo:matrix:%x", sha256.Sum256(data))
}

func (h *Handler) buildDistanceMatrix(coords []Coordinate) DistanceMatrixResponse {
	n := len(coords)
	matrix := make([][]MatrixCell, n)
	for i := range matrix {
		matrix[i] = make([]MatrixCell, n)
		for j := range matrix[i] {
			if i == j {
				matrix[i][j] = MatrixCell{DistanceM: 0, DurationSec: 0, Status: "OK"}
				continue
			}
			dist, dur, err := h.fetchGoogleDistance(coords[i], coords[j])
			if err != nil {
				distF := haversineMeters(coords[i].Lat, coords[i].Lng, coords[j].Lat, coords[j].Lng)
				dist = int(distF)
				dur = int(distF / 13.9) // ~50 km/h
			} else {
				h.apiCalls.WithLabelValues("distance_matrix").Inc()
			}
			matrix[i][j] = MatrixCell{DistanceM: dist, DurationSec: dur, Status: "OK"}
		}
	}
	return DistanceMatrixResponse{Matrix: matrix}
}

func (h *Handler) fetchGoogleDistance(from, to Coordinate) (int, int, error) {
	if h.googleMapsKey == "" {
		return 0, 0, fmt.Errorf("no api key")
	}
	origins := fmt.Sprintf("%f,%f", from.Lat, from.Lng)
	destinations := fmt.Sprintf("%f,%f", to.Lat, to.Lng)
	apiURL := fmt.Sprintf(
		"https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s",
		url.QueryEscape(origins), url.QueryEscape(destinations), h.googleMapsKey,
	)
	resp, err := http.Get(apiURL)
	if err != nil {
		return 0, 0, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return 0, 0, err
	}
	rows, ok := result["rows"].([]interface{})
	if !ok || len(rows) == 0 {
		return 0, 0, fmt.Errorf("no rows in response")
	}
	row := rows[0].(map[string]interface{})
	elements, ok := row["elements"].([]interface{})
	if !ok || len(elements) == 0 {
		return 0, 0, fmt.Errorf("no elements in response")
	}
	elem := elements[0].(map[string]interface{})
	distMap, ok := elem["distance"].(map[string]interface{})
	if !ok {
		return 0, 0, fmt.Errorf("no distance field")
	}
	distM := int(distMap["value"].(float64))
	durSec := 0
	if durMap, ok := elem["duration"].(map[string]interface{}); ok {
		durSec = int(durMap["value"].(float64))
	}
	return distM, durSec, nil
}

func haversineMeters(lat1, lng1, lat2, lng2 float64) float64 {
	const R = 6371000.0
	dLat := (lat2 - lat1) * math.Pi / 180
	dLng := (lng2 - lng1) * math.Pi / 180
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1*math.Pi/180)*math.Cos(lat2*math.Pi/180)*
			math.Sin(dLng/2)*math.Sin(dLng/2)
	return R * 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
}
