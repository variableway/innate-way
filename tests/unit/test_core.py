"""核心功能单元测试"""

import pytest
import tempfile
import shutil
from pathlib import Path

from capture_tui.core.client import CaptureClient
from capture_tui.core.category_manager import CategoryManager
from capture_tui.config import Config


class TestCaptureClient:
    """核心客户端测试"""
    
    @pytest.fixture
    def temp_client(self):
        """临时客户端"""
        temp_dir = tempfile.mkdtemp()
        config = Config()
        config.storage.root_dir = temp_dir
        client = CaptureClient(config)
        yield client
        shutil.rmtree(temp_dir)
    
    def test_add_idea(self, temp_client):
        """测试添加想法"""
        entry = temp_client.add_idea(
            content="测试想法",
            category="test",
            tags=["tag1"]
        )
        
        assert entry.title == "测试想法"
        assert entry.category == "test"
        assert "tag1" in entry.tags
    
    def test_add_idea_with_tasks(self, temp_client):
        """测试添加带任务的 idea"""
        entry = temp_client.add_idea(
            content="这是一个想法\n\n- [ ] 任务1\n- [ ] 任务2",
            category="test"
        )
        
        assert len(entry.tasks) >= 1
    
    def test_get_entry(self, temp_client):
        """测试获取条目"""
        entry = temp_client.add_idea("测试", category="test")
        
        result = temp_client.get_entry(entry.id)
        
        assert result is not None
        assert result.id == entry.id
    
    def test_list_entries(self, temp_client):
        """测试列出入门"""
        temp_client.add_idea("想法1", category="test")
        temp_client.add_idea("想法2", category="test")
        
        entries = temp_client.list_entries(category="test")
        
        assert len(entries) == 2
    
    def test_delete_entry(self, temp_client):
        """测试删除条目"""
        entry = temp_client.add_idea("待删除", category="test")
        
        success = temp_client.delete_entry(entry.id)
        
        assert success is True
        assert temp_client.get_entry(entry.id) is None
    
    def test_create_category(self, temp_client):
        """测试创建分类"""
        category = temp_client.create_category(
            name="new-cat",
            display_name="新分类"
        )
        
        assert category.name == "new-cat"
        assert category.display_name == "新分类"
    
    def test_category_limit(self, temp_client):
        """测试分类数量限制"""
        # 创建10个分类（达到上限）
        for i in range(10):
            temp_client.create_category(f"cat{i}")
        
        # 第11个应该失败
        with pytest.raises(ValueError, match="Maximum"):
            temp_client.create_category("cat10")
    
    def test_analyze_category(self, temp_client):
        """测试分析分类"""
        temp_client.add_idea("想法1", category="test", tags=["tag1"])
        temp_client.add_idea("想法2", category="test", tags=["tag2"])
        
        report = temp_client.analyze_category("test")
        
        assert report["category"] == "test"
        assert report["statistics"]["total_entries"] == 2


class TestCategoryManager:
    """分类管理器测试"""
    
    @pytest.fixture
    def temp_manager(self):
        """临时管理器"""
        temp_dir = tempfile.mkdtemp()
        manager = CategoryManager(temp_dir)
        yield manager
        shutil.rmtree(temp_dir)
    
    def test_create_and_get(self, temp_manager):
        """测试创建和获取"""
        cat = temp_manager.create("test", "测试")
        
        assert cat.name == "test"
        
        result = temp_manager.get("test")
        assert result is not None
        assert result.name == "test"
    
    def test_create_duplicate(self, temp_manager):
        """测试重复创建"""
        temp_manager.create("test")
        
        with pytest.raises(ValueError, match="already exists"):
            temp_manager.create("test")
    
    def test_list_all(self, temp_manager):
        """测试列出所有"""
        temp_manager.create("cat1")
        temp_manager.create("cat2")
        
        cats = temp_manager.list_all()
        
        assert len(cats) == 2
    
    def test_can_create(self, temp_manager):
        """测试能否创建"""
        assert temp_manager.can_create() is True
        
        # 创建10个分类
        for i in range(10):
            temp_manager.create(f"cat{i}")
        
        assert temp_manager.can_create() is False
    
    def test_get_count(self, temp_manager):
        """测试获取计数"""
        assert temp_manager.get_count() == 0
        
        temp_manager.create("cat1")
        assert temp_manager.get_count() == 1
