# Capture TUI - API Specification

## 概述

Capture TUI Go 版本的完整 API 规范，包含数据类型、调用方式和 CLI 接口参数。

---

## 1. 数据类型 (Types)

### 1.1 Entry (条目)

```go
// internal/models/entry.go
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

type EntryMetadata struct {
    Source         string   `json:"source" yaml:"source"`           // cli, file, session
    Priority       string   `json:"priority" yaml:"priority"`       // P0, P1, P2
    Author         string   `json:"author,omitempty" yaml:"author,omitempty"`
    RelatedEntries []string `json:"related_entries,omitempty" yaml:"related_entries,omitempty"`
}
```

### 1.2 Category (分类)

```go
// internal/models/category.go
type Category struct {
    Name        string     `json:"name" yaml:"name"`
    DisplayName string     `json:"display_name" yaml:"display_name"`
    Count       int        `json:"count" yaml:"count"`
    CreatedAt   time.Time  `json:"created_at" yaml:"created_at"`
    LastEntry   *time.Time `json:"last_entry,omitempty" yaml:"last_entry,omitempty"`
    Description string     `json:"description" yaml:"description"`
}
```

### 1.3 Session (会话)

```go
// internal/models/session.go
type Session struct {
    ID              string         `json:"id" yaml:"id"`
    Name            string         `json:"name" yaml:"name"`
    StartTime       time.Time      `json:"start_time" yaml:"start_time"`
    EndTime         *time.Time     `json:"end_time,omitempty" yaml:"end_time,omitempty"`
    Turns           []SessionTurn  `json:"turns" yaml:"turns"`
    Goal            string         `json:"goal,omitempty" yaml:"goal,omitempty"`
    Tool            string         `json:"tool" yaml:"tool"`
    Summary         string         `json:"summary,omitempty" yaml:"summary,omitempty"`
    ExtractedTasks  []string       `json:"extracted_tasks,omitempty" yaml:"extracted_tasks,omitempty"`
}

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
```

### 1.4 Configuration (配置)

```go
// internal/config/config.go
type Config struct {
    Version string          `mapstructure:"version"`
    Storage StorageConfig   `mapstructure:"storage"`
    Input   InputConfig     `mapstructure:"input"`
    AI      AIConfig        `mapstructure:"ai"`
    Export  ExportConfig    `mapstructure:"export"`
    Session SessionConfig   `mapstructure:"session"`
}

type StorageConfig struct {
    RootDir            string `mapstructure:"root_dir"`
    MaxCategories      int    `mapstructure:"max_categories"`
    AutoCreateCategory bool   `mapstructure:"auto_create_category"`
    ArchiveAfterDays   int    `mapstructure:"archive_after_days"`
}

type InputConfig struct {
    DefaultCategory  string `mapstructure:"default_category"`
    ExtractTasksAuto bool   `mapstructure:"extract_tasks_auto"`
    ExtractTagsAuto  bool   `mapstructure:"extract_tags_auto"`
}

type AIConfig struct {
    Enabled            bool   `mapstructure:"enabled"`
    Model              string `mapstructure:"model"`
    SummarizeOnAnalyze bool   `mapstructure:"summarize_on_analyze"`
    AutoCategorize     bool   `mapstructure:"auto_categorize"`
}

type ExportConfig struct {
    Formats []string       `mapstructure:"formats"`
    Feishu  FeishuConfig   `mapstructure:"feishu"`
}

type FeishuConfig struct {
    Enabled      bool   `mapstructure:"enabled"`
    AppID        string `mapstructure:"app_id"`
    AppSecret    string `mapstructure:"app_secret"`
    DefaultTable string `mapstructure:"default_table"`
}

type SessionConfig struct {
    CaptureDir      string `mapstructure:"capture_dir"`
    AutoCapture     bool   `mapstructure:"auto_capture"`
    CaptureThinking bool   `mapstructure:"capture_thinking"`
    MaxDuration     int    `mapstructure:"max_duration"`
}
```

### 1.5 ParsedInput (解析后的输入)

```go
// internal/parser/types.go
type InputType string

const (
    InputTypeText     InputType = "text"
    InputTypeFile     InputType = "file"
    InputTypeURL      InputType = "url"
    InputTypeMarkdown InputType = "markdown"
)

type ParsedInput struct {
    RawContent string                 `json:"raw_content"`
    InputType  InputType              `json:"input_type"`
    Title      string                 `json:"title"`
    Content    string                 `json:"content"`
    Tasks      []string               `json:"tasks"`
    Tags       []string               `json:"tags"`
    Priority   string                 `json:"priority"`
    SourcePath string                 `json:"source_path,omitempty"`
    Metadata   map[string]interface{} `json:"metadata,omitempty"`
}
```

### 1.6 AnalysisReport (分析报告)

```go
// internal/ai/types.go
type AnalysisReport struct {
    Category      string                 `json:"category"`
    GeneratedAt   time.Time              `json:"generated_at"`
    Statistics    ReportStatistics       `json:"statistics"`
    Themes        []Theme                `json:"themes"`
    Trends        TrendAnalysis          `json:"trends"`
    Tasks         []TaskInfo             `json:"tasks"`
    Recommendations []string             `json:"recommendations"`
}

type ReportStatistics struct {
    TotalEntries        int                `json:"total_entries"`
    TotalTasks          int                `json:"total_tasks"`
    UniqueTags          int                `json:"unique_tags"`
    TopTags             []TagCount         `json:"top_tags"`
    PriorityDistribution map[string]int    `json:"priority_distribution"`
}

type TagCount struct {
    Tag   string `json:"tag"`
    Count int    `json:"count"`
}

type Theme struct {
    Name           string   `json:"name"`
    RelatedEntries []string `json:"related_entries"`
}

type TrendAnalysis struct {
    MonthlyActivity map[string]int `json:"monthly_activity"`
    PeakMonth       string         `json:"peak_month,omitempty"`
}

type TaskInfo struct {
    Content     string `json:"content"`
    EntryTitle  string `json:"entry_title"`
    EntryID     string `json:"entry_id"`
    Priority    string `json:"priority"`
}
```

---

## 2. CLI 接口参数

### 2.1 全局参数

```
Global Flags:
  -c, --config string    配置文件路径 (默认: ./.capture/config.yaml)
  -r, --root-dir string  数据根目录
      --verbose          启用详细输出
      --version          显示版本信息
  -h, --help             帮助信息
```

### 2.2 子命令参数

#### `init` - 初始化项目

```
Usage: capture init [flags]

Flags:
  -r, --root-dir string   数据根目录 (默认: ./ideas)
      --force            强制重新初始化
  -h, --help             帮助信息
```

#### `add` - 添加想法

```
Usage: capture add [content] [flags]

Arguments:
  content                 想法内容（可选，如省略则进入交互模式）

Flags:
  -c, --category string   分类名称 (默认: uncategorized)
  -t, --tags strings      标签列表（逗号分隔）
      --title string      指定标题（默认识别第一行）
  -p, --priority string   优先级: P0, P1, P2 (默认: P2)
  -f, --file string       从文件读取内容
      --interactive       强制交互式输入
  -h, --help              帮助信息

Examples:
  capture add "优化登录页面" -c features -t ui,performance -p P1
  capture add -f ./ideas.md -c backlog
  capture add --interactive
```

#### `categories` - 分类管理

```
Usage: capture categories <subcommand> [flags]

Subcommands:
  list                    列出所有分类
  create                  创建新分类
  show                    显示分类详情
  delete                  删除分类

Flags for create:
      --display-name string   显示名称
      --description string    描述

Flags for show/delete:
      --name string           分类名称

Examples:
  capture categories list
  capture categories create bugs --display-name="缺陷跟踪"
  capture categories show features
```

#### `analyze` - 分析分类

```
Usage: capture analyze <category> [flags]

Arguments:
  category                要分析的分类名称

Flags:
  -o, --output string     输出文件路径
      --format string     输出格式: markdown, json (默认: markdown)
      --summary-only      仅输出摘要
  -h, --help              帮助信息

Examples:
  capture analyze features
  capture analyze features -o ./analysis.md
  capture analyze features --format json
```

#### `export` - 导出数据

```
Usage: capture export [flags]

Flags:
  -f, --format string     导出格式: csv, json, markdown (默认: markdown)
  -o, --output string     输出文件路径（必需）
  -c, --category string   按分类过滤
      --tags strings      按标签过滤
      --tasks-only        仅导出包含任务的条目
      --since string      起始日期 (YYYY-MM-DD)
      --until string      结束日期 (YYYY-MM-DD)
  -h, --help              帮助信息

Examples:
  capture export -f csv -o ./export.csv
  capture export -f markdown -c features -o ./features.md
  capture export --tasks-only -f csv -o ./tasks.csv
```

#### `session` - 会话管理

```
Usage: capture session <subcommand> [flags]

Subcommands:
  start                   开始新会话
  end                     结束当前会话
  list                    列出所有会话
  show                    显示会话详情
  export                  导出会话

Flags for start:
  -n, --name string       会话名称（必需）
  -g, --goal string       会话目标
      --tool string       使用的工具 (默认: capture-cli)

Flags for end:
  -s, --summary string    会话总结

Flags for show/export:
      --id string         会话 ID

Flags for export:
      --format string     导出格式: markdown, json (默认: markdown)
  -o, --output string     输出文件路径

Examples:
  capture session start -n "架构设计" -g "设计API"
  capture session end -s "完成了设计"
  capture session list
  capture session export --id sess-xxx -o ./session.md
```

#### `stats` - 显示统计

```
Usage: capture stats [flags]

Flags:
      --category string   指定分类统计
      --json              以 JSON 格式输出
  -h, --help              帮助信息
```

---

## 3. 内部 API 调用方式

### 3.1 Client API

```go
// pkg/client/client.go
package client

type CaptureClient interface {
    // Entry 管理
    AddIdea(content string, opts AddOptions) (*models.Entry, error)
    AddFromFile(filePath string, opts AddOptions) (*models.Entry, error)
    GetEntry(entryID string) (*models.Entry, error)
    ListEntries(opts ListOptions) ([]*models.Entry, error)
    DeleteEntry(entryID string) error
    
    // Category 管理
    CreateCategory(name string, opts CategoryOptions) (*models.Category, error)
    ListCategories() ([]*models.Category, error)
    GetCategory(name string) (*models.Category, error)
    DeleteCategory(name string, force bool) error
    
    // 分析
    AnalyzeCategory(category string) (*ai.AnalysisReport, error)
    
    // 统计
    GetStats() (*Stats, error)
}

type AddOptions struct {
    Category string
    Tags     []string
    Title    string
    Priority string
}

type ListOptions struct {
    Category  string
    Tags      []string
    HasTasks  *bool
    Since     *time.Time
    Until     *time.Time
}

type CategoryOptions struct {
    DisplayName string
    Description string
}
```

### 3.2 Session Manager API

```go
// internal/session/manager.go
package session

type Manager interface {
    StartSession(name, goal, tool string) (*models.Session, error)
    EndSession(summary string) (*models.Session, error)
    GetActiveSession() (*models.Session, error)
    IsActive() bool
    
    AddTurn(userInput, aiResponse, thinking string, skillsUsed []string, model string) (*models.SessionTurn, error)
    
    ListSessions() ([]SessionInfo, error)
    LoadSession(sessionID string) (*models.Session, error)
    DeleteSession(sessionID string) error
    ExportSession(sessionID string, format string) (string, error)
}

type SessionInfo struct {
    ID          string
    Name        string
    StartTime   time.Time
    EndTime     *time.Time
    TurnCount   int
    Duration    time.Duration
}
```

### 3.3 Exporter API

```go
// internal/exporters/interface.go
package exporters

type Exporter interface {
    Export(entries []*models.Entry, outputPath string) error
    ExportToString(entries []*models.Entry) (string, error)
    GetFormat() string
}

type ExporterFactory interface {
    GetExporter(format string) (Exporter, error)
    SupportedFormats() []string
}
```

---

## 4. 配置文件格式

### 4.1 YAML 配置示例

```yaml
# .capture/config.yaml
version: "1.0"

storage:
  root_dir: "./ideas"
  max_categories: 10
  auto_create_category: true
  archive_after_days: 90

input:
  default_category: "uncategorized"
  extract_tasks_auto: true
  extract_tags_auto: true

ai:
  enabled: true
  model: "kimi"
  summarize_on_analyze: true
  auto_categorize: false

export:
  formats: ["md", "csv", "json"]
  feishu:
    enabled: false
    app_id: "${FEISHU_APP_ID}"
    app_secret: "${FEISHU_APP_SECRET}"
    default_table: ""

session:
  capture_dir: "./docs/capture-tui/sessions"
  auto_capture: true
  capture_thinking: true
  max_duration: 3600
```

### 4.2 环境变量支持

| 环境变量 | 说明 | 优先级 |
|---------|------|--------|
| `CAPTURE_CONFIG` | 配置文件路径 | 高 |
| `CAPTURE_ROOT_DIR` | 数据根目录 | 高 |
| `FEISHU_APP_ID` | 飞书 App ID | 中 |
| `FEISHU_APP_SECRET` | 飞书 App Secret | 中 |
| `CAPTURE_DEBUG` | 调试模式 | 低 |

---

## 5. 错误码规范

```go
// internal/errors/errors.go
package errors

const (
    ErrCodeInvalidInput      = "INVALID_INPUT"
    ErrCodeCategoryNotFound  = "CATEGORY_NOT_FOUND"
    ErrCodeCategoryLimit     = "CATEGORY_LIMIT_EXCEEDED"
    ErrCodeEntryNotFound     = "ENTRY_NOT_FOUND"
    ErrCodeSessionNotFound   = "SESSION_NOT_FOUND"
    ErrCodeInvalidFormat     = "INVALID_FORMAT"
    ErrCodeExportFailed      = "EXPORT_FAILED"
    ErrCodeConfigError       = "CONFIG_ERROR"
    ErrCodeStorageError      = "STORAGE_ERROR"
    ErrCodePermissionDenied  = "PERMISSION_DENIED"
)

type CaptureError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

func (e *CaptureError) Error() string {
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}
```

---

## 6. 版本兼容性

| 版本 | CLI 格式 | 配置文件 | 数据格式 |
|------|----------|----------|----------|
| v1.0 | 当前格式 | v1.0 | entry-v1 |

---

## 7. 参考实现

- Go 版本: `./cmd/capture/`
- Python 版本: `./capture_tui/`
