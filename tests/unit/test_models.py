"""数据模型单元测试"""

import pytest
from datetime import datetime
from capture_tui.models.entry import Entry, EntryMetadata
from capture_tui.models.category import Category
from capture_tui.models.session import Session, SessionTurn


class TestEntry:
    """Entry 模型测试"""
    
    def test_entry_creation(self):
        """测试条目创建"""
        entry = Entry.create(
            title="测试标题",
            content="测试内容",
            category="test",
            tags=["tag1", "tag2"]
        )
        
        assert entry.title == "测试标题"
        assert entry.content == "测试内容"
        assert entry.category == "test"
        assert entry.tags == ["tag1", "tag2"]
        assert entry.id.startswith("ideas-")
        assert isinstance(entry.created_at, datetime)
    
    def test_entry_to_dict(self):
        """测试转换为字典"""
        entry = Entry.create(
            title="测试",
            content="内容",
            category="test"
        )
        
        data = entry.to_dict()
        
        assert data["title"] == "测试"
        assert data["category"] == "test"
        assert "id" in data
        assert "created_at" in data
    
    def test_entry_from_dict(self):
        """测试从字典创建"""
        entry = Entry.create(title="测试", content="内容", category="test")
        data = entry.to_dict()
        
        restored = Entry.from_dict(data)
        
        assert restored.title == entry.title
        assert restored.id == entry.id
    
    def test_entry_to_markdown(self):
        """测试转换为 Markdown"""
        entry = Entry.create(
            title="测试标题",
            content="测试内容",
            category="features",
            tags=["ui"],
            tasks=["任务1", "任务2"]
        )
        
        md = entry.to_markdown()
        
        assert "# 测试标题" in md
        assert "测试内容" in md
        assert 'category: "features"' in md
        assert "- [ ] 任务1" in md
        assert "- [ ] 任务2" in md
    
    def test_entry_from_markdown(self):
        """测试从 Markdown 解析"""
        md = """---
id: "ideas-20240115-001"
category: "features"
created_at: "2024-01-15T10:30:00"
tags: ["ui", "improvement"]
priority: "P1"
source: "cli"
---

# 测试标题

这是内容。

## 关联任务

- [ ] 任务1
- [ ] 任务2
"""
        
        entry = Entry.from_markdown(md)
        
        assert entry.id == "ideas-20240115-001"
        assert entry.title == "测试标题"
        assert entry.category == "features"
        assert "ui" in entry.tags
        assert len(entry.tasks) == 2


class TestCategory:
    """Category 模型测试"""
    
    def test_category_creation(self):
        """测试分类创建"""
        cat = Category(
            name="features",
            display_name="功能特性",
            description="功能相关的想法"
        )
        
        assert cat.name == "features"
        assert cat.display_name == "功能特性"
        assert cat.count == 0
        assert isinstance(cat.created_at, datetime)
    
    def test_category_update_count(self):
        """测试更新计数"""
        cat = Category(name="test", display_name="Test")
        
        cat.update_count(1)
        assert cat.count == 1
        assert cat.last_entry is not None
        
        cat.update_count(-1)
        assert cat.count == 0
    
    def test_category_to_from_dict(self):
        """测试字典转换"""
        cat = Category(name="test", display_name="Test", count=5)
        
        data = cat.to_dict()
        restored = Category.from_dict(data)
        
        assert restored.name == cat.name
        assert restored.count == cat.count


class TestSession:
    """Session 模型测试"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = Session.create(name="测试会话", goal="测试目标")
        
        assert session.name == "测试会话"
        assert session.goal == "测试目标"
        assert session.id.startswith("sess-")
        assert len(session.turns) == 0
    
    def test_session_add_turn(self):
        """测试添加对话轮次"""
        session = Session.create(name="测试")
        
        turn = SessionTurn(
            turn_number=1,
            user_input="你好",
            ai_response="你好！",
            skills_used=["greeting"]
        )
        
        session.add_turn(turn)
        
        assert len(session.turns) == 1
        assert session.turns[0].user_input == "你好"
    
    def test_session_duration(self):
        """测试会话时长"""
        session = Session.create(name="测试")
        import time
        time.sleep(0.01)
        session.end()
        
        assert session.duration > 0
    
    def test_session_all_skills(self):
        """测试获取所有技能"""
        session = Session.create(name="测试")
        
        session.add_turn(SessionTurn(
            turn_number=1,
            user_input="测试1",
            ai_response="回复1",
            skills_used=["skill1", "skill2"]
        ))
        session.add_turn(SessionTurn(
            turn_number=2,
            user_input="测试2",
            ai_response="回复2",
            skills_used=["skill2", "skill3"]
        ))
        
        skills = session.all_skills
        
        assert "skill1" in skills
        assert "skill2" in skills
        assert "skill3" in skills
    
    def test_session_to_markdown(self):
        """测试转换为 Markdown"""
        session = Session.create(name="测试会话", goal="目标")
        session.add_turn(SessionTurn(
            turn_number=1,
            user_input="输入",
            ai_response="输出",
            thinking="思考过程",
            skills_used=["test"]
        ))
        session.end()
        
        md = session.to_markdown()
        
        assert "# 测试会话" in md
        assert "## 用户目标" in md
        assert "目标" in md
        assert "输入" in md
        assert "输出" in md
        assert "思考过程" in md
