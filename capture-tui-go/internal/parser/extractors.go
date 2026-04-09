package parser

import (
	"regexp"
	"strings"
)

// TaskExtractor extracts tasks from content
type TaskExtractor struct {
	patterns []*regexp.Regexp
}

// NewTaskExtractor creates a new task extractor
func NewTaskExtractor() *TaskExtractor {
	patterns := []*regexp.Regexp{
		regexp.MustCompile(`(?m)^- \[ \] (.+)$`),           // Markdown todo
		regexp.MustCompile(`(?i)TODO[:：]\s*(.+)$`),         // TODO: task
		regexp.MustCompile(`(?i)任务[:：]\s*(.+)$`),          // 任务: task
		regexp.MustCompile(`(?i)ACTION[:：]\s*(.+)$`),        // ACTION: task
	}

	return &TaskExtractor{patterns: patterns}
}

// Extract extracts tasks from content
func (te *TaskExtractor) Extract(content string) []string {
	seen := make(map[string]bool)
	var tasks []string

	for _, pattern := range te.patterns {
		matches := pattern.FindAllStringSubmatch(content, -1)
		for _, match := range matches {
			if len(match) > 1 {
				task := strings.TrimSpace(match[1])
				if task != "" && !seen[task] {
					seen[task] = true
					tasks = append(tasks, task)
				}
			}
		}
	}

	return tasks
}

// TagExtractor extracts tags from content
type TagExtractor struct {
	pattern *regexp.Regexp
}

// NewTagExtractor creates a new tag extractor
func NewTagExtractor() *TagExtractor {
	return &TagExtractor{
		pattern: regexp.MustCompile(`#(\w+)`),
	}
}

// Extract extracts tags from content
func (te *TagExtractor) Extract(content string) []string {
	matches := te.pattern.FindAllStringSubmatch(content, -1)
	seen := make(map[string]bool)
	var tags []string

	for _, match := range matches {
		if len(match) > 1 {
			tag := strings.ToLower(strings.TrimSpace(match[1]))
			if tag != "" && !seen[tag] {
				seen[tag] = true
				tags = append(tags, tag)
			}
		}
	}

	return tags
}

// PriorityExtractor extracts priority from content
type PriorityExtractor struct {
	patterns map[string][]*regexp.Regexp
}

// NewPriorityExtractor creates a new priority extractor
func NewPriorityExtractor() *PriorityExtractor {
	return &PriorityExtractor{
		patterns: map[string][]*regexp.Regexp{
			"P0": {
				regexp.MustCompile(`\bP0\b`),
				regexp.MustCompile(`【紧急】`),
				regexp.MustCompile(`【高优先级】`),
				regexp.MustCompile(`(?i)\burgent\b`),
				regexp.MustCompile(`(?i)\bcritical\b`),
				regexp.MustCompile(`(?i)\bASAP\b`),
			},
			"P1": {
				regexp.MustCompile(`\bP1\b`),
				regexp.MustCompile(`【重要】`),
				regexp.MustCompile(`(?i)\bimportant\b`),
				regexp.MustCompile(`(?i)high priority`),
			},
			"P2": {
				regexp.MustCompile(`\bP2\b`),
				regexp.MustCompile(`【一般】`),
				regexp.MustCompile(`(?i)\bnormal\b`),
				regexp.MustCompile(`(?i)low priority`),
			},
		},
	}
}

// Extract extracts priority from content
func (pe *PriorityExtractor) Extract(content string) string {
	// Check P0 first, then P1, then P2
	for _, priority := range []string{"P0", "P1", "P2"} {
		for _, pattern := range pe.patterns[priority] {
			if pattern.MatchString(content) {
				return priority
			}
		}
	}
	return "P2" // Default priority
}

// TitleExtractor extracts title from content
type TitleExtractor struct {
	maxLength int
}

// NewTitleExtractor creates a new title extractor
func NewTitleExtractor() *TitleExtractor {
	return &TitleExtractor{maxLength: 100}
}

// Extract extracts title from content
func (te *TitleExtractor) Extract(content string) string {
	lines := strings.Split(content, "\n")
	
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Check for markdown heading
		if strings.HasPrefix(line, "#") {
			line = strings.TrimLeft(line, "# ")
			return te.truncate(line)
		}

		// Use first non-empty line
		return te.truncate(line)
	}

	return "Untitled"
}

// truncate truncates text to max length
func (te *TitleExtractor) truncate(text string) string {
	if len(text) > te.maxLength {
		return text[:te.maxLength]
	}
	return text
}

// SetMaxLength sets the maximum title length
func (te *TitleExtractor) SetMaxLength(length int) {
	te.maxLength = length
}
