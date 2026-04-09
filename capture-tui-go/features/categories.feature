# Feature: Category Management
# 分类管理功能

Feature: Manage Categories
  As a user
  I want to organize my entries into categories
  So that I can better manage and find them

  Background:
    Given an initialized project at "./ideas"

  # ============================================================================
  # 列出分类
  # ============================================================================
  
  Scenario: List categories when none exist
    When I run "capture categories list"
    Then the command should succeed
    And the output should contain "No categories found"

  Scenario: List categories with entries
    Given the following entries exist:
      | category  | title      |
      | features  | Feature 1  |
      | features  | Feature 2  |
      | bugs      | Bug 1      |
    When I run "capture categories list"
    Then the command should succeed
    And the output should contain "features"
    And the output should contain "bugs"
    And the output should show "features" has 2 entries
    And the output should show "bugs" has 1 entry

  Scenario: List categories with details
    Given category "features" was created on "2024-01-01"
    And category "features" has 5 entries
    When I run "capture categories list"
    Then the output should show:
      | field        | value        |
      | Name         | features     |
      | Count        | 5            |
      | Last Entry   | recent date  |

  # ============================================================================
  # 创建分类
  # ============================================================================
  
  Scenario: Create new category
    When I run "capture categories create my-category"
    Then the command should succeed
    And the directory "./ideas/my-category" should be created
    And the output should contain "Category created: my-category"

  Scenario: Create category with display name
    When I run "capture categories create bugs --display-name='Bug Tracking'"
    Then the command should succeed
    And the category "bugs" should have display name "Bug Tracking"

  Scenario: Create category with description
    When I run "capture categories create features --description='New feature ideas and improvements'"
    Then the command should succeed
    And the category "features" should have description "New feature ideas and improvements"

  Scenario: Create category with all options
    When I run "capture categories create archive --display-name='Archive' --description='Archived items'"
    Then the command should succeed
    And the category should have:
      | field        | value            |
      | name         | archive          |
      | display_name | Archive          |
      | description  | Archived items   |

  # ============================================================================
  # 分类限制
  # ============================================================================
  
  Scenario: Cannot create more than 10 categories
    Given 10 categories already exist
    When I run "capture categories create eleventh"
    Then the command should fail
    And the error should contain "Maximum 10 categories allowed"
    And the error code should be "CATEGORY_LIMIT_EXCEEDED"

  Scenario: Cannot create duplicate category
    Given category "features" exists
    When I run "capture categories create features"
    Then the command should fail
    And the error should contain "Category already exists"

  # ============================================================================
  # 显示分类详情
  # ============================================================================
  
  Scenario: Show category details
    Given category "features" exists with 3 entries
    When I run "capture categories show features"
    Then the command should succeed
    And the output should contain "Category: features"
    And the output should contain "Entry count: 3"

  Scenario: Show category with recent entries
    Given the following entries exist in category "features":
      | title      | created_at |
      | Recent 1   | today      |
      | Recent 2   | yesterday  |
      | Old 1      | last week  |
    When I run "capture categories show features"
    Then the output should contain "Recent entries"
    And the output should list "Recent 1" and "Recent 2"

  Scenario: Show non-existent category
    When I run "capture categories show non-existent"
    Then the command should fail
    And the error should contain "Category not found"

  # ============================================================================
  # 删除分类
  # ============================================================================
  
  Scenario: Delete empty category
    Given an empty category "temp"
    When I run "capture categories delete temp"
    Then the command should succeed
    And the directory "./ideas/temp" should not exist
    And the category should be removed from index

  Scenario: Cannot delete category with entries without force
    Given category "features" has 3 entries
    When I run "capture categories delete features"
    Then the command should prompt for confirmation
    And warn "Category contains 3 entries"

  Scenario: Delete category with entries using force
    Given category "features" has 3 entries
    When I run "capture categories delete features --force"
    Then the command should succeed
    And the directory "./ideas/features" should not exist
    And the entries should be removed

  # ============================================================================
  # 分类重命名（可选）
  # ============================================================================
  
  Scenario: Rename category
    Given category "old-name" exists
    When I run "capture categories rename old-name new-name"
    Then the command should succeed
    And the directory should be renamed to "./ideas/new-name"
    And all entries should have category "new-name"
