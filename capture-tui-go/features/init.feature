# Feature: Initialize Project
# 项目初始化功能

Feature: Initialize Capture TUI Project
  As a user
  I want to initialize a new Capture TUI project
  So that I can start capturing and managing my ideas

  Background:
    Given the capture CLI is installed

  # ============================================================================
  # 基本初始化
  # ============================================================================
  
  Scenario: Initialize project with default settings
    When I run "capture init"
    Then the command should succeed
    And the directory "./ideas" should be created
    And the directory "./ideas/.capture" should be created
    And the directory "./ideas/.capture/templates" should be created
    And the file "./ideas/.capture/config.yaml" should exist
    And the file "./ideas/.capture/index.json" should exist
    And the default config should contain:
      | key              | value           |
      | version          | 1.0             |
      | storage.root_dir | ./ideas         |
      | input.default_category | uncategorized |

  Scenario: Initialize project with custom root directory
    When I run "capture init --root-dir=./my-ideas"
    Then the command should succeed
    And the directory "./my-ideas" should be created
    And the config should have "storage.root_dir" set to "./my-ideas"

  Scenario: Initialize project with short flag
    When I run "capture init -r ./custom-ideas"
    Then the command should succeed
    And the directory "./custom-ideas" should be created

  # ============================================================================
  # 重新初始化
  # ============================================================================
  
  Scenario: Re-initialize existing project with force flag
    Given an initialized project at "./ideas"
    When I run "capture init --root-dir=./ideas --force"
    Then the command should succeed
    And the existing config should be overwritten

  Scenario: Re-initialize without force flag should warn
    Given an initialized project at "./ideas"
    When I run "capture init --root-dir=./ideas"
    Then the command should prompt for confirmation
    And ask "Project already exists. Overwrite?"

  # ============================================================================
  # 错误处理
  # ============================================================================
  
  Scenario: Initialize with invalid root directory
    When I run "capture init --root-dir=/invalid/path/that/cannot/be/created"
    Then the command should fail
    And the error message should contain "cannot create directory"

  Scenario: Initialize with permission denied
    Given a read-only parent directory
    When I run "capture init --root-dir=./readonly/ideas"
    Then the command should fail
    And the error code should be "PERMISSION_DENIED"

  # ============================================================================
  # 配置验证
  # ============================================================================
  
  Scenario: Default config structure
    When I run "capture init"
    Then the config file should have the following sections:
      | section |
      | storage |
      | input   |
      | ai      |
      | export  |
      | session |

  Scenario: Template files creation
    When I run "capture init"
    Then the following template files should exist:
      | path                                  |
      | ./ideas/.capture/templates/idea.md.tpl |
      | ./ideas/.capture/templates/session.md.tpl |
