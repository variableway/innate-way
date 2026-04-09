"""Session 数据模型"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


@dataclass
class SessionTurn:
    """对话轮次"""
    turn_number: int
    user_input: str
    ai_response: str
    thinking: Optional[str] = None
    skills_used: List[str] = field(default_factory=list)
    model: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "turn_number": self.turn_number,
            "user_input": self.user_input,
            "ai_response": self.ai_response,
            "thinking": self.thinking,
            "skills_used": self.skills_used,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionTurn":
        return cls(
            turn_number=data["turn_number"],
            user_input=data["user_input"],
            ai_response=data["ai_response"],
            thinking=data.get("thinking"),
            skills_used=data.get("skills_used", []),
            model=data.get("model"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class Session:
    """会话记录"""
    id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    turns: List[SessionTurn] = field(default_factory=list)
    goal: Optional[str] = None
    tool: str = "kimi-cli"
    summary: Optional[str] = None
    extracted_tasks: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, name: str, goal: Optional[str] = None) -> "Session":
        """创建新会话"""
        session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        return cls(
            id=session_id,
            name=name,
            start_time=datetime.now(),
            goal=goal,
            tool="kimi-cli"
        )
    
    def add_turn(self, turn: SessionTurn):
        """添加对话轮次"""
        self.turns.append(turn)
    
    def end(self):
        """结束会话"""
        self.end_time = datetime.now()
    
    @property
    def duration(self) -> float:
        """会话持续时间（秒）"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def all_skills(self) -> List[str]:
        """获取所有使用的技能"""
        skills = set()
        for turn in self.turns:
            skills.update(turn.skills_used)
        return list(skills)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "turns": [t.to_dict() for t in self.turns],
            "goal": self.goal,
            "tool": self.tool,
            "summary": self.summary,
            "extracted_tasks": self.extracted_tasks
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(
            id=data["id"],
            name=data["name"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            turns=[SessionTurn.from_dict(t) for t in data.get("turns", [])],
            goal=data.get("goal"),
            tool=data.get("tool", "kimi-cli"),
            summary=data.get("summary"),
            extracted_tasks=data.get("extracted_tasks", [])
        )
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        lines = [
            "---",
            f'session_id: "{self.id}"',
            f'name: "{self.name}"',
            f'start_time: "{self.start_time.isoformat()}"',
            f'end_time: "{self.end_time.isoformat() if self.end_time else ""}"',
            f'tool: "{self.tool}"',
            f'skills_used: {self.all_skills}',
            "---",
            "",
            f"# {self.name}",
            "",
        ]
        
        if self.goal:
            lines.extend([
                "## 用户目标",
                "",
                self.goal,
                "",
            ])
        
        lines.extend([
            "## 对话过程",
            "",
        ])
        
        for turn in self.turns:
            lines.extend([
                f"### Turn {turn.turn_number}",
                "",
                f"**时间**: {turn.timestamp.strftime('%H:%M:%S')}",
                "",
                f"**用户**: {turn.user_input}",
                "",
                f"**AI**: {turn.ai_response}",
                "",
            ])
            if turn.thinking:
                lines.extend([
                    f"**思考过程**: {turn.thinking}",
                    "",
                ])
            if turn.skills_used:
                lines.extend([
                    f"**使用技能**: {', '.join(turn.skills_used)}",
                    "",
                ])
            lines.append("")
        
        if self.all_skills:
            lines.extend([
                "## 技能使用分析",
                "",
                "| 技能 | 使用次数 |",
                "|------|---------|",
            ])
            from collections import Counter
            skill_counts = Counter()
            for turn in self.turns:
                skill_counts.update(turn.skills_used)
            for skill, count in skill_counts.most_common():
                lines.append(f"| {skill} | {count} |")
            lines.append("")
        
        if self.extracted_tasks:
            lines.extend([
                "## 提取的行动项",
                "",
            ])
            for task in self.extracted_tasks:
                lines.append(f"- [ ] {task}")
            lines.append("")
        
        return "\n".join(lines)
