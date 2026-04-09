package models

import (
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"
)

// Session represents a recorded conversation session
type Session struct {
	ID             string        `json:"id" yaml:"id"`
	Name           string        `json:"name" yaml:"name"`
	StartTime      time.Time     `json:"start_time" yaml:"start_time"`
	EndTime        *time.Time    `json:"end_time,omitempty" yaml:"end_time,omitempty"`
	Turns          []SessionTurn `json:"turns" yaml:"turns"`
	Goal           string        `json:"goal,omitempty" yaml:"goal,omitempty"`
	Tool           string        `json:"tool" yaml:"tool"`
	Summary        string        `json:"summary,omitempty" yaml:"summary,omitempty"`
	ExtractedTasks []string      `json:"extracted_tasks,omitempty" yaml:"extracted_tasks,omitempty"`
}

// SessionTurn represents a single turn in a conversation
type SessionTurn struct {
	TurnNumber int                    `json:"turn_number" yaml:"turn_number"`
	UserInput  string                 `json:"user_input" yaml:"user_input"`
	AIResponse string                 `json:"ai_response" yaml:"ai_response"`
	Thinking   string                 `json:"thinking,omitempty" yaml:"thinking,omitempty"`
	SkillsUsed []string               `json:"skills_used,omitempty" yaml:"skills_used,omitempty"`
	Model      string                 `json:"model,omitempty" yaml:"model,omitempty"`
	Timestamp  time.Time              `json:"timestamp" yaml:"timestamp"`
	Metadata   map[string]interface{} `json:"metadata,omitempty" yaml:"metadata,omitempty"`
}

// NewSession creates a new session
func NewSession(name, goal, tool string) *Session {
	if tool == "" {
		tool = "capture-cli"
	}
	return &Session{
		ID:        generateSessionID(),
		Name:      name,
		StartTime: time.Now(),
		Goal:      goal,
		Tool:      tool,
		Turns:     []SessionTurn{},
	}
}

// generateSessionID generates a unique session ID
func generateSessionID() string {
	timestamp := time.Now().Format("20060102-150405")
	shortUUID := uuid.New().String()[:6]
	return fmt.Sprintf("sess-%s-%s", timestamp, shortUUID)
}

// AddTurn adds a turn to the session
func (s *Session) AddTurn(turn SessionTurn) {
	turn.TurnNumber = len(s.Turns) + 1
	s.Turns = append(s.Turns, turn)
}

// End ends the session
func (s *Session) End() {
	now := time.Now()
	s.EndTime = &now
}

// Duration returns the session duration in seconds
func (s *Session) Duration() float64 {
	end := s.EndTime
	if end == nil {
		endTime := time.Now()
		end = &endTime
	}
	return end.Sub(s.StartTime).Seconds()
}

// AllSkills returns all unique skills used in the session
func (s *Session) AllSkills() []string {
	skillMap := make(map[string]bool)
	for _, turn := range s.Turns {
		for _, skill := range turn.SkillsUsed {
			skillMap[skill] = true
		}
	}

	skills := make([]string, 0, len(skillMap))
	for skill := range skillMap {
		skills = append(skills, skill)
	}
	return skills
}

// SkillUsageCounts returns the count of each skill usage
func (s *Session) SkillUsageCounts() map[string]int {
	counts := make(map[string]int)
	for _, turn := range s.Turns {
		for _, skill := range turn.SkillsUsed {
			counts[skill]++
		}
	}
	return counts
}

// IsActive returns true if the session is still active
func (s *Session) IsActive() bool {
	return s.EndTime == nil
}

// ToMarkdown converts the session to Markdown format
func (s *Session) ToMarkdown() string {
	var sb strings.Builder

	// Frontmatter
	sb.WriteString("---\n")
	sb.WriteString(fmt.Sprintf("session_id: \"%s\"\n", s.ID))
	sb.WriteString(fmt.Sprintf("name: \"%s\"\n", s.Name))
	sb.WriteString(fmt.Sprintf("start_time: \"%s\"\n", s.StartTime.Format(time.RFC3339)))
	if s.EndTime != nil {
		sb.WriteString(fmt.Sprintf("end_time: \"%s\"\n", s.EndTime.Format(time.RFC3339)))
	}
	sb.WriteString(fmt.Sprintf("tool: \"%s\"\n", s.Tool))
	sb.WriteString(fmt.Sprintf("skills_used: %v\n", s.AllSkills()))
	sb.WriteString("---\n\n")

	// Title
	sb.WriteString(fmt.Sprintf("# %s\n\n", s.Name))

	// Goal
	if s.Goal != "" {
		sb.WriteString("## 用户目标\n\n")
		sb.WriteString(s.Goal)
		sb.WriteString("\n\n")
	}

	// Conversation
	sb.WriteString("## 对话过程\n\n")
	for _, turn := range s.Turns {
		sb.WriteString(fmt.Sprintf("### Turn %d\n\n", turn.TurnNumber))
		sb.WriteString(fmt.Sprintf("**时间**: %s\n\n", turn.Timestamp.Format("15:04:05")))
		sb.WriteString(fmt.Sprintf("**用户**: %s\n\n", turn.UserInput))
		sb.WriteString(fmt.Sprintf("**AI**: %s\n\n", turn.AIResponse))

		if turn.Thinking != "" {
			sb.WriteString(fmt.Sprintf("**思考过程**: %s\n\n", turn.Thinking))
		}
		if len(turn.SkillsUsed) > 0 {
			sb.WriteString(fmt.Sprintf("**使用技能**: %s\n\n", strings.Join(turn.SkillsUsed, ", ")))
		}
		sb.WriteString("\n")
	}

	// Skill usage analysis
	skillCounts := s.SkillUsageCounts()
	if len(skillCounts) > 0 {
		sb.WriteString("## 技能使用分析\n\n")
		sb.WriteString("| 技能 | 使用次数 |\n")
		sb.WriteString("|------|---------|\n")
		for skill, count := range skillCounts {
			sb.WriteString(fmt.Sprintf("| %s | %d |\n", skill, count))
		}
		sb.WriteString("\n")
	}

	// Extracted tasks
	if len(s.ExtractedTasks) > 0 {
		sb.WriteString("## 提取的行动项\n\n")
		for _, task := range s.ExtractedTasks {
			sb.WriteString(fmt.Sprintf("- [ ] %s\n", task))
		}
		sb.WriteString("\n")
	}

	return sb.String()
}

// SessionInfo contains summary information about a session
type SessionInfo struct {
	ID        string     `json:"id"`
	Name      string     `json:"name"`
	StartTime time.Time  `json:"start_time"`
	EndTime   *time.Time `json:"end_time,omitempty"`
	TurnCount int        `json:"turn_count"`
}

// ToSessionInfo converts Session to SessionInfo
func (s *Session) ToSessionInfo() SessionInfo {
	return SessionInfo{
		ID:        s.ID,
		Name:      s.Name,
		StartTime: s.StartTime,
		EndTime:   s.EndTime,
		TurnCount: len(s.Turns),
	}
}
