"""Markdown 导出器"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime


class MarkdownExporter:
    """Markdown 导出器"""
    
    def export_entries(
        self,
        entries: List[Dict],
        output_path: str,
        title: str = "导出文档"
    ) -> str:
        """导出条目到 Markdown"""
        lines = [
            f"# {title}",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"共 {len(entries)} 条记录",
            "",
            "---",
            "",
        ]
        
        for entry in entries:
            lines.extend(self._format_entry(entry))
            lines.append("---")
            lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def export_todo_list(
        self,
        entries: List[Dict],
        output_path: str
    ) -> str:
        """导出待办列表"""
        lines = [
            "# 待办任务列表",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        # 按优先级分组
        priorities = {'P0': [], 'P1': [], 'P2': []}
        
        for entry in entries:
            priority = entry.get('metadata', {}).get('priority', 'P2')
            for task in entry.get('tasks', []):
                priorities.get(priority, priorities['P2']).append({
                    'task': task,
                    'entry': entry.get('title', ''),
                    'category': entry.get('category', '')
                })
        
        for priority in ['P0', 'P1', 'P2']:
            tasks = priorities[priority]
            if tasks:
                lines.extend([
                    f"## {priority}",
                    "",
                ])
                for item in tasks:
                    lines.append(f"- [ ] {item['task']} ({item['entry']})")
                lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def _format_entry(self, entry: Dict) -> List[str]:
        """格式化单个条目"""
        lines = [
            f"## {entry.get('title', 'Untitled')}",
            "",
            f"**ID**: {entry.get('id', '')}",
            f"**分类**: {entry.get('category', '')}",
            f"**标签**: {', '.join(entry.get('tags', []))}",
            f"**时间**: {entry.get('created_at', '')}",
            "",
        ]
        
        content = entry.get('content', '')
        if content:
            lines.append(content)
            lines.append("")
        
        tasks = entry.get('tasks', [])
        if tasks:
            lines.append("**关联任务**:")
            lines.append("")
            for task in tasks:
                lines.append(f"- [ ] {task}")
            lines.append("")
        
        return lines
