package config

import (
	"context"
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/viper"
)

// Config holds the application configuration
type Config struct {
	Version string          `mapstructure:"version"`
	Storage StorageConfig   `mapstructure:"storage"`
	Input   InputConfig     `mapstructure:"input"`
	AI      AIConfig        `mapstructure:"ai"`
	Export  ExportConfig    `mapstructure:"export"`
	Session SessionConfig   `mapstructure:"session"`
}

// StorageConfig holds storage-related configuration
type StorageConfig struct {
	RootDir            string `mapstructure:"root_dir"`
	MaxCategories      int    `mapstructure:"max_categories"`
	AutoCreateCategory bool   `mapstructure:"auto_create_category"`
	ArchiveAfterDays   int    `mapstructure:"archive_after_days"`
}

// InputConfig holds input-related configuration
type InputConfig struct {
	DefaultCategory  string `mapstructure:"default_category"`
	ExtractTasksAuto bool   `mapstructure:"extract_tasks_auto"`
	ExtractTagsAuto  bool   `mapstructure:"extract_tags_auto"`
}

// AIConfig holds AI-related configuration
type AIConfig struct {
	Enabled            bool   `mapstructure:"enabled"`
	Model              string `mapstructure:"model"`
	SummarizeOnAnalyze bool   `mapstructure:"summarize_on_analyze"`
	AutoCategorize     bool   `mapstructure:"auto_categorize"`
}

// ExportConfig holds export-related configuration
type ExportConfig struct {
	Formats []string     `mapstructure:"formats"`
	Feishu  FeishuConfig `mapstructure:"feishu"`
}

// FeishuConfig holds Feishu export configuration
type FeishuConfig struct {
	Enabled      bool   `mapstructure:"enabled"`
	AppID        string `mapstructure:"app_id"`
	AppSecret    string `mapstructure:"app_secret"`
	DefaultTable string `mapstructure:"default_table"`
}

// SessionConfig holds session-related configuration
type SessionConfig struct {
	CaptureDir      string `mapstructure:"capture_dir"`
	AutoCapture     bool   `mapstructure:"auto_capture"`
	CaptureThinking bool   `mapstructure:"capture_thinking"`
	MaxDuration     int    `mapstructure:"max_duration"`
}

// DefaultConfig returns the default configuration
func DefaultConfig() *Config {
	return &Config{
		Version: "1.0",
		Storage: StorageConfig{
			RootDir:            "./ideas",
			MaxCategories:      10,
			AutoCreateCategory: true,
			ArchiveAfterDays:   90,
		},
		Input: InputConfig{
			DefaultCategory:  "uncategorized",
			ExtractTasksAuto: true,
			ExtractTagsAuto:  true,
		},
		AI: AIConfig{
			Enabled:            true,
			Model:              "kimi",
			SummarizeOnAnalyze: true,
			AutoCategorize:     false,
		},
		Export: ExportConfig{
			Formats: []string{"md", "csv", "json"},
			Feishu: FeishuConfig{
				Enabled: false,
			},
		},
		Session: SessionConfig{
			CaptureDir:      "./docs/capture-tui/sessions",
			AutoCapture:     true,
			CaptureThinking: true,
			MaxDuration:     3600,
		},
	}
}

// Load loads configuration from file and environment
func Load(configPath string) (*Config, error) {
	v := viper.New()

	// Set defaults
	setDefaults(v)

	// Set config file if provided
	if configPath != "" {
		v.SetConfigFile(configPath)
	} else {
		// Search for config in default locations
		v.SetConfigName("config")
		v.SetConfigType("yaml")
		v.AddConfigPath("./.capture")
		v.AddConfigPath("./ideas/.capture")
		v.AddConfigPath("$HOME/.capture")
	}

	// Environment variables
	v.SetEnvPrefix("CAPTURE")
	v.AutomaticEnv()

	// Read config
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("failed to read config: %w", err)
		}
		// Config file not found, use defaults
	}

	var config Config
	if err := v.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	// Expand environment variables in paths
	config.Storage.RootDir = os.ExpandEnv(config.Storage.RootDir)
	config.Session.CaptureDir = os.ExpandEnv(config.Session.CaptureDir)

	return &config, nil
}

// setDefaults sets default values for viper
func setDefaults(v *viper.Viper) {
	defaults := DefaultConfig()
	v.SetDefault("version", defaults.Version)
	v.SetDefault("storage", defaults.Storage)
	v.SetDefault("input", defaults.Input)
	v.SetDefault("ai", defaults.AI)
	v.SetDefault("export", defaults.Export)
	v.SetDefault("session", defaults.Session)
}

// Save saves the configuration to file
func (c *Config) Save(path string) error {
	// Ensure directory exists
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	v := viper.New()
	v.Set("version", c.Version)
	v.Set("storage", c.Storage)
	v.Set("input", c.Input)
	v.Set("ai", c.AI)
	v.Set("export", c.Export)
	v.Set("session", c.Session)

	v.SetConfigFile(path)
	return v.WriteConfig()
}

// InitProject initializes a new project with the given root directory
func (c *Config) InitProject(rootDir string) error {
	if rootDir != "" {
		c.Storage.RootDir = rootDir
	}

	// Create directories
	dirs := []string{
		c.Storage.RootDir,
		filepath.Join(c.Storage.RootDir, ".capture"),
		filepath.Join(c.Storage.RootDir, ".capture", "templates"),
		filepath.Join(c.Storage.RootDir, ".capture", "sessions"),
		filepath.Join(c.Storage.RootDir, c.Input.DefaultCategory),
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("failed to create directory %s: %w", dir, err)
		}
	}

	// Save config
	configPath := filepath.Join(c.Storage.RootDir, ".capture", "config.yaml")
	if err := c.Save(configPath); err != nil {
		return fmt.Errorf("failed to save config: %w", err)
	}

	// Create templates
	if err := c.createTemplates(); err != nil {
		return fmt.Errorf("failed to create templates: %w", err)
	}

	// Create initial index
	if err := c.createIndex(); err != nil {
		return fmt.Errorf("failed to create index: %w", err)
	}

	return nil
}

// createTemplates creates template files
func (c *Config) createTemplates() error {
	ideaTemplate := `---
id: "{{.ID}}"
category: "{{.Category}}"
created_at: "{{.CreatedAt}}"
tags: {{.Tags}}
priority: "{{.Metadata.Priority}}"
source: "{{.Metadata.Source}}"
---

# {{.Title}}

{{.Content}}
{{if .Tasks}}
## 关联任务
{{range .Tasks}}
- [ ] {{.}}
{{end}}
{{end}}
`

	templatePath := filepath.Join(c.Storage.RootDir, ".capture", "templates", "idea.md.tpl")
	return os.WriteFile(templatePath, []byte(ideaTemplate), 0644)
}

// createIndex creates the initial index file
func (c *Config) createIndex() error {
	index := `{
  "version": "1.0",
  "last_updated": null,
  "categories": [],
  "entries": [],
  "stats": {
    "total_entries": 0,
    "total_categories": 0,
    "pending_tasks": 0
  }
}`

	indexPath := filepath.Join(c.Storage.RootDir, ".capture", "index.json")
	return os.WriteFile(indexPath, []byte(index), 0644)
}


type contextKey string

const configKey contextKey = "config"

// WithConfig stores config in context
func WithConfig(ctx context.Context, cfg *Config) context.Context {
	return context.WithValue(ctx, configKey, cfg)
}

// FromConfig retrieves config from context
func FromConfig(ctx context.Context) *Config {
	if cfg, ok := ctx.Value(configKey).(*Config); ok {
		return cfg
	}
	return DefaultConfig()
}

// RootDir returns the absolute root directory
func (c *Config) RootDir() string {
	abs, _ := filepath.Abs(c.Storage.RootDir)
	return abs
}

// ConfigDir returns the config directory path
func (c *Config) ConfigDir() string {
	return filepath.Join(c.Storage.RootDir, ".capture")
}
