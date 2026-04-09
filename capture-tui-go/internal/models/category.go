package models

import "time"

// Category represents a category for organizing entries
type Category struct {
	Name        string     `json:"name" yaml:"name"`
	DisplayName string     `json:"display_name" yaml:"display_name"`
	Count       int        `json:"count" yaml:"count"`
	CreatedAt   time.Time  `json:"created_at" yaml:"created_at"`
	LastEntry   *time.Time `json:"last_entry,omitempty" yaml:"last_entry,omitempty"`
	Description string     `json:"description" yaml:"description"`
}

// NewCategory creates a new category
func NewCategory(name, displayName, description string) *Category {
	return &Category{
		Name:        name,
		DisplayName: displayName,
		Count:       0,
		CreatedAt:   time.Now(),
		Description: description,
	}
}

// UpdateCount updates the entry count and last entry time
func (c *Category) UpdateCount(delta int) {
	c.Count += delta
	if c.Count < 0 {
		c.Count = 0
	}
	if delta > 0 {
		now := time.Now()
		c.LastEntry = &now
	}
}

// SetDisplayName sets the display name, defaulting to the category name
func (c *Category) SetDisplayName(displayName string) {
	if displayName == "" {
		c.DisplayName = c.Name
	} else {
		c.DisplayName = displayName
	}
}
