package main

import (
	"fmt"
	"os"

	"github.com/capture-tui/capture/internal/config"
	"github.com/spf13/cobra"
)

var (
	cfgFile string
	rootDir string
	verbose bool
)

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

var rootCmd = &cobra.Command{
	Use:   "capture",
	Short: "Capture TUI - 终端输入捕获与管理工具",
	Long: `Capture TUI is a terminal-based tool for capturing and managing ideas,
tasks, and plans. It supports categorization, analysis, and export to various formats.`,
	PersistentPreRun: func(cmd *cobra.Command, args []string) {
		// Load configuration
		cfg, err := config.Load(cfgFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Warning: failed to load config: %v\n", err)
		}
		
		// Override rootDir if provided
		if rootDir != "" {
			cfg.Storage.RootDir = rootDir
		}
		
		// Store config in context for subcommands
		cmd.SetContext(config.WithConfig(cmd.Context(), cfg))
	},
}

func init() {
	rootCmd.PersistentFlags().StringVarP(&cfgFile, "config", "c", "", "配置文件路径")
	rootCmd.PersistentFlags().StringVarP(&rootDir, "root-dir", "r", "", "数据根目录")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "启用详细输出")

	// Add subcommands
	rootCmd.AddCommand(initCmd)
	rootCmd.AddCommand(addCmd)
	rootCmd.AddCommand(categoriesCmd)
	rootCmd.AddCommand(analyzeCmd)
	rootCmd.AddCommand(exportCmd)
	rootCmd.AddCommand(sessionCmd)
	rootCmd.AddCommand(statsCmd)
}

// initCmd initializes a new project
var initCmd = &cobra.Command{
	Use:   "init",
	Short: "初始化项目",
	Long:  `Initialize a new Capture TUI project with the specified root directory.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg := config.DefaultConfig()
		
		if rootDir != "" {
			cfg.Storage.RootDir = rootDir
		}
		
		// Check if already initialized
		configPath := cfg.ConfigDir()
		if _, err := os.Stat(configPath); err == nil {
			force, _ := cmd.Flags().GetBool("force")
			if !force {
				fmt.Println("Project already exists. Use --force to overwrite.")
				return nil
			}
		}
		
		if err := cfg.InitProject(cfg.Storage.RootDir); err != nil {
			return fmt.Errorf("failed to initialize project: %w", err)
		}
		
		fmt.Printf("✓ Project initialized at: %s\n", cfg.Storage.RootDir)
		fmt.Printf("  Config file: %s\n", configPath)
		return nil
	},
}

func init() {
	initCmd.Flags().Bool("force", false, "强制重新初始化")
}

// addCmd adds a new entry
var addCmd = &cobra.Command{
	Use:   "add [content]",
	Short: "添加想法/任务",
	Long:  `Add a new idea or task to the capture system.`,
	Example: `  capture add "优化登录页面" -c features -t ui,performance -p P1
  capture add -f ./ideas.md -c backlog
  capture add --interactive`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Implementation will be added
		fmt.Println("Add command - to be implemented")
		return nil
	},
}

func init() {
	addCmd.Flags().StringP("category", "c", "", "分类名称")
	addCmd.Flags().StringSliceP("tags", "t", []string{}, "标签列表（逗号分隔）")
	addCmd.Flags().String("title", "", "指定标题")
	addCmd.Flags().StringP("priority", "p", "P2", "优先级: P0, P1, P2")
	addCmd.Flags().StringP("file", "f", "", "从文件读取内容")
	addCmd.Flags().BoolP("interactive", "i", false, "交互式输入")
}

// categoriesCmd manages categories
var categoriesCmd = &cobra.Command{
	Use:   "categories",
	Short: "分类管理",
	Long:  `Manage categories for organizing entries.`,
}

var categoriesListCmd = &cobra.Command{
	Use:   "list",
	Short: "列出所有分类",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Categories list - to be implemented")
		return nil
	},
}

var categoriesCreateCmd = &cobra.Command{
	Use:   "create [name]",
	Short: "创建新分类",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Printf("Create category: %s\n", args[0])
		return nil
	},
}

var categoriesShowCmd = &cobra.Command{
	Use:   "show [name]",
	Short: "显示分类详情",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Printf("Show category: %s\n", args[0])
		return nil
	},
}

func init() {
	categoriesCmd.AddCommand(categoriesListCmd)
	categoriesCmd.AddCommand(categoriesCreateCmd)
	categoriesCmd.AddCommand(categoriesShowCmd)
	
	categoriesCreateCmd.Flags().String("display-name", "", "显示名称")
	categoriesCreateCmd.Flags().String("description", "", "描述")
}

// analyzeCmd analyzes a category
var analyzeCmd = &cobra.Command{
	Use:   "analyze [category]",
	Short: "分析分类内容",
	Args:  cobra.ExactArgs(1),
	Example: `  capture analyze features
  capture analyze features -o ./analysis.md
  capture analyze features --format json`,
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Printf("Analyze category: %s\n", args[0])
		return nil
	},
}

func init() {
	analyzeCmd.Flags().StringP("output", "o", "", "输出文件路径")
	analyzeCmd.Flags().String("format", "markdown", "输出格式: markdown, json")
	analyzeCmd.Flags().Bool("summary-only", false, "仅输出摘要")
}

// exportCmd exports data
var exportCmd = &cobra.Command{
	Use:   "export",
	Short: "导出数据",
	Long:  `Export entries to various formats.`,
	Example: `  capture export -f csv -o ./export.csv
  capture export -f json -c features -o ./features.json
  capture export --tasks-only -f csv`,
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Export - to be implemented")
		return nil
	},
}

func init() {
	exportCmd.Flags().StringP("format", "f", "markdown", "导出格式: csv, json, markdown")
	exportCmd.Flags().StringP("output", "o", "", "输出文件路径（必需）")
	exportCmd.Flags().StringP("category", "c", "", "按分类过滤")
	exportCmd.Flags().StringSlice("tags", []string{}, "按标签过滤")
	exportCmd.Flags().Bool("tasks-only", false, "仅导出包含任务的条目")
	exportCmd.Flags().String("since", "", "起始日期 (YYYY-MM-DD)")
	exportCmd.Flags().String("until", "", "结束日期 (YYYY-MM-DD)")
	exportCmd.MarkFlagRequired("output")
}

// sessionCmd manages sessions
var sessionCmd = &cobra.Command{
	Use:   "session",
	Short: "会话管理",
	Long:  `Record and manage conversation sessions.`,
}

var sessionStartCmd = &cobra.Command{
	Use:   "start",
	Short: "开始新会话",
	Example: `  capture session start -n "架构设计" -g "设计API"`,
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Session start - to be implemented")
		return nil
	},
}

var sessionEndCmd = &cobra.Command{
	Use:   "end",
	Short: "结束当前会话",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Session end - to be implemented")
		return nil
	},
}

var sessionListCmd = &cobra.Command{
	Use:   "list",
	Short: "列出所有会话",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Session list - to be implemented")
		return nil
	},
}

func init() {
	sessionCmd.AddCommand(sessionStartCmd)
	sessionCmd.AddCommand(sessionEndCmd)
	sessionCmd.AddCommand(sessionListCmd)
	
	sessionStartCmd.Flags().StringP("name", "n", "", "会话名称（必需）")
	sessionStartCmd.Flags().StringP("goal", "g", "", "会话目标")
	sessionStartCmd.Flags().String("tool", "capture-cli", "使用的工具")
	sessionStartCmd.MarkFlagRequired("name")
	
	sessionEndCmd.Flags().StringP("summary", "s", "", "会话总结")
}

// statsCmd shows statistics
var statsCmd = &cobra.Command{
	Use:   "stats",
	Short: "显示统计信息",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Stats - to be implemented")
		return nil
	},
}

func init() {
	statsCmd.Flags().String("category", "", "指定分类统计")
	statsCmd.Flags().Bool("json", false, "以 JSON 格式输出")
}
