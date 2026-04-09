# Feature: Analyze Category
# 分类分析功能

Feature: Analyze Category Content
  As a user
  I want to analyze the content of a category
  So that I can understand trends, extract tasks, and generate insights

  Background:
    Given an initialized project at "./ideas"

  # ============================================================================
  # 基本分析
  # ============================================================================
  
  Scenario: Analyze empty category
    Given an empty category "empty-cat"
    When I run "capture analyze empty-cat"
    Then the command should succeed
    And the output should contain "No entries found"

  Scenario: Analyze category with entries
    Given the following entries exist in category "features":
      | title       | tags              | priority | tasks        |
      | Feature A   | ui,important      | P1       | Task 1       |
      | Feature B   | api,backend       | P2       | Task 2,Task 3|
      | Feature C   | ui,performance    | P1       |              |
    When I run "capture analyze features"
    Then the command should succeed
    And the output should contain "Total entries: 3"
    And the output should contain "Total tasks: 3"

  # ============================================================================
  # 统计信息
  # ============================================================================
  
  Scenario: Show statistics
    Given 5 entries exist in category "features"
    And they have a total of 12 tasks
    And they have tags ["ui", "api", "performance"]
    When I run "capture analyze features"
    Then the output should contain:
      | text              |
      | Statistics        |
      | Total entries: 5  |
      | Total tasks: 12   |
      | Unique tags: 3    |

  Scenario: Show priority distribution
    Given entries with priorities:
      | priority | count |
      | P0       | 2     |
      | P1       | 5     |
      | P2       | 3     |
    When I run "capture analyze features"
    Then the output should contain "Priority Distribution"
    And the output should contain "P0: 2"
    And the output should contain "P1: 5"
    And the output should contain "P2: 3"

  Scenario: Show top tags
    Given entries with tag frequencies:
      | tag         | count |
      | ui          | 10    |
      | api         | 8     |
      | performance | 5     |
      | bug         | 3     |
    When I run "capture analyze features"
    Then the output should contain "Top Tags"
    And the output should show "ui" with count 10
    And the output should show "api" with count 8

  # ============================================================================
  # 主题提取
  # ============================================================================
  
  Scenario: Extract themes from tags
    Given the following entries exist:
      | title | tags           |
      | E1    | frontend,ui    |
      | E2    | frontend,ux    |
      | E3    | backend,api    |
      | E4    | backend,db     |
    When I run "capture analyze features"
    Then the output should contain "Themes"
    And the output should list theme "Frontend" with related entries
    And the output should list theme "Backend" with related entries

  # ============================================================================
  # 任务汇总
  # ============================================================================
  
  Scenario: Aggregate tasks by priority
    Given entries with tasks:
      | entry | task      | priority |
      | E1    | Task P0-1 | P0       |
      | E1    | Task P0-2 | P0       |
      | E2    | Task P1-1 | P1       |
      | E3    | Task P2-1 | P2       |
    When I run "capture analyze features"
    Then the output should contain "Tasks by Priority"
    And the output should show P0 tasks first
    And the output should show "Task P0-1" and "Task P0-2"

  # ============================================================================
  # 输出格式
  # ============================================================================
  
  Scenario: Output as Markdown
    Given 3 entries exist in category "features"
    When I run "capture analyze features --format=markdown"
    Then the command should succeed
    And the output should be valid Markdown
    And the output should contain "# features Analysis"

  Scenario: Output as JSON
    Given 3 entries exist in category "features"
    When I run "capture analyze features --format=json"
    Then the command should succeed
    And the output should be valid JSON
    And the JSON should have fields:
      | field           |
      | category        |
      | generated_at    |
      | statistics      |
      | themes          |
      | tasks           |

  Scenario: Save to file
    Given 3 entries exist in category "features"
    When I run "capture analyze features -o ./analysis.md"
    Then the command should succeed
    And the file "./analysis.md" should exist
    And the file should contain the analysis report

  Scenario: Summary only mode
    Given 10 entries exist in category "features"
    When I run "capture analyze features --summary-only"
    Then the output should contain only summary statistics
    And the output should not contain individual entry details

  # ============================================================================
  # 趋势分析
  # ============================================================================
  
  Scenario: Show monthly activity
    Given entries created in:
      | month    | count |
      | 2024-01  | 5     |
      | 2024-02  | 8     |
      | 2024-03  | 3     |
    When I run "capture analyze features"
    Then the output should contain "Activity Trends"
    And the output should show peak month "2024-02"

  # ============================================================================
  # 建议生成
  # ============================================================================
  
  Scenario: Generate recommendations
    Given 10 P0 priority tasks exist
    When I run "capture analyze features"
    Then the output should contain "Recommendations"
    And the output should contain suggestion about P0 tasks

  Scenario: Recommend tag consolidation
    Given entries with similar tags:
      | tag      | count |
      | ui       | 5     |
      | UI       | 3     |
      | user-interface | 2 |
    When I run "capture analyze features"
    Then the output may suggest tag consolidation
