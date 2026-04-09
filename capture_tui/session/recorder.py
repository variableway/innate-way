"""会话记录器"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.session import SessionTurn
from .manager import SessionManager


class SessionRecorder:
    """会话记录器 - 用于 Skill 集成"""
    
    def __init__(self, manager: Optional[SessionManager] = None):
        self.manager = manager or SessionManager()
        self._metadata: Dict[str, Any] = {}
    
    def record_input(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """记录用户输入"""
        if not self.manager.is_active():
            # 自动开始会话
            self.manager.start_session(
                name=f"Auto Session {datetime.now().strftime('%H:%M:%S')}",
                goal="Auto captured session"
            )
        
        self._metadata['last_input'] = user_input
        self._metadata['input_context'] = context or {}
        
        return {
            "recorded": True,
            "session_id": self.manager.get_active_session().id,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_output(
        self,
        ai_response: str,
        thinking: Optional[str] = None,
        skills_used: Optional[List[str]] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[SessionTurn]:
        """记录 AI 输出"""
        if not self.manager.is_active():
            return None
        
        user_input = self._metadata.get('last_input', '')
        
        turn = self.manager.add_turn(
            user_input=user_input,
            ai_response=ai_response,
            thinking=thinking,
            skills_used=skills_used,
            model=model
        )
        
        # 合并元数据
        if metadata:
            turn.metadata.update(metadata)
        
        return turn
    
    def record_skill_usage(
        self,
        skill_name: str,
        skill_type: str,
        params: Optional[Dict] = None
    ):
        """记录技能使用"""
        if 'skills' not in self._metadata:
            self._metadata['skills'] = []
        
        self._metadata['skills'].append({
            "name": skill_name,
            "type": skill_type,
            "params": params or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def record_thinking(self, thinking: str):
        """记录思考过程"""
        self._metadata['thinking'] = thinking
    
    def end(self, summary: Optional[str] = None):
        """结束记录"""
        return self.manager.end_session(summary)
