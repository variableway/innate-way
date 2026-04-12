"""分类管理器"""

from pathlib import Path
from typing import List, Optional

from ..models.category import Category
from ..storage.index_manager import IndexManager


class CategoryManager:
    """分类管理器"""
    
    MAX_CATEGORIES = 10
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.index_manager = IndexManager(root_dir)
    
    def list_all(self) -> List[Category]:
        """列出所有分类"""
        data = self.index_manager.list_categories()
        return [Category.from_dict(c) for c in data]
    
    def get(self, name: str) -> Optional[Category]:
        """获取分类"""
        data = self.index_manager.get_category(name)
        if data:
            return Category.from_dict(data)
        return None
    
    def create(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: str = ""
    ) -> Category:
        """创建分类"""
        # 检查数量限制
        if not self.can_create():
            raise ValueError(
                f"Maximum {self.MAX_CATEGORIES} categories allowed. "
                "Please delete an existing category first."
            )
        
        # 检查名称是否已存在
        if self.get(name):
            raise ValueError(f"Category '{name}' already exists.")
        
        # 验证名称
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Category name must be alphanumeric (with - or _ allowed).")
        
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
    
    def delete(self, name: str, force: bool = False) -> bool:
        """删除分类"""
        category = self.get(name)
        if not category:
            return False
        
        # 检查是否有条目
        if category.count > 0 and not force:
            raise ValueError(
                f"Category '{name}' contains {category.count} entries. "
                "Use force=True to delete anyway."
            )
        
        # 删除目录
        import shutil
        category_dir = self.root_dir / name
        if category_dir.exists():
            shutil.rmtree(category_dir)
        
        # 从索引中移除
        # 注意：这里简化处理，实际应该更新索引
        
        return True
    
    def rename(self, old_name: str, new_name: str) -> Category:
        """重命名分类"""
        category = self.get(old_name)
        if not category:
            raise ValueError(f"Category '{old_name}' not found.")
        
        if self.get(new_name):
            raise ValueError(f"Category '{new_name}' already exists.")
        
        # 重命名目录
        old_dir = self.root_dir / old_name
        new_dir = self.root_dir / new_name
        old_dir.rename(new_dir)
        
        # 更新索引
        category.name = new_name
        self.index_manager.add_category(category)
        
        return category
    
    def can_create(self) -> bool:
        """检查是否可以创建新分类"""
        return len(self.list_all()) < self.MAX_CATEGORIES
    
    def get_count(self) -> int:
        """获取分类数量"""
        return len(self.list_all())
