"""会话管理器"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from ..models.session import Session, SessionTurn


class SessionManager:
    """会话管理器"""
    
    def __init__(self, capture_dir: str = "./docs/capture-tui/sessions"):
        self.capture_dir = Path(capture_dir)
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self._active_session: Optional[Session] = None
    
    def start_session(
        self,
        name: str,
        goal: Optional[str] = None,
        tool: str = "kimi-cli"
    ) -> Session:
        """开始新会话"""
        self._active_session = Session.create(name=name, goal=goal)
        self._active_session.tool = tool
        return self._active_session
    
    def end_session(self, summary: Optional[str] = None) -> Optional[Session]:
        """结束当前会话"""
        if not self._active_session:
            return None
        
        self._active_session.end()
        if summary:
            self._active_session.summary = summary
        
        # 保存会话
        self._save_session(self._active_session)
        
        session = self._active_session
        self._active_session = None
        return session
    
    def add_turn(
        self,
        user_input: str,
        ai_response: str,
        thinking: Optional[str] = None,
        skills_used: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> Optional[SessionTurn]:
        """添加对话轮次"""
        if not self._active_session:
            return None
        
        turn = SessionTurn(
            turn_number=len(self._active_session.turns) + 1,
            user_input=user_input,
            ai_response=ai_response,
            thinking=thinking,
            skills_used=skills_used or [],
            model=model
        )
        
        self._active_session.add_turn(turn)
        return turn
    
    def get_active_session(self) -> Optional[Session]:
        """获取当前活动会话"""
        return self._active_session
    
    def is_active(self) -> bool:
        """检查是否有活动会话"""
        return self._active_session is not None
    
    def list_sessions(self) -> List[Dict]:
        """列出所有会话"""
        sessions = []
        
        for session_file in self.capture_dir.rglob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get('id'),
                        "name": data.get('name'),
                        "start_time": data.get('start_time'),
                        "end_time": data.get('end_time'),
                        "turn_count": len(data.get('turns', [])),
                        "path": str(session_file.relative_to(self.capture_dir))
                    })
            except Exception:
                pass
        
        # 按时间倒序
        sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return sessions
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """加载会话"""
        # 搜索会话文件
        for session_file in self.capture_dir.rglob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('id') == session_id:
                        return Session.from_dict(data)
            except Exception:
                pass
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        for session_file in self.capture_dir.rglob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('id') == session_id:
                        session_file.unlink()
                        return True
            except Exception:
                pass
        
        return False
    
    def _save_session(self, session: Session):
        """保存会话到文件"""
        # 按日期组织目录
        date_dir = self.capture_dir / session.start_time.strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为 JSON
        json_path = date_dir / f"{session.id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        # 同时保存为 Markdown
        md_path = date_dir / f"{session.id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(session.to_markdown())
    
    def extract_tasks(self, session_id: str) -> List[str]:
        """从会话中提取任务"""
        session = self.load_session(session_id)
        if not session:
            return []
        
        # 简单的任务提取
        tasks = []
        for turn in session.turns:
            # 从用户输入和 AI 回复中提取 TODO
            import re
            for text in [turn.user_input, turn.ai_response]:
                matches = re.findall(r'(?:TODO|任务|需要|应该)\s*[:：]\s*(.+)', text, re.IGNORECASE)
                tasks.extend(matches)
        
        return list(set(tasks))
