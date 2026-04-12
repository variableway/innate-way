"""核心客户端"""

from pathlib import Path
from typing import Optional, List, Dict

from ..models.entry import Entry, EntryMetadata
from ..models.category import Category
from ..storage.entry_store import EntryStore
from ..storage.index_manager import IndexManager
from ..parser.input_parser import InputParser, InputType
from ..config import Config


class CaptureClient:
    """Capture TUI 核心客户端"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self.root_dir = Path(self.config.storage.root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        self.entry_store = EntryStore(str(self.root_dir))
        self.index_manager = IndexManager(str(self.root_dir))
        self.input_parser = InputParser()
    
    def add_idea(
        self,
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        title: Optional[str] = None,
        priority: Optional[str] = None,
        input_type: Optional[InputType] = None
    ) -> Entry:
        """添加想法/任务"""
        # 解析输入
        parsed = self.input_parser.parse(content, input_type)
        
        # 确定分类
        if category:
            pass
        elif parsed.tags:
            category = parsed.tags[0]
        else:
            category = self.config.input.default_category
        
        # 检查分类数量限制
        if not self._category_exists(category):
            if not self._can_create_category():
                raise ValueError(
                    f"Cannot create new category '{category}'. "
                    f"Maximum {self.config.storage.max_categories} categories allowed."
                )
        
        # 创建条目
        entry = Entry.create(
            title=title or parsed.title,
            content=parsed.content,
            category=category,
            tags=list(set((tags or []) + parsed.tags)),
            tasks=parsed.tasks,
            metadata=EntryMetadata(
                source=parsed.input_type.value,
                priority=priority or parsed.priority
            )
        )
        
        # 保存到文件
        self.entry_store.save(entry)
        
        # 更新索引
        self.index_manager.add_entry(entry)
        
        return entry
    
    def add_from_file(
        self,
        file_path: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Entry:
        """从文件添加"""
        parsed = self.input_parser.parse(file_path, InputType.FILE)
        
        return self.add_idea(
            content=parsed.raw_content,
            category=category or parsed.metadata.get('category'),
            tags=tags,
            title=parsed.title,
            input_type=InputType.FILE
        )
    
    def get_entry(self, entry_id: str) -> Optional[Entry]:
        """获取条目"""
        entry_data = self.index_manager.get_entry(entry_id)
        if not entry_data:
            return None
        
        # 尝试从存储路径加载
        path = entry_data.get('path')
        if path:
            try:
                return self.entry_store.load(path)
            except Exception:
                pass
        
        # 尝试从分类目录查找
        category = entry_data.get('category', 'uncategorized')
        entries = self.entry_store.list_by_category(category)
        for entry in entries:
            if entry.id == entry_id:
                return entry
        
        return None
    
    def list_entries(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        has_tasks: Optional[bool] = None
    ) -> List[Dict]:
        """列出入门"""
        return self.index_manager.list_entries(category, tags, has_tasks)
    
    def delete_entry(self, entry_id: str) -> bool:
        """删除条目"""
        # 先从索引获取路径信息
        entry_data = self.index_manager.get_entry(entry_id)
        if not entry_data:
            return False
        
        # 尝试找到并删除文件
        category = entry_data.get('category', 'uncategorized')
        entries = self.entry_store.list_by_category(category)
        
        for entry in entries:
            if entry.id == entry_id:
                self.entry_store.delete(entry)
                break
        
        # 从索引中移除
        self.index_manager.remove_entry(entry_id)
        return True
    
    def list_categories(self) -> List[Dict]:
        """列出所有分类"""
        return self.index_manager.list_categories()
    
    def get_category(self, name: str) -> Optional[Dict]:
        """获取分类信息"""
        return self.index_manager.get_category(name)
    
    def create_category(self, name: str, display_name: Optional[str] = None, description: str = "") -> Category:
        """创建分类"""
        if not self._can_create_category():
            raise ValueError(
                f"Maximum {self.config.storage.max_categories} categories allowed."
            )
        
        category = Category(
            name=name,
            display_name=display_name or name,
            description=description
        )
        
        # 创建目录
        category_dir = self.root_dir / name
        category_dir.mkdir(exist_ok=True)
        
        # 添加到索引
        self.index_manager.add_category(category)
        
        return category
    
    def analyze_category(self, category: str) -> Dict:
        """分析分类内容"""
        from ..ai.analyzer import CategoryAnalyzer
        analyzer = CategoryAnalyzer(str(self.root_dir))
        return analyzer.analyze(category)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.index_manager.get_stats()
    
    def _category_exists(self, name: str) -> bool:
        """检查分类是否存在"""
        return self.index_manager.get_category(name) is not None
    
    def _can_create_category(self) -> bool:
        """检查是否可以创建新分类"""
        categories = self.index_manager.list_categories()
        return len(categories) < self.config.storage.max_categories
    
    def init_project(self, root_dir: Optional[str] = None):
        """初始化项目"""
        if root_dir:
            self.config.storage.root_dir = root_dir
            self.root_dir = Path(root_dir)
        
        self.config.init_project(str(self.root_dir))
        
        # 重新初始化存储
        self.entry_store = EntryStore(str(self.root_dir))
        self.index_manager = IndexManager(str(self.root_dir))
