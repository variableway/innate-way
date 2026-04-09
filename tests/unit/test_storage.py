"""存储层单元测试"""

import pytest
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path

from capture_tui.storage.file_store import FileStore
from capture_tui.storage.index_manager import IndexManager
from capture_tui.storage.entry_store import EntryStore
from capture_tui.models.entry import Entry


class TestFileStore:
    """文件存储测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_write_and_read(self, temp_dir):
        """测试写入和读取"""
        store = FileStore(temp_dir)
        
        store.write("test/file.txt", "Hello World")
        content = store.read("test/file.txt")
        
        assert content == "Hello World"
    
    def test_exists(self, temp_dir):
        """测试存在检查"""
        store = FileStore(temp_dir)
        
        assert not store.exists("nonexistent.txt")
        
        store.write("exists.txt", "content")
        assert store.exists("exists.txt")
    
    def test_list_dirs(self, temp_dir):
        """测试列出目录"""
        store = FileStore(temp_dir)
        
        store.write("dir1/file.txt", "")
        store.write("dir2/file.txt", "")
        
        dirs = store.list_dirs()
        
        assert "dir1" in dirs
        assert "dir2" in dirs
    
    def test_delete(self, temp_dir):
        """测试删除"""
        store = FileStore(temp_dir)
        
        store.write("to_delete.txt", "content")
        assert store.exists("to_delete.txt")
        
        store.delete("to_delete.txt")
        assert not store.exists("to_delete.txt")


class TestIndexManager:
    """索引管理器测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_add_and_get_entry(self, temp_dir):
        """测试添加和获取条目"""
        manager = IndexManager(temp_dir)
        
        entry = Entry.create(title="测试", content="内容", category="test")
        manager.add_entry(entry)
        
        result = manager.get_entry(entry.id)
        
        assert result is not None
        assert result["id"] == entry.id
        assert result["title"] == "测试"
    
    def test_list_entries(self, temp_dir):
        """测试列出入门"""
        manager = IndexManager(temp_dir)
        
        entry1 = Entry.create(title="条目1", content="内容", category="cat1")
        entry2 = Entry.create(title="条目2", content="内容", category="cat2")
        
        manager.add_entry(entry1)
        manager.add_entry(entry2)
        
        entries = manager.list_entries()
        
        assert len(entries) == 2
    
    def test_list_by_category(self, temp_dir):
        """测试按分类列出"""
        manager = IndexManager(temp_dir)
        
        entry1 = Entry.create(title="条目1", content="内容", category="cat1")
        entry2 = Entry.create(title="条目2", content="内容", category="cat2")
        
        manager.add_entry(entry1)
        manager.add_entry(entry2)
        
        entries = manager.list_entries(category="cat1")
        
        assert len(entries) == 1
        assert entries[0]["category"] == "cat1"
    
    def test_remove_entry(self, temp_dir):
        """测试删除条目"""
        manager = IndexManager(temp_dir)
        
        entry = Entry.create(title="测试", content="内容", category="test")
        manager.add_entry(entry)
        
        removed = manager.remove_entry(entry.id)
        
        assert removed is not None
        assert manager.get_entry(entry.id) is None
    
    def test_get_stats(self, temp_dir):
        """测试获取统计"""
        manager = IndexManager(temp_dir)
        
        entry = Entry.create(title="测试", content="内容", category="test")
        entry.tasks = ["任务1", "任务2"]
        manager.add_entry(entry)
        
        stats = manager.get_stats()
        
        assert stats["total_entries"] == 1
        assert stats["pending_tasks"] == 2


class TestEntryStore:
    """条目存储测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    def test_save_and_load(self, temp_dir):
        """测试保存和加载"""
        store = EntryStore(temp_dir)
        
        entry = Entry.create(title="测试", content="内容", category="test")
        path = store.save(entry)
        
        assert path.exists()
        
        loaded = store.load(str(path.relative_to(Path(temp_dir))))
        
        assert loaded.id == entry.id
        assert loaded.title == entry.title
    
    def test_get_path(self, temp_dir):
        """测试获取路径"""
        store = EntryStore(temp_dir)
        
        entry = Entry.create(title="测试标题", content="内容", category="features")
        path = store.get_path(entry)
        
        assert "features" in str(path)
        assert path.suffix == ".md"
    
    def test_list_by_category(self, temp_dir):
        """测试按分类列出"""
        store = EntryStore(temp_dir)
        
        entry1 = Entry.create(title="条目1", content="内容", category="test")
        entry2 = Entry.create(title="条目2", content="内容", category="test")
        
        store.save(entry1)
        store.save(entry2)
        
        entries = store.list_by_category("test")
        
        assert len(entries) == 2
    
    def test_slugify(self, temp_dir):
        """测试 slug 生成"""
        store = EntryStore(temp_dir)
        
        assert store._slugify("Hello World") == "hello-world"
        assert store._slugify("Test-Title_123") == "test-title_123"
        assert store._slugify("  Spaces  ") == "spaces"
