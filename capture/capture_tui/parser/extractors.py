"""内容提取器"""

import re
from typing import List


class TaskExtractor:
    """任务提取器"""
    
    PATTERNS = [
        r'- \[ \] (.+)',          # Markdown 待办
        r'TODO[:：]\s*(.+)',      # TODO: 任务
        r'任务[:：]\s*(.+)',      # 任务: 任务
        r'ACTION[:：]\s*(.+)',     # ACTION: 动作
        r'(?:需要|应该|要)\s*(.+?)(?:，|。|$)',  # 需要/应该/要 ...
    ]
    
    def extract(self, content: str) -> List[str]:
        """提取任务列表"""
        tasks = []
        for pattern in self.PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            tasks.extend(matches)
        
        # 去重并清理
        seen = set()
        cleaned = []
        for task in tasks:
            task = task.strip()
            if task and task not in seen:
                seen.add(task)
                cleaned.append(task)
        
        return cleaned


class TagExtractor:
    """标签提取器"""
    
    PATTERN = r'#(\w+)'
    
    # 常见的标签词
    COMMON_TAGS = [
        'feature', 'bug', 'improvement', 'docs', 'refactor',
        'ui', 'api', 'backend', 'frontend', 'test',
        'urgent', 'important', 'later', 'idea'
    ]
    
    def extract(self, content: str) -> List[str]:
        """提取标签"""
        # 提取 #tag 格式
        tags = re.findall(self.PATTERN, content)
        
        # 转换为小写并去重
        tags = list(set(t.lower() for t in tags))
        
        return tags


class PriorityExtractor:
    """优先级提取器"""
    
    PATTERNS = {
        'P0': [
            r'P0',
            r'【紧急】',
            r'【高优先级】',
            r'urgent',
            r'critical',
            r'ASAP',
        ],
        'P1': [
            r'P1',
            r'【重要】',
            r'important',
            r'high priority',
        ],
        'P2': [
            r'P2',
            r'【一般】',
            r'normal',
            r'low priority',
        ]
    }
    
    def extract(self, content: str) -> str:
        """提取优先级"""
        # 中文模式不需要转小写
        for priority, patterns in self.PATTERNS.items():
            for pattern in patterns:
                # 检查原始内容（用于中文匹配）
                if re.search(pattern, content):
                    return priority
                # 检查小写内容（用于英文匹配）
                if re.search(pattern, content, re.IGNORECASE):
                    return priority
        
        return 'P2'  # 默认优先级


class TitleExtractor:
    """标题提取器"""
    
    def extract(self, content: str, max_length: int = 100) -> str:
        """提取标题"""
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 如果是 Markdown 标题
            if line.startswith('#'):
                return line.lstrip('#').strip()[:max_length]
            
            # 普通文本取第一行
            return line[:max_length]
        
        return "Untitled"
