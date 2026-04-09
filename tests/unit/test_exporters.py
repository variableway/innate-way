"""导出器单元测试"""

import pytest
import tempfile
import shutil
import json
import csv
from pathlib import Path

from capture_tui.exporters.csv_exporter import CSVExporter
from capture_tui.exporters.json_exporter import JSONExporter
from capture_tui.exporters.markdown_exporter import MarkdownExporter


class TestCSVExporter:
    """CSV 导出器测试"""
    
    @pytest.fixture
    def sample_entries(self):
        """示例条目"""
        return [
            {
                "id": "ideas-001",
                "title": "条目1",
                "category": "test",
                "tags": ["tag1", "tag2"],
                "created_at": "2024-01-15T10:30:00",
                "content": "内容1",
                "tasks": ["任务1"],
                "has_tasks": True,
                "metadata": {"priority": "P1"}
            },
            {
                "id": "ideas-002",
                "title": "条目2",
                "category": "test",
                "tags": ["tag3"],
                "created_at": "2024-01-15T11:00:00",
                "content": "内容2",
                "tasks": [],
                "has_tasks": False,
                "metadata": {"priority": "P2"}
            }
        ]
    
    def test_export_entries(self, sample_entries, tmp_path):
        """测试导出条目"""
        exporter = CSVExporter()
        output_path = str(tmp_path / "output.csv")
        
        result = exporter.export_entries(sample_entries, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
    
    def test_export_tasks_only(self, sample_entries, tmp_path):
        """测试仅导出任务"""
        exporter = CSVExporter()
        output_path = str(tmp_path / "tasks.csv")
        
        result = exporter.export_tasks(sample_entries, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # 应该有标题行 + 至少1个任务行
            assert len(rows) >= 1
    
    def test_to_string(self, sample_entries):
        """测试导出为字符串"""
        exporter = CSVExporter()
        
        result = exporter.to_string(sample_entries)
        
        assert "ideas-001" in result
        assert "条目1" in result


class TestJSONExporter:
    """JSON 导出器测试"""
    
    def test_export(self, tmp_path):
        """测试导出"""
        exporter = JSONExporter()
        data = {"key": "value", "list": [1, 2, 3]}
        output_path = str(tmp_path / "output.json")
        
        result = exporter.export(data, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r') as f:
            loaded = json.load(f)
            assert loaded["key"] == "value"
    
    def test_export_entries(self, tmp_path):
        """测试导出条目"""
        exporter = JSONExporter()
        entries = [{"id": "1", "title": "Test"}]
        output_path = str(tmp_path / "entries.json")
        
        result = exporter.export_entries(entries, output_path)
        
        assert Path(result).exists()
    
    def test_to_string(self):
        """测试转换为字符串"""
        exporter = JSONExporter()
        data = {"key": "value"}
        
        result = exporter.to_string(data)
        
        assert '"key": "value"' in result


class TestMarkdownExporter:
    """Markdown 导出器测试"""
    
    @pytest.fixture
    def sample_entries(self):
        """示例条目"""
        return [
            {
                "id": "ideas-001",
                "title": "条目1",
                "category": "test",
                "tags": ["tag1"],
                "created_at": "2024-01-15T10:30:00",
                "content": "内容1",
                "tasks": ["任务1"],
                "metadata": {"priority": "P1"}
            }
        ]
    
    def test_export_entries(self, sample_entries, tmp_path):
        """测试导出条目"""
        exporter = MarkdownExporter()
        output_path = str(tmp_path / "output.md")
        
        result = exporter.export_entries(sample_entries, output_path, title="测试文档")
        
        assert Path(result).exists()
        
        with open(result, 'r') as f:
            content = f.read()
            assert "# 测试文档" in content
            assert "## 条目1" in content
    
    def test_export_todo_list(self, sample_entries, tmp_path):
        """测试导出待办列表"""
        exporter = MarkdownExporter()
        output_path = str(tmp_path / "todos.md")
        
        result = exporter.export_todo_list(sample_entries, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r') as f:
            content = f.read()
            assert "# 待办任务列表" in content
            assert "- [ ]" in content
