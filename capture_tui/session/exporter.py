"""会话导出器"""

import json
from pathlib import Path
from typing import Optional, List, Dict
from collections import Counter

from ..models.session import Session


class SessionExporter:
    """会话导出器"""
    
    def export_markdown(self, session: Session, output_path: str) -> str:
        """导出为 Markdown"""
        content = session.to_markdown()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def export_json(self, session: Session, output_path: str) -> str:
        """导出为 JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_summary(self, session: Session, output_path: str) -> str:
        """导出摘要"""
        # 统计信息
        skill_counts = Counter()
        for turn in session.turns:
            skill_counts.update(turn.skills_used)
        
        lines = [
            f"# 会话摘要: {session.name}",
            "",
            f"**会话 ID**: {session.id}",
            f"**开始时间**: {session.start_time}",
            f"**结束时间**: {session.end_time or '进行中'}",
            f"**持续时间**: {self._format_duration(session.duration)}",
            f"**对话轮次**: {len(session.turns)}",
            "",
            "## 技能使用统计",
            "",
        ]
        
        for skill, count in skill_counts.most_common():
            lines.append(f"- {skill}: {count} 次")
        
        lines.extend([
            "",
            "## 提取的任务",
            "",
        ])
        
        for task in session.extracted_tasks:
            lines.append(f"- [ ] {task}")
        
        if session.summary:
            lines.extend([
                "",
                "## 会话总结",
                "",
                session.summary
            ])
        
        content = '\n'.join(lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def generate_report(self, sessions: List[Session]) -> Dict:
        """生成批量报告"""
        total_turns = sum(len(s.turns) for s in sessions)
        total_duration = sum(s.duration for s in sessions if s.end_time)
        
        # 统计技能使用
        all_skills = Counter()
        for session in sessions:
            for turn in session.turns:
                all_skills.update(turn.skills_used)
        
        return {
            "total_sessions": len(sessions),
            "total_turns": total_turns,
            "total_duration_seconds": total_duration,
            "avg_turns_per_session": total_turns / len(sessions) if sessions else 0,
            "top_skills": all_skills.most_common(10),
            "sessions": [
                {
                    "id": s.id,
                    "name": s.name,
                    "turns": len(s.turns),
                    "duration": s.duration if s.end_time else None
                }
                for s in sessions
            ]
        }
    
    def _format_duration(self, seconds: float) -> str:
        """格式化持续时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟{secs}秒"
        else:
            return f"{secs}秒"
