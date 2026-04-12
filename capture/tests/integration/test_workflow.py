"""工作流集成测试"""

import pytest
import tempfile
import shutil
from pathlib import Path

from capture_tui.core.client import CaptureClient
from capture_tui.config import Config
from capture_tui.session.manager import SessionManager


class TestCompleteWorkflow:
    """完整工作流测试"""
    
    @pytest.fixture
    def temp_project(self):
        """临时项目"""
        temp_dir = tempfile.mkdtemp()
        config = Config()
        config.storage.root_dir = temp_dir
        client = CaptureClient(config)
        client.init_project(temp_dir)
        yield client, temp_dir
        shutil.rmtree(temp_dir)
    
    def test_add_and_retrieve(self, temp_project):
        """测试添加和检索"""
        client, _ = temp_project
        
        # 添加想法
        entry = client.add_idea(
            content="这是一个测试想法\n\n包含一些任务:\n- [ ] 任务1\n- [ ] 任务2",
            category="features",
            tags=["test", "important"]
        )
        
        # 检索
        retrieved = client.get_entry(entry.id)
        
        assert retrieved is not None
        assert retrieved.title == "这是一个测试想法"
        assert len(retrieved.tasks) >= 1
    
    def test_category_workflow(self, temp_project):
        """测试分类工作流"""
        client, _ = temp_project
        
        # 创建分类
        client.create_category("bugs", "缺陷")
        client.create_category("features", "功能")
        
        # 添加到不同分类
        client.add_idea("Bug 1", category="bugs")
        client.add_idea("Feature 1", category="features")
        
        # 列出分类
        categories = client.list_categories()
        
        assert len(categories) >= 2
        
        # 按分类列出
        bug_entries = client.list_entries(category="bugs")
        assert len(bug_entries) == 1
    
    def test_export_workflow(self, temp_project, tmp_path):
        """测试导出工作流"""
        client, _ = temp_project
        
        # 添加数据
        client.add_idea("想法1", category="test", tags=["tag1"])
        client.add_idea("想法2", category="test", tags=["tag2"])
        
        # 导出 CSV
        from capture_tui.exporters.csv_exporter import CSVExporter
        entries = client.list_entries()
        
        exporter = CSVExporter()
        output_path = str(tmp_path / "export.csv")
        exporter.export_entries(entries, output_path)
        
        assert Path(output_path).exists()
    
    def test_session_workflow(self, temp_project):
        """测试会话工作流"""
        client, temp_dir = temp_project
        
        # 创建会话管理器
        manager = SessionManager(f"{temp_dir}/sessions")
        
        # 开始会话
        session = manager.start_session(name="测试会话", goal="测试目标")
        
        # 添加对话
        manager.add_turn(
            user_input="请帮我设计API",
            ai_response="好的，建议使用RESTful风格",
            skills_used=["design"]
        )
        
        # 结束会话
        manager.end_session("完成了API设计")
        
        # 验证会话已保存
        sessions = manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["name"] == "测试会话"


class TestAnalysisWorkflow:
    """分析工作流测试"""
    
    @pytest.fixture
    def temp_project(self):
        """临时项目"""
        temp_dir = tempfile.mkdtemp()
        config = Config()
        config.storage.root_dir = temp_dir
        client = CaptureClient(config)
        client.init_project(temp_dir)
        yield client, temp_dir
        shutil.rmtree(temp_dir)
    
    def test_analyze_category(self, temp_project):
        """测试分析分类"""
        client, temp_dir = temp_project
        
        # 添加多个想法
        client.add_idea(
            "Dashboard优化\n\n- [ ] 优化加载速度\n- [ ] 改进UI设计",
            category="features",
            tags=["ui", "performance"],
            priority="P1"
        )
        client.add_idea(
            "添加导出功能\n\n- [ ] 支持CSV导出\n- [ ] 支持JSON导出",
            category="features",
            tags=["export", "feature"],
            priority="P2"
        )
        
        # 分析
        from capture_tui.ai.analyzer import CategoryAnalyzer
        analyzer = CategoryAnalyzer(temp_dir)
        
        report = analyzer.analyze("features")
        
        assert report["statistics"]["total_entries"] == 2
        assert report["statistics"]["total_tasks"] == 4
        assert len(report["themes"]) > 0
