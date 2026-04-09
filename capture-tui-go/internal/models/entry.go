package models

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/google/uuid"
	"gopkg.in/yaml.v3"
)

// Entry represents a captured idea or task
type Entry struct {
	ID        string         `json:"id" yaml:"id"`
	Title     string         `json:"title" yaml:"title"`
	Content   string         `json:"content" yaml:"content"`
	Category  string         `json:"category" yaml:"category"`
	Tags      []string       `json:"tags" yaml:"tags"`
	CreatedAt time.Time      `json:"created_at" yaml:"created_at"`
	UpdatedAt *time.Time     `json:"updated_at,omitempty" yaml:"updated_at,omitempty"`
	Tasks     []string       `json:"tasks" yaml:"tasks"`
	Metadata  EntryMetadata  `json:"metadata" yaml:"metadata"`
}

// EntryMetadata contains additional metadata for an entry
type EntryMetadata struct {
	Source         string   `json:"source" yaml:"source"`
	Priority       string   `json:"priority" yaml:"priority"`
	Author         string   `json:"author,omitempty" yaml:"author,omitempty"`
	RelatedEntries []string `json:"related_entries,omitempty" yaml:"related_entries,omitempty"`
}

// NewEntry creates a new entry with generated ID
func NewEntry(title, content, category string, tags []string) *Entry {
	now := time.Now()
	return &Entry{
		ID:        generateID(),
		Title:     title,
		Content:   content,
		Category:  category,
		Tags:      tags,
		CreatedAt: now,
		Metadata: EntryMetadata{
			Source:   "cli",
			Priority: "P2",
		},
	}
}

// generateID generates a unique entry ID
func generateID() string {
	timestamp := time.Now().Format("20060102-150405")
	shortUUID := uuid.New().String()[:6]
	return fmt.Sprintf("ideas-%s-%s", timestamp, shortUUID)
}

// ToMarkdown converts the entry to Markdown format
func (e *Entry) ToMarkdown() string {
	var sb strings.Builder

	// Frontmatter
	sb.WriteString("---\n")
	sb.WriteString(fmt.Sprintf("id: \"%s\"\n", e.ID))
	sb.WriteString(fmt.Sprintf("category: \"%s\"\n", e.Category))
	sb.WriteString(fmt.Sprintf("created_at: \"%s\"\n", e.CreatedAt.Format(time.RFC3339)))
	sb.WriteString(fmt.Sprintf("tags: %v\n", e.Tags))
	sb.WriteString(fmt.Sprintf("priority: \"%s\"\n", e.Metadata.Priority))
	sb.WriteString(fmt.Sprintf("source: \"%s\"\n", e.Metadata.Source))
	sb.WriteString("---\n\n")

	// Title
	sb.WriteString(fmt.Sprintf("# %s\n\n", e.Title))

	// Content
	sb.WriteString(e.Content)
	sb.WriteString("\n")

	// Tasks
	if len(e.Tasks) > 0 {
		sb.WriteString("\n## 关联任务\n\n")
		for _, task := range e.Tasks {
			sb.WriteString(fmt.Sprintf("- [ ] %s\n", task))
		}
	}

	return sb.String()
}

// EntryFromMarkdown parses an entry from Markdown content
func EntryFromMarkdown(content string) (*Entry, error) {
	// Extract frontmatter
	frontmatterRegex := regexp.MustCompile(`(?s)^---\n(.*?)\n---\n(.*)`)
	matches := frontmatterRegex.FindStringSubmatch(content)
	if len(matches) < 3 {
		return nil, fmt.Errorf("invalid markdown format: missing frontmatter")
	}

	var frontmatter map[string]interface{}
	if err := yaml.Unmarshal([]byte(matches[1]), &frontmatter); err != nil {
		return nil, fmt.Errorf("failed to parse frontmatter: %w", err)
	}

	body := matches[2]

	// Extract title
	titleRegex := regexp.MustCompile(`(?m)^# (.+)$`)
	titleMatch := titleRegex.FindStringSubmatch(body)
	title := "Untitled"
	if len(titleMatch) > 1 {
		title = strings.TrimSpace(titleMatch[1])
	}

	// Extract content (remove title)
	contentBody := titleRegex.ReplaceAllString(body, "")
	contentBody = strings.TrimSpace(contentBody)

	// Extract tasks
	taskRegex := regexp.MustCompile(`(?m)^- \[ \] (.+)$`)
	taskMatches := taskRegex.FindAllStringSubmatch(contentBody, -1)
	tasks := make([]string, 0, len(taskMatches))
	for _, match := range taskMatches {
		if len(match) > 1 {
			tasks = append(tasks, strings.TrimSpace(match[1]))
		}
	}

	// Remove tasks section from content
	tasksSectionRegex := regexp.MustCompile(`(?s)\n?## 关联任务\n\n(?:- \[ \] .+\n?)+`)
	contentBody = tasksSectionRegex.ReplaceAllString(contentBody, "")
	contentBody = strings.TrimSpace(contentBody)

	// Parse timestamps
	createdAt, _ := time.Parse(time.RFC3339, getString(frontmatter, "created_at"))

	entry := &Entry{
		ID:        getString(frontmatter, "id"),
		Title:     title,
		Content:   contentBody,
		Category:  getString(frontmatter, "category"),
		Tags:      getStringSlice(frontmatter, "tags"),
		CreatedAt: createdAt,
		Tasks:     tasks,
		Metadata: EntryMetadata{
			Source:   getString(frontmatter, "source"),
			Priority: getString(frontmatter, "priority"),
		},
	}

	return entry, nil
}

// Helper functions
func getString(m map[string]interface{}, key string) string {
	if v, ok := m[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

func getStringSlice(m map[string]interface{}, key string) []string {
	if v, ok := m[key]; ok {
		if arr, ok := v.([]interface{}); ok {
			result := make([]string, 0, len(arr))
			for _, item := range arr {
				if s, ok := item.(string); ok {
					result = append(result, s)
				}
			}
			return result
		}
	}
	return []string{}
}

// Update updates the entry's updated_at timestamp
func (e *Entry) Update() {
	now := time.Now()
	e.UpdatedAt = &now
}

// AddTask adds a task to the entry
func (e *Entry) AddTask(task string) {
	e.Tasks = append(e.Tasks, task)
}

// HasTasks returns true if the entry has tasks
func (e *Entry) HasTasks() bool {
	return len(e.Tasks) > 0
}

// TaskCount returns the number of tasks
func (e *Entry) TaskCount() int {
	return len(e.Tasks)
}
