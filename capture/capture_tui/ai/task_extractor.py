"""AI 任务提取器"""

from typing import List, Dict
from ..models.entry import Entry


class AITaskExtractor:
    """智能任务提取器"""
    
    ACTION_KEYWORDS = [
        "需要", "应该", "要", "必须", "得",
        "实现", "完成", "添加", "修改", "删除",
        "创建", "设计", "开发", "测试", "部署",
        "优化", "修复", "重构", "集成"
    ]
    
    def extract_from_entry(self, entry: Entry) -> List[Dict]:
        """从条目中提取任务"""
        tasks = []
        
        for task in entry.tasks:
            tasks.append({
                "content": task,
                "priority": entry.metadata.priority,
                "source_entry": entry.id,
                "category": entry.category
            })
        
        # 从内容中提取隐含任务
        implied_tasks = self._extract_implied_tasks(entry.content)
        for task in implied_tasks:
            if not any(t['content'] == task for t in tasks):
                tasks.append({
                    "content": task,
                    "priority": "P2",
                    "source_entry": entry.id,
                    "category": entry.category
                })
        
        return tasks
    
    def extract_from_entries(self, entries: List[Entry]) -> List[Dict]:
        """批量提取任务"""
        all_tasks = []
        for entry in entries:
            all_tasks.extend(self.extract_from_entry(entry))
        
        # 去重
        seen = set()
        unique_tasks = []
        for task in all_tasks:
            key = task['content']
            if key not in seen:
                seen.add(key)
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _extract_implied_tasks(self, content: str) -> List[str]:
        """提取隐含任务"""
        import re
        
        tasks = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否包含动作关键词
            for keyword in self.ACTION_KEYWORDS:
                if keyword in line and len(line) > 10:
                    # 清理并提取
                    task = re.sub(r'^[\s\-•]*', '', line)
                    if task and len(task) < 200:
                        tasks.append(task)
                        break
        
        return tasks[:10]  # 限制数量
    
    def deduplicate_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """任务去重"""
        seen = set()
        result = []
        
        for task in tasks:
            # 简单的文本相似度去重
            content = task['content'].lower().strip()
            
            # 检查是否已存在相似任务
            is_duplicate = False
            for seen_task in seen:
                if self._similarity(content, seen_task) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen.add(content)
                result.append(task)
        
        return result
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度（简单实现）"""
        if s1 == s2:
            return 1.0
        
        # 使用集合交集计算
        set1 = set(s1.split())
        set2 = set(s2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
