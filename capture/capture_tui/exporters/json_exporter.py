"""JSON 导出器"""

import json
from pathlib import Path
from typing import List, Dict, Any


class JSONExporter:
    """JSON 导出器"""
    
    def export(
        self,
        data: Any,
        output_path: str,
        pretty: bool = True
    ) -> str:
        """导出数据到 JSON 文件"""
        indent = 2 if pretty else None
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        return output_path
    
    def export_entries(
        self,
        entries: List[Dict],
        output_path: str,
        include_content: bool = True
    ) -> str:
        """导出条目"""
        if not include_content:
            # 简化版本，不包含完整内容
            entries = [
                {k: v for k, v in e.items() if k != 'content'}
                for e in entries
            ]
        
        return self.export(entries, output_path)
    
    def to_string(self, data: Any, pretty: bool = True) -> str:
        """转换为 JSON 字符串"""
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    
    def export_stats(self, stats: Dict, output_path: str) -> str:
        """导出统计信息"""
        return self.export(stats, output_path)
