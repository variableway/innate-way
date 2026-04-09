# Feature: Session Management
# 会话管理功能

Feature: Record and Manage Sessions
  As a user
  I want to record my interactions with AI assistants
  So that I can review the conversation and extract action items

  Background:
    Given an initialized project at "./ideas"

  # ============================================================================
  # 会话生命周期
  # ============================================================================
  
  Scenario: Start a new session
    When I run "capture session start -n 'Design Discussion'"
    Then the command should succeed
    And the output should contain "Session started"
    And the output should contain a session ID
    And a session file should be created

  Scenario: Start session with goal
    When I run "capture session start -n 'API Design' -g 'Design REST API for user management'"
    Then the command should succeed
    And the session should have goal "Design REST API for user management"

  Scenario: Start session with custom tool
    When I run "capture session start -n 'Code Review' --tool=claude-code"
    Then the command should succeed
    And the session should have tool "claude-code"

  Scenario: End a session
    Given an active session exists
    When I run "capture session end"
    Then the command should succeed
    And the output should contain "Session ended"
    And the session should have end time

  Scenario: End session with summary
    Given an active session exists
    When I run "capture session end -s 'Completed API design with 3 endpoints'"
    Then the session should have summary "Completed API design with 3 endpoints"

  Scenario: End session without active session
    Given no active session exists
    When I run "capture session end"
    Then the command should fail
    And the error should contain "No active session"

  # ============================================================================
  # 会话记录
  # ============================================================================
  
  Scenario: Record conversation turns
    Given an active session "S1"
    When a turn is recorded:
      | field        | value                        |
      | user_input   | How do I implement OAuth?    |
      | ai_response  | You can implement OAuth by...|
      | thinking     | User needs auth guidance     |
      | skills_used  | explain, code                |
    Then the session should have 1 turn
    And the turn should have turn_number 1

  Scenario: Record multiple turns
    Given an active session "S1"
    When 3 turns are recorded
    Then the session should have 3 turns
    And turns should have sequential numbers 1, 2, 3

  # ============================================================================
  # 列出会话
  # ============================================================================
  
  Scenario: List sessions when none exist
    When I run "capture session list"
    Then the command should succeed
    And the output should contain "No sessions found"

  Scenario: List sessions
    Given the following sessions exist:
      | name          | turns | duration |
      | Session A     | 5     | 300      |
      | Session B     | 3     | 180      |
    When I run "capture session list"
    Then the output should contain "Session A"
    And the output should contain "Session B"
    And the output should show turn counts

  Scenario: List sessions sorted by date
    Given sessions created on:
      | date       | name    |
      | 2024-01-15 | Older   |
      | 2024-01-20 | Newer   |
    When I run "capture session list"
    Then "Newer" should appear before "Older"

  # ============================================================================
  # 显示会话详情
  # ============================================================================
  
  Scenario: Show session details
    Given a session with ID "sess-abc123" exists
    And it has 3 turns
    When I run "capture session show --id=sess-abc123"
    Then the output should contain session ID
    And the output should contain turn count
    And the output should list all turns

  # ============================================================================
  # 导出会话
  # ============================================================================
  
  Scenario: Export session to Markdown
    Given a session "S1" with 2 turns exists
    When I run "capture session export --id=S1 --format=markdown -o ./session.md"
    Then the file "./session.md" should exist
    And the file should contain session name
    And the file should contain all turns
    And the file should contain user inputs
    And the file should contain AI responses

  Scenario: Export session to JSON
    Given a session "S1" exists
    When I run "capture session export --id=S1 --format=json -o ./session.json"
    Then the file "./session.json" should exist
    And the JSON should have session structure

  Scenario: Export with skill usage statistics
    Given a session with skills used:
      | skill    | count |
      | explore  | 3     |
      | plan     | 1     |
      | code     | 2     |
    When I run "capture session export --id=S1 -o ./session.md"
    Then the export should contain skill usage statistics

  # ============================================================================
  # 任务提取
  # ============================================================================
  
  Scenario: Extract tasks from session
    Given a session with turns:
      | user_input                 | ai_response                |
      | TODO: implement auth       | I'll help you implement... |
      | Task: write tests          | Let's write tests...       |
    When I run "capture session extract-tasks --id=S1"
    Then the output should contain extracted tasks
    And the tasks should be saved to session

  # ============================================================================
  # 删除会话
  # ============================================================================
  
  Scenario: Delete session
    Given a session "S1" exists
    When I run "capture session delete --id=S1"
    Then the command should succeed
    And the session file should be removed

  Scenario: Delete non-existent session
    When I run "capture session delete --id=non-existent"
    Then the command should fail
    And the error should contain "Session not found"

  # ============================================================================
  # 会话统计
  # ============================================================================
  
  Scenario: Generate session report
    Given multiple sessions exist
    When I run "capture session report"
    Then the output should contain:
      | metric               |
      | Total sessions       |
      | Total turns          |
      | Average duration     |
      | Top skills used      |
