"""Entry 数据模型"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class EntryMetadata:
    """条目元数据"""
    source: str = "cli"  # cli, file, session
    priority: str = "P2"  # P0, P1, P2
    author: Optional[str] = None
    related_entries: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "EntryMetadata":
        return cls(**data)


@dataclass
class Entry:
    """想法/任务条目"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    tasks: List[str] = field(default_factory=list)
    metadata: EntryMetadata = field(default_factory=EntryMetadata)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        category: str = "uncategorized",
        tags: Optional[List[str]] = None,
        tasks: Optional[List[str]] = None,
        metadata: Optional[EntryMetadata] = None
    ) -> "Entry":
        """创建新条目"""
        entry_id = cls._generate_id()
        return cls(
            id=entry_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            tasks=tasks or [],
            metadata=metadata or EntryMetadata()
        )
    
    @staticmethod
    def _generate_id() -> str:
        """生成唯一ID"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        short_uuid = uuid.uuid4().hex[:6]
        return f"ideas-{timestamp}-{short_uuid}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tasks": self.tasks,
            "metadata": self.metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Entry":
        """从字典创建"""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            category=data["category"],
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            tasks=data.get("tasks", []),
            metadata=EntryMetadata.from_dict(data.get("metadata", {}))
        )
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        lines = [
            "---",
            f'id: "{self.id}"',
            f'category: "{self.category}"',
            f'created_at: "{self.created_at.isoformat()}"',
            f'tags: {self.tags}',
            f'priority: "{self.metadata.priority}"',
            f'source: "{self.metadata.source}"',
            "---",
            "",
            f"# {self.title}",
            "",
            self.content,
            "",
        ]
        
        if self.tasks:
            lines.extend([
                "## 关联任务",
                ""
            ])
            for task in self.tasks:
                lines.append(f"- [ ] {task}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, content: str) -> "Entry":
        """从 Markdown 解析"""
        import re
        
        # 解析 frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError("Invalid markdown format: missing frontmatter")
        
        import yaml
        fm = yaml.safe_load(frontmatter_match.group(1))
        body = frontmatter_match.group(2).strip()
        
        # 提取标题
        title_match = re.match(r'^# (.+)$', body, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"
        
        # 提取内容（去掉标题）
        content_body = re.sub(r'^# .+\n', '', body).strip()
        
        # 分离关联任务部分
        task_section_match = re.search(r'## 关联任务\n\n((?:- \[ \] .+\n?)+)', content_body)
        if task_section_match:
            # 从任务部分提取任务
            tasks = re.findall(r'- \[ \] (.+)', task_section_match.group(1))
            # 从内容中移除任务部分
            content_body = re.sub(r'\n?## 关联任务\n\n(?:- \[ \] .+\n?)+', '', content_body).strip()
        else:
            # 没有单独的任务部分，从整个内容提取
            tasks = re.findall(r'- \[ \] (.+)', content_body)
        
        metadata = EntryMetadata(
            source=fm.get("source", "file"),
            priority=fm.get("priority", "P2")
        )
        
        return cls(
            id=fm["id"],
            title=title,
            content=content_body,
            category=fm["category"],
            tags=fm.get("tags", []),
            created_at=datetime.fromisoformat(fm["created_at"]),
            metadata=metadata,
            tasks=tasks
        )
