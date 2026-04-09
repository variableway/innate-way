"""会话模块单元测试"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path

from capture_tui.session.manager import SessionManager
from capture_tui.session.recorder import SessionRecorder
from capture_tui.session.exporter import SessionExporter
from capture_tui.models.session import Session, SessionTurn


class TestSessionManager:
    """会话管理器测试"""
    
    @pytest.fixture
    def temp_manager(self):
        """临时管理器"""
        temp_dir = tempfile.mkdtemp()
        manager = SessionManager(temp_dir)
        yield manager
        shutil.rmtree(temp_dir)
    
    def test_start_and_end_session(self, temp_manager):
        """测试开始和结束会话"""
        session = temp_manager.start_session(name="测试", goal="目标")
        
        assert session.name == "测试"
        assert session.goal == "目标"
        assert temp_manager.is_active() is True
        
        ended = temp_manager.end_session("总结")
        
        assert ended is not None
        assert ended.summary == "总结"
        assert temp_manager.is_active() is False
    
    def test_add_turn(self, temp_manager):
        """测试添加对话轮次"""
        temp_manager.start_session(name="测试")
        
        turn = temp_manager.add_turn(
            user_input="你好",
            ai_response="你好！",
            skills_used=["greeting"]
        )
        
        assert turn is not None
        assert turn.user_input == "你好"
        assert "greeting" in turn.skills_used
    
    def test_no_active_session(self, temp_manager):
        """测试无活动会话"""
        turn = temp_manager.add_turn("输入", "输出")
        
        assert turn is None
    
    def test_list_sessions(self, temp_manager):
        """测试列出会话"""
        # 创建并结束一个会话
        temp_manager.start_session(name="测试1")
        temp_manager.add_turn("输入", "输出")
        temp_manager.end_session()
        
        sessions = temp_manager.list_sessions()
        
        assert len(sessions) == 1
        assert sessions[0]["name"] == "测试1"
    
    def test_load_session(self, temp_manager):
        """测试加载会话"""
        session = temp_manager.start_session(name="测试")
        session_id = session.id
        temp_manager.end_session()
        
        loaded = temp_manager.load_session(session_id)
        
        assert loaded is not None
        assert loaded.name == "测试"
    
    def test_extract_tasks(self, temp_manager):
        """测试提取任务"""
        temp_manager.start_session(name="测试")
        temp_manager.add_turn(
            user_input="TODO: 完成任务",
            ai_response="好的"
        )
        temp_manager.end_session()
        
        # 获取最后一个会话的 ID
        sessions = temp_manager.list_sessions()
        session_id = sessions[0]["id"]
        
        tasks = temp_manager.extract_tasks(session_id)
        
        # 应该提取到任务
        assert len(tasks) > 0


class TestSessionRecorder:
    """会话记录器测试"""
    
    @pytest.fixture
    def temp_recorder(self):
        """临时记录器"""
        temp_dir = tempfile.mkdtemp()
        manager = SessionManager(temp_dir)
        recorder = SessionRecorder(manager)
        yield recorder
        shutil.rmtree(temp_dir)
    
    def test_record_input(self, temp_recorder):
        """测试记录输入"""
        result = temp_recorder.record_input("测试输入")
        
        assert result["recorded"] is True
        assert "session_id" in result
    
    def test_record_output(self, temp_recorder):
        """测试记录输出"""
        temp_recorder.record_input("输入")
        turn = temp_recorder.record_output(
            ai_response="输出",
            thinking="思考",
            skills_used=["test"]
        )
        
        assert turn is not None
        assert turn.ai_response == "输出"
        assert turn.thinking == "思考"
    
    def test_record_skill_usage(self, temp_recorder):
        """测试记录技能使用"""
        temp_recorder.record_skill_usage("explore", "agent", {"path": "/test"})
        
        assert "skills" in temp_recorder._metadata
        assert len(temp_recorder._metadata["skills"]) == 1


class TestSessionExporter:
    """会话导出器测试"""
    
    @pytest.fixture
    def sample_session(self):
        """示例会话"""
        session = Session.create(name="测试会话", goal="目标")
        session.add_turn(SessionTurn(
            turn_number=1,
            user_input="输入",
            ai_response="输出",
            skills_used=["test"]
        ))
        session.end()
        return session
    
    def test_export_markdown(self, sample_session, tmp_path):
        """测试导出 Markdown"""
        exporter = SessionExporter()
        output_path = str(tmp_path / "session.md")
        
        result = exporter.export_markdown(sample_session, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r') as f:
            content = f.read()
            assert "# 测试会话" in content
    
    def test_export_json(self, sample_session, tmp_path):
        """测试导出 JSON"""
        exporter = SessionExporter()
        output_path = str(tmp_path / "session.json")
        
        result = exporter.export_json(sample_session, output_path)
        
        assert Path(result).exists()
        
        with open(result, 'r') as f:
            data = json.load(f)
            assert data["name"] == "测试会话"
    
    def test_generate_report(self, sample_session):
        """测试生成报告"""
        exporter = SessionExporter()
        
        report = exporter.generate_report([sample_session])
        
        assert report["total_sessions"] == 1
        assert report["total_turns"] == 1
