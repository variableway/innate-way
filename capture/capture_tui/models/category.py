"""Category 数据模型"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Category:
    """分类模型"""
    name: str
    display_name: str
    count: int = 0
    created_at: datetime = None
    last_entry: Optional[datetime] = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "count": self.count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_entry": self.last_entry.isoformat() if self.last_entry else None,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            count=data.get("count", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            last_entry=datetime.fromisoformat(data["last_entry"]) if data.get("last_entry") else None,
            description=data.get("description", "")
        )
    
    def update_count(self, delta: int = 1):
        """更新条目计数"""
        self.count += delta
        if delta > 0:
            self.last_entry = datetime.now()
