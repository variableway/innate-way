# Feature: Export Data
# 数据导出功能

Feature: Export Entries and Tasks
  As a user
  I want to export my entries and tasks in various formats
  So that I can use them in other tools or share with others

  Background:
    Given an initialized project at "./ideas"

  # ============================================================================
  # CSV 导出
  # ============================================================================
  
  Scenario: Export to CSV
    Given the following entries exist:
      | title   | category  | tags      | priority |
      | Entry 1 | features  | ui,important | P1    |
      | Entry 2 | bugs      | urgent    | P0       |
    When I run "capture export -f csv -o ./export.csv"
    Then the command should succeed
    And the file "./export.csv" should exist
    And the CSV should have header row
    And the CSV should contain 2 data rows
    And the CSV should have columns:
      | column    |
      | id        |
      | title     |
      | category  |
      | tags      |
      | priority  |

  Scenario: Export tasks only to CSV
    Given entries with tasks:
      | entry | tasks              |
      | E1    | Task 1, Task 2     |
      | E2    | Task 3             |
      | E3    | (no tasks)         |
    When I run "capture export -f csv --tasks-only -o ./tasks.csv"
    Then the CSV should contain 3 task rows
    And the CSV should not contain entry E3

  # ============================================================================
  # JSON 导出
  # ============================================================================
  
  Scenario: Export to JSON
    Given 3 entries exist
    When I run "capture export -f json -o ./export.json"
    Then the command should succeed
    And the file "./export.json" should exist
    And the JSON should be a valid array
    And the array should have 3 items

  Scenario: Export with pretty print
    Given 2 entries exist
    When I run "capture export -f json -o ./pretty.json"
    Then the JSON file should be indented

  # ============================================================================
  # Markdown 导出
  # ============================================================================
  
  Scenario: Export to Markdown
    Given entries exist:
      | title       | content     | tasks       |
      | Idea 1      | Content 1   | Task 1      |
      | Idea 2      | Content 2   | Task 2      |
    When I run "capture export -f markdown -o ./export.md"
    Then the command should succeed
    And the Markdown file should have:
      | element              |
      | Document title       |
      | Entry 1 as heading   |
      | Entry 1 content      |
      | Entry 1 tasks        |
      | Entry 2 as heading   |

  Scenario: Export TODO list to Markdown
    Given entries with tasks exist
    When I run "capture export -f markdown --tasks-only -o ./todos.md"
    Then the Markdown should be a TODO list
    And the TODO list should have checkboxes
    And the TODO list should be grouped by priority

  # ============================================================================
  # 过滤导出
  # ============================================================================
  
  Scenario: Export by category
    Given entries in categories:
      | category  | count |
      | features  | 5     |
      | bugs      | 3     |
    When I run "capture export -f csv -c features -o ./features.csv"
    Then the CSV should contain 5 rows
    And all rows should have category "features"

  Scenario: Export by tags
    Given entries with tags:
      | tags          | count |
      | ui            | 3     |
      | api           | 2     |
      | ui,important  | 1     |
    When I run "capture export -f csv --tags=ui -o ./ui-tagged.csv"
    Then the CSV should contain 4 rows

  Scenario: Export by date range
    Given entries created:
      | date       | count |
      | 2024-01-15 | 2     |
      | 2024-02-01 | 3     |
      | 2024-03-10 | 1     |
    When I run "capture export -f csv --since=2024-02-01 --until=2024-02-28 -o ./feb.csv"
    Then the CSV should contain 3 rows

  # ============================================================================
  # 组合过滤
  # ============================================================================
  
  Scenario: Export with multiple filters
    Given various entries exist
    When I run "capture export -f csv -c features --tags=ui --tasks-only -o ./filtered.csv"
    Then only entries matching all criteria should be exported

  # ============================================================================
  # 错误处理
  # ============================================================================
  
  Scenario: Export with unsupported format
    When I run "capture export -f xml -o ./export.xml"
    Then the command should fail
    And the error should contain "unsupported format"

  Scenario: Export without output path
    When I run "capture export -f csv"
    Then the command should fail
    And the error should contain "output path is required"

  Scenario: Export to invalid path
    When I run "capture export -f csv -o /invalid/path/export.csv"
    Then the command should fail
    And the error should contain "cannot write to path"

  # ============================================================================
  # 飞书导出（可选）
  # ============================================================================
  
  Scenario: Export to Feishu
    Given Feishu is configured
    When I run "capture export --to-feishu -c features"
    Then the command should succeed
    And the entries should be synced to Feishu table
