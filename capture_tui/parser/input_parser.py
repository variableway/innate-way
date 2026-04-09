"""输入解析器"""

import re
from enum import Enum, auto
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

from .extractors import TaskExtractor, TagExtractor, PriorityExtractor


class InputType(Enum):
    """输入类型"""
    TEXT = "text"
    FILE = "file"
    URL = "url"
    MARKDOWN = "markdown"


@dataclass
class ParsedInput:
    """解析后的输入"""
    raw_content: str
    input_type: InputType
    title: Optional[str] = None
    content: str = ""
    tasks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    priority: str = "P2"
    source_path: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class InputParser:
    """输入解析器"""
    
    def __init__(self):
        self.task_extractor = TaskExtractor()
        self.tag_extractor = TagExtractor()
        self.priority_extractor = PriorityExtractor()
    
    def parse(self, content: str, input_type: Optional[InputType] = None) -> ParsedInput:
        """解析输入内容"""
        # 检测输入类型
        if input_type is None:
            input_type = self._detect_type(content)
        
        # 根据类型处理
        if input_type == InputType.FILE:
            return self._parse_file(content)
        elif input_type == InputType.URL:
            return self._parse_url(content)
        else:
            return self._parse_text(content)
    
    def _detect_type(self, content: str) -> InputType:
        """检测输入类型"""
        content = content.strip()
        
        # 检查是否是文件路径
        if Path(content).exists() and Path(content).is_file():
            return InputType.FILE
        
        # 检查是否是 URL
        if content.startswith(('http://', 'https://')):
            return InputType.URL
        
        # 检查是否是 Markdown (优先检查 frontmatter 格式)
        if content.strip().startswith('---') or content.strip().startswith('#'):
            return InputType.MARKDOWN
        
        return InputType.TEXT
    
    def _parse_text(self, content: str) -> ParsedInput:
        """解析文本输入"""
        # 提取第一行作为标题
        lines = content.strip().split('\n')
        title = lines[0][:100] if lines else "Untitled"
        
        # 提取任务
        tasks = self.task_extractor.extract(content)
        
        # 提取标签
        tags = self.tag_extractor.extract(content)
        
        # 提取优先级
        priority = self.priority_extractor.extract(content)
        
        return ParsedInput(
            raw_content=content,
            input_type=InputType.TEXT,
            title=title,
            content=content,
            tasks=tasks,
            tags=tags,
            priority=priority
        )
    
    def _parse_file(self, file_path: str) -> ParsedInput:
        """解析文件输入"""
        path = Path(file_path)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否是 Markdown
        if path.suffix in ['.md', '.markdown']:
            result = self._parse_markdown(content, str(path))
            result.input_type = InputType.FILE
            return result
        
        # 普通文本文件
        result = self._parse_text(content)
        result.input_type = InputType.FILE
        result.source_path = str(path)
        result.metadata['file_name'] = path.name
        result.metadata['file_size'] = path.stat().st_size
        
        return result
    
    def _parse_url(self, url: str) -> ParsedInput:
        """解析 URL 输入"""
        # 简化实现，实际可能需要网络请求获取内容
        parsed = urlparse(url)
        title = f"Content from {parsed.netloc}"
        
        return ParsedInput(
            raw_content=url,
            input_type=InputType.URL,
            title=title,
            content=url,
            source_path=url,
            metadata={'url': url, 'domain': parsed.netloc}
        )
    
    def _parse_markdown(self, content: str, source_path: Optional[str] = None) -> ParsedInput:
        """解析 Markdown 输入"""
        # 尝试提取 frontmatter
        import yaml
        
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        
        if frontmatter_match:
            # 有 frontmatter
            try:
                fm = yaml.safe_load(frontmatter_match.group(1))
                body = frontmatter_match.group(2).strip()
            except yaml.YAMLError:
                fm = {}
                body = content
        else:
            fm = {}
            body = content
        
        # 提取标题
        title_match = re.match(r'^# (.+)$', body, re.MULTILINE)
        title = title_match.group(1) if title_match else (fm.get('title', 'Untitled'))
        
        # 提取任务
        tasks = self.task_extractor.extract(body)
        
        # 提取标签
        tags = list(set(
            (fm.get('tags', [])) + 
            self.tag_extractor.extract(body)
        ))
        
        # 提取优先级
        priority = fm.get('priority') or self.priority_extractor.extract(body)
        
        return ParsedInput(
            raw_content=content,
            input_type=InputType.MARKDOWN,
            title=title,
            content=body,
            tasks=tasks,
            tags=tags,
            priority=priority,
            source_path=source_path,
            metadata=fm
        )
