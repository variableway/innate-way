"""索引管理"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.entry import Entry
from ..models.category import Category


class IndexManager:
    """索引管理器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.index_path = self.root_dir / ".capture" / "index.json"
        self._cache: Optional[Dict] = None
    
    def _load(self) -> Dict:
        """加载索引"""
        if self._cache is not None:
            return self._cache
        
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        else:
            self._cache = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "categories": [],
                "entries": [],
                "stats": {
                    "total_entries": 0,
                    "total_categories": 0,
                    "pending_tasks": 0
                }
            }
        return self._cache
    
    def _save(self):
        """保存索引"""
        data = self._load()
        data["last_updated"] = datetime.now().isoformat()
        
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, entry: Entry):
        """添加条目到索引"""
        data = self._load()
        
        # 检查是否已存在
        for i, e in enumerate(data["entries"]):
            if e["id"] == entry.id:
                data["entries"][i] = self._entry_to_dict(entry)
                break
        else:
            data["entries"].append(self._entry_to_dict(entry))
        
        # 更新分类计数
        self._update_category_count(entry.category, 1)
        
        # 更新统计
        data["stats"]["total_entries"] = len(data["entries"])
        data["stats"]["total_categories"] = len(data["categories"])
        data["stats"]["pending_tasks"] = sum(
            e.get("task_count", 0) for e in data["entries"]
        )
        
        self._save()
    
    def remove_entry(self, entry_id: str) -> Optional[dict]:
        """从索引中移除条目"""
        data = self._load()
        
        for i, e in enumerate(data["entries"]):
            if e["id"] == entry_id:
                entry_data = data["entries"].pop(i)
                
                # 更新分类计数
                self._update_category_count(entry_data["category"], -1)
                
                # 更新统计
                data["stats"]["total_entries"] = len(data["entries"])
                data["stats"]["pending_tasks"] = sum(
                    e.get("task_count", 0) for e in data["entries"]
                )
                
                self._save()
                return entry_data
        
        return None
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """获取条目"""
        data = self._load()
        for e in data["entries"]:
            if e["id"] == entry_id:
                return e
        return None
    
    def list_entries(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        has_tasks: Optional[bool] = None
    ) -> List[Dict]:
        """列出入门"""
        data = self._load()
        entries = data["entries"]
        
        if category:
            entries = [e for e in entries if e["category"] == category]
        
        if tags:
            entries = [e for e in entries if any(t in e.get("tags", []) for t in tags)]
        
        if has_tasks is not None:
            entries = [e for e in entries if bool(e.get("tasks")) == has_tasks]
        
        # 按时间倒序
        entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return entries
    
    def add_category(self, category: Category):
        """添加分类"""
        data = self._load()
        
        # 检查是否已存在
        for i, c in enumerate(data["categories"]):
            if c["name"] == category.name:
                data["categories"][i] = category.to_dict()
                break
        else:
            data["categories"].append(category.to_dict())
        
        data["stats"]["total_categories"] = len(data["categories"])
        self._save()
    
    def get_category(self, name: str) -> Optional[Dict]:
        """获取分类"""
        data = self._load()
        for c in data["categories"]:
            if c["name"] == name:
                return c
        return None
    
    def list_categories(self) -> List[Dict]:
        """列出所有分类"""
        data = self._load()
        return data["categories"]
    
    def _update_category_count(self, category_name: str, delta: int):
        """更新分类计数"""
        data = self._load()
        for c in data["categories"]:
            if c["name"] == category_name:
                c["count"] = max(0, c.get("count", 0) + delta)
                if delta > 0:
                    c["last_entry"] = datetime.now().isoformat()
                break
        else:
            # 自动创建分类
            if delta > 0:
                data["categories"].append({
                    "name": category_name,
                    "display_name": category_name,
                    "count": delta,
                    "created_at": datetime.now().isoformat(),
                    "last_entry": datetime.now().isoformat()
                })
                data["stats"]["total_categories"] = len(data["categories"])
    
    def _entry_to_dict(self, entry: Entry) -> Dict:
        """转换条目为字典"""
        return {
            "id": entry.id,
            "path": self._get_entry_path(entry),
            "category": entry.category,
            "title": entry.title,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "has_tasks": bool(entry.tasks),
            "task_count": len(entry.tasks)
        }
    
    def _get_entry_path(self, entry: Entry) -> str:
        """获取条目存储路径"""
        from .entry_store import EntryStore
        return str(EntryStore(self.root_dir).get_path(entry))
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        data = self._load()
        return data["stats"]
    
    def rebuild(self):
        """重建索引"""
        # 扫描所有文件重建索引
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "categories": [],
            "entries": [],
            "stats": {
                "total_entries": 0,
                "total_categories": 0,
                "pending_tasks": 0
            }
        }
        
        # 保存空索引
        self._cache = data
        self._save()
        
        # 扫描文件
        for entry_file in self.root_dir.rglob("*.md"):
            if ".capture" in str(entry_file):
                continue
            if entry_file.name == "summary.md":
                continue
            
            try:
                with open(entry_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                entry = Entry.from_markdown(content)
                self.add_entry(entry)
            except Exception:
                pass  # 忽略解析错误
