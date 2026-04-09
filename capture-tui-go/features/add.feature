# Feature: Add Entry
# 添加条目功能

Feature: Add Entry to Capture
  As a user
  I want to add ideas and tasks to my capture system
  So that I can track and manage them

  Background:
    Given an initialized project at "./ideas"

  # ============================================================================
  # 基本添加
  # ============================================================================
  
  Scenario: Add simple text entry
    When I run "capture add 'This is a test idea'"
    Then the command should succeed
    And the output should contain "Entry created"
    And the output should contain an entry ID
    And a new entry file should be created in "./ideas/uncategorized/"
    And the entry file should contain "This is a test idea"

  Scenario: Add entry with category
    When I run "capture add 'Dashboard improvement' --category=features"
    Then the command should succeed
    And a new entry file should be created in "./ideas/features/"
    And the entry should have category "features"

  Scenario: Add entry with tags
    When I run "capture add 'New feature' --category=features --tags=ui,important"
    Then the command should succeed
    And the entry should have tags ["ui", "important"]

  Scenario: Add entry with priority
    When I run "capture add 'Urgent bug fix' --category=bugs -p P0"
    Then the command should succeed
    And the entry should have priority "P0"

  # ============================================================================
  # 标签和优先级识别
  # ============================================================================
  
  Scenario: Auto-extract tags from content
    When I run "capture add 'Implement #dashboard feature with #performance improvements'"
    Then the command should succeed
    And the entry should have tags ["dashboard", "performance"]

  Scenario: Auto-extract priority from content
    When I run "capture add 'Fix critical bug P0'"
    Then the command should succeed
    And the entry should have priority "P0"

  Scenario: Auto-extract tasks from content
    When I run "capture add 'Project plan:
      
      - [ ] Task one
      - [ ] Task two'"
    Then the command should succeed
    And the entry should have 2 tasks
    And the tasks should be ["Task one", "Task two"]

  # ============================================================================
  # 从文件添加
  # ============================================================================
  
  Scenario: Add entry from file
    Given a file "./test-idea.md" with content:
      """
      # My Great Idea
      
      This is a detailed description.
      
      - [ ] Implement feature
      - [ ] Write tests
      """
    When I run "capture add --file=./test-idea.md --category=backlog"
    Then the command should succeed
    And the entry title should be "My Great Idea"
    And the entry should have 2 tasks

  Scenario: Add entry from markdown file with frontmatter
    Given a file "./with-frontmatter.md" with content:
      """
      ---
      title: Custom Title
      tags: ["tag1", "tag2"]
      priority: P1
      ---
      
      # Original Title
      
      Content here.
      """
    When I run "capture add --file=./with-frontmatter.md"
    Then the command should succeed
    And the entry title should be "Custom Title"
    And the entry should have tags ["tag1", "tag2"]
    And the entry should have priority "P1"

  # ============================================================================
  # 交互式输入
  # ============================================================================
  
  Scenario: Interactive mode
    When I run "capture add --interactive" and type:
      """
      My interactive idea
      
      This is the content.
      
      - [ ] Task 1
      ^D
      """
    Then the command should succeed
    And an entry should be created with title "My interactive idea"

  # ============================================================================
  # 分类管理
  # ============================================================================
  
  Scenario: Auto-create category when enabled
    Given the config has "storage.auto_create_category" set to "true"
    When I run "capture add 'New idea' --category=new-category"
    Then the command should succeed
    And the directory "./ideas/new-category" should be created

  Scenario: Fail when category limit reached
    Given 10 categories already exist
    When I run "capture add 'New idea' --category=eleventh-category"
    Then the command should fail
    And the error should contain "Maximum 10 categories allowed"
    And the error code should be "CATEGORY_LIMIT_EXCEEDED"

  Scenario: Use default category when not specified
    Given the config has "input.default_category" set to "inbox"
    When I run "capture add 'No category specified'"
    Then the command should succeed
    And the entry should be created in "./ideas/inbox/"

  # ============================================================================
  # 错误处理
  # ============================================================================
  
  Scenario: Add with non-existent file
    When I run "capture add --file=./non-existent.md"
    Then the command should fail
    And the error should contain "file not found"

  Scenario: Add with invalid priority
    When I run "capture add 'Test' --priority=P5"
    Then the command should fail
    And the error should contain "invalid priority"
    And the error should contain "valid values: P0, P1, P2"

  Scenario: Add empty content
    When I run "capture add ''"
    Then the command should fail
    And the error should contain "content cannot be empty"

  # ============================================================================
  # 存储格式
  # ============================================================================
  
  Scenario: Entry file structure
    When I run "capture add 'Test idea' --category=test -t tag1 -p P1"
    Then the created entry file should have:
      | field        | value          |
      | frontmatter  | present        |
      | id           | non-empty      |
      | category     | test           |
      | priority     | P1             |
      | tags         | [tag1]         |
      | title        | Test idea      |
      | content      | Test idea      |
