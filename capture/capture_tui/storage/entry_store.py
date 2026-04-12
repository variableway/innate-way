"""Entry 存储管理"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from .file_store import FileStore
from ..models.entry import Entry


class EntryStore:
    """条目存储管理器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.file_store = FileStore(root_dir)
    
    def save(self, entry: Entry) -> Path:
        """保存条目"""
        path = self.get_path(entry)
        content = entry.to_markdown()
        return self.file_store.write(str(path), content)
    
    def load(self, path: str) -> Entry:
        """加载条目"""
        content = self.file_store.read(path)
        return Entry.from_markdown(content)
    
    def get_path(self, entry: Entry) -> Path:
        """获取条目存储路径"""
        # 格式: {category}/{YYYY-MM}/{DD}-{SEQ}-{slug}.md
        date = entry.created_at
        month_dir = f"{date.strftime('%Y-%m')}"
        
        # 计算序号
        seq = self._get_next_sequence(entry.category, date)
        
        # 生成 slug
        slug = self._slugify(entry.title)[:30]
        
        filename = f"{date.strftime('%d')}-{seq:03d}-{slug}.md"
        
        return Path(entry.category) / month_dir / filename
    
    def _get_next_sequence(self, category: str, date: datetime) -> int:
        """获取下一个序号"""
        category_dir = self.root_dir / category / date.strftime('%Y-%m')
        if not category_dir.exists():
            return 1
        
        # 查找当天的最大序号
        day_prefix = date.strftime('%d')
        max_seq = 0
        
        for f in category_dir.iterdir():
            if f.is_file() and f.name.startswith(day_prefix + "-"):
                try:
                    seq = int(f.name.split('-')[1])
                    max_seq = max(max_seq, seq)
                except (IndexError, ValueError):
                    pass
        
        return max_seq + 1
    
    def _slugify(self, text: str) -> str:
        """生成 URL 友好的 slug"""
        # 替换非字母数字字符为 -
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def list_by_category(self, category: str) -> List[Entry]:
        """列出分类下的所有条目"""
        entries = []
        category_dir = self.root_dir / category
        
        if not category_dir.exists():
            return entries
        
        for md_file in category_dir.rglob("*.md"):
            if md_file.name == "summary.md":
                continue
            try:
                rel_path = md_file.relative_to(self.root_dir)
                entry = self.load(str(rel_path))
                entries.append(entry)
            except Exception as e:
                # 忽略解析错误
                pass
        
        # 按时间倒序
        entries.sort(key=lambda e: e.created_at, reverse=True)
        return entries
    
    def delete(self, entry: Entry):
        """删除条目"""
        path = self.get_path(entry)
        if self.file_store.exists(str(path)):
            self.file_store.delete(str(path))
    
    def exists(self, entry: Entry) -> bool:
        """检查条目是否存在"""
        path = self.get_path(entry)
        return self.file_store.exists(str(path))
