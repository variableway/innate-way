"""文件存储基础"""

import os
import shutil
from pathlib import Path
from typing import Optional, List


class FileStore:
    """文件存储管理"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
    
    def ensure_dir(self, path: str) -> Path:
        """确保目录存在"""
        full_path = self.root_dir / path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def write(self, path: str, content: str) -> Path:
        """写入文件"""
        full_path = self.root_dir / path
        self.ensure_dir(full_path.parent)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def read(self, path: str) -> str:
        """读取文件"""
        full_path = self.root_dir / path
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return (self.root_dir / path).exists()
    
    def list_dirs(self, path: str = ".") -> List[str]:
        """列出子目录"""
        full_path = self.root_dir / path
        if not full_path.exists():
            return []
        return [d.name for d in full_path.iterdir() if d.is_dir()]
    
    def list_files(self, path: str = ".", pattern: str = "*") -> List[Path]:
        """列出文件"""
        full_path = self.root_dir / path
        if not full_path.exists():
            return []
        return list(full_path.rglob(pattern))
    
    def delete(self, path: str):
        """删除文件或目录"""
        full_path = self.root_dir / path
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
    
    def move(self, src: str, dst: str):
        """移动文件"""
        src_path = self.root_dir / src
        dst_path = self.root_dir / dst
        self.ensure_dir(dst_path.parent)
        shutil.move(str(src_path), str(dst_path))
