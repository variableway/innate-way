"""内容摘要生成器"""

from typing import List, Dict
from ..models.entry import Entry


class ContentSummarizer:
    """内容摘要生成器"""
    
    def summarize_entry(self, entry: Entry) -> str:
        """生成单个条目的摘要"""
        lines = [
            f"标题: {entry.title}",
            f"分类: {entry.category}",
            f"标签: {', '.join(entry.tags) if entry.tags else '无'}",
            f"优先级: {entry.metadata.priority}",
        ]
        
        if entry.tasks:
            lines.append(f"包含 {len(entry.tasks)} 个待办任务")
        
        return " | ".join(lines)
    
    def summarize_entries(self, entries: List[Entry]) -> Dict:
        """批量生成摘要"""
        summaries = []
        for entry in entries:
            summaries.append({
                "id": entry.id,
                "title": entry.title,
                "summary": self.summarize_entry(entry),
                "key_points": self._extract_key_points(entry.content)
            })
        
        return {
            "total": len(entries),
            "summaries": summaries
        }
    
    def _extract_key_points(self, content: str, max_points: int = 3) -> List[str]:
        """提取关键点"""
        # 简单的句子提取
        sentences = content.replace('。', '.').replace('，', ',').split('.')
        points = []
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 10 and len(points) < max_points:
                points.append(sent[:100])  # 限制长度
        
        return points
