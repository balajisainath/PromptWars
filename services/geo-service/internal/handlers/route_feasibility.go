package handlers

import (
	"fmt"
	"net/http"
	"sort"

	"github.com/gin-gonic/gin"
)

type ActivitySlot struct {
	Name      string  `json:"name"`
	Lat       float64 `json:"lat"`
	Lng       float64 `json:"lng"`
	StartTime string  `json:"start_time"`
	EndTime   string  `json:"end_time"`
}

type RouteFeasibilityRequest struct {
	Activities []ActivitySlot `json:"activities" binding:"required,min=2"`
}

type RouteFeasibilityResponse struct {
	Feasible bool     `json:"feasible"`
	Issues   []string `json:"issues"`
}

func (h *Handler) RouteFeasibility(c *gin.Context) {
	var req RouteFeasibilityRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	issues := []string{}

	sorted := make([]ActivitySlot, len(req.Activities))
	copy(sorted, req.Activities)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].StartTime < sorted[j].StartTime
	})

	for i := 1; i < len(sorted); i++ {
		prev := sorted[i-1]
		curr := sorted[i]
		if prev.EndTime != "" && curr.StartTime != "" && prev.EndTime > curr.StartTime {
			issues = append(issues, fmt.Sprintf(
				"Time conflict: '%s' ends at %s but '%s' starts at %s",
				prev.Name, prev.EndTime, curr.Name, curr.StartTime,
			))
		}
	}

	for i := 0; i < len(sorted)-1; i++ {
		if sorted[i].Lat == 0 || sorted[i+1].Lat == 0 {
			continue
		}
		dist := haversineMeters(sorted[i].Lat, sorted[i].Lng, sorted[i+1].Lat, sorted[i+1].Lng)
		if dist > 50000 {
			issues = append(issues, fmt.Sprintf(
				"Long distance (%.1fkm) between '%s' and '%s'",
				dist/1000, sorted[i].Name, sorted[i+1].Name,
			))
		}
	}

	c.JSON(http.StatusOK, RouteFeasibilityResponse{
		Feasible: len(issues) == 0,
		Issues:   issues,
	})
}
