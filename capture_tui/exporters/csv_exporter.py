"""CSV 导出器"""

import csv
import io
from pathlib import Path
from typing import List, Dict, Any


class CSVExporter:
    """CSV 导出器"""
    
    DEFAULT_FIELDS = [
        'id', 'category', 'title', 'tags', 'created_at',
        'content', 'tasks', 'priority'
    ]
    
    def export_entries(
        self,
        entries: List[Dict],
        output_path: str,
        fields: List[str] = None,
        tasks_only: bool = False
    ) -> str:
        """导出条目到 CSV"""
        if fields is None:
            fields = self.DEFAULT_FIELDS
        
        # 过滤只包含任务的条目
        if tasks_only:
            entries = [e for e in entries if e.get('has_tasks')]
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            for entry in entries:
                row = self._format_row(entry, fields)
                writer.writerow(row)
        
        return output_path
    
    def export_tasks(
        self,
        entries: List[Dict],
        output_path: str
    ) -> str:
        """导出任务列表"""
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['任务内容', '来源条目', '分类', '优先级', '创建时间'])
            
            for entry in entries:
                for task in entry.get('tasks', []):
                    writer.writerow([
                        task,
                        entry.get('title', ''),
                        entry.get('category', ''),
                        entry.get('priority', 'P2'),
                        entry.get('created_at', '')
                    ])
        
        return output_path
    
    def to_string(self, entries: List[Dict], fields: List[str] = None) -> str:
        """导出为 CSV 字符串"""
        if fields is None:
            fields = self.DEFAULT_FIELDS
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        
        for entry in entries:
            row = self._format_row(entry, fields)
            writer.writerow(row)
        
        return output.getvalue()
    
    def _format_row(self, entry: Dict, fields: List[str]) -> Dict:
        """格式化行数据"""
        row = {}
        
        for field in fields:
            value = entry.get(field, '')
            
            if field == 'tags' and isinstance(value, list):
                value = ','.join(value)
            elif field == 'tasks' and isinstance(value, list):
                value = '|'.join(value)
            elif field == 'priority':
                # 从 metadata 中获取
                metadata = entry.get('metadata', {})
                value = metadata.get('priority', 'P2')
            
            row[field] = value
        
        return row
