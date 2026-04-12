"""分类分析器"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import re

from ..models.entry import Entry
from ..storage.entry_store import EntryStore


class CategoryAnalyzer:
    """分类内容分析器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.entry_store = EntryStore(root_dir)
    
    def analyze(self, category: str) -> Dict[str, Any]:
        """分析分类内容并生成报告"""
        entries = self.entry_store.list_by_category(category)
        
        if not entries:
            empty_report = self._empty_report(category)
            self._save_report(category, empty_report)
            return empty_report
        
        # 基础统计
        stats = self._calculate_stats(entries)
        
        # 主题提取
        themes = self._extract_themes(entries)
        
        # 趋势分析
        trends = self._analyze_trends(entries)
        
        # 任务汇总
        tasks = self._aggregate_tasks(entries)
        
        # 生成报告
        report = {
            "category": category,
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "themes": themes,
            "trends": trends,
            "tasks": tasks,
            "recommendations": self._generate_recommendations(entries, stats)
        }
        
        # 保存报告到文件
        self._save_report(category, report)
        
        return report
    
    def generate_summary_markdown(self, category: str) -> str:
        """生成 Markdown 格式的汇总报告"""
        report = self.analyze(category)
        
        lines = [
            f"# {category} 分类汇总报告",
            "",
            f"生成时间: {report['generated_at']}",
            "",
            "## 统计概览",
            "",
            f"- 总条目数: {report['statistics']['total_entries']}",
            f"- 总任务数: {report['statistics']['total_tasks']}",
            f"- 唯一标签数: {report['statistics']['unique_tags']}",
            "",
            "### 优先级分布",
            "",
        ]
        
        for priority, count in report['statistics']['priority_distribution'].items():
            lines.append(f"- {priority}: {count}")
        
        lines.extend([
            "",
            "## 热门标签",
            "",
            "| 标签 | 出现次数 |",
            "|------|---------|",
        ])
        
        for tag, count in report['statistics']['top_tags']:
            lines.append(f"| {tag} | {count} |")
        
        lines.extend([
            "",
            "## 核心主题",
            "",
        ])
        
        for theme in report['themes']:
            lines.extend([
                f"### {theme['name']}",
                "",
                f"相关条目: {', '.join(theme['related_entries'][:5])}",
                "",
            ])
        
        lines.extend([
            "",
            "## 待办任务",
            "",
        ])
        
        for priority in ['P0', 'P1', 'P2']:
            priority_tasks = [t for t in report['tasks'] if t['priority'] == priority]
            if priority_tasks:
                lines.extend([
                    f"### {priority}",
                    "",
                ])
                for task in priority_tasks[:10]:  # 每优先级最多10个
                    lines.append(f"- [ ] {task['content']} ({task['entry_title']})")
                lines.append("")
        
        lines.extend([
            "",
            "## 建议",
            "",
        ])
        
        for rec in report['recommendations']:
            lines.append(f"- {rec}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _calculate_stats(self, entries: List[Entry]) -> Dict:
        """计算统计信息"""
        all_tags = []
        all_tasks = []
        priority_counts = {"P0": 0, "P1": 0, "P2": 0}
        
        for entry in entries:
            all_tags.extend(entry.tags)
            all_tasks.extend(entry.tasks)
            priority = entry.metadata.priority
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        tag_counter = Counter(all_tags)
        
        return {
            "total_entries": len(entries),
            "total_tasks": len(all_tasks),
            "unique_tags": len(set(all_tags)),
            "top_tags": tag_counter.most_common(10),
            "priority_distribution": priority_counts
        }
    
    def _extract_themes(self, entries: List[Entry]) -> List[Dict]:
        """提取核心主题"""
        # 基于标签和关键词聚类
        tag_groups = {}
        
        for entry in entries:
            for tag in entry.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(entry.title)
        
        # 按频次排序
        sorted_tags = sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        themes = []
        for tag, titles in sorted_tags[:5]:  # 前5个主题
            themes.append({
                "name": tag.capitalize(),
                "related_entries": titles
            })
        
        return themes
    
    def _analyze_trends(self, entries: List[Entry]) -> Dict:
        """分析时间趋势"""
        from collections import defaultdict
        
        monthly_counts = defaultdict(int)
        
        for entry in entries:
            month = entry.created_at.strftime("%Y-%m")
            monthly_counts[month] += 1
        
        return {
            "monthly_activity": dict(sorted(monthly_counts.items())),
            "peak_month": max(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else None
        }
    
    def _aggregate_tasks(self, entries: List[Entry]) -> List[Dict]:
        """汇总任务"""
        tasks = []
        
        for entry in entries:
            for task_content in entry.tasks:
                tasks.append({
                    "content": task_content,
                    "entry_title": entry.title,
                    "entry_id": entry.id,
                    "priority": entry.metadata.priority
                })
        
        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        tasks.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return tasks
    
    def _generate_recommendations(self, entries: List[Entry], stats: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于优先级的建议
        p0_count = stats['priority_distribution'].get('P0', 0)
        if p0_count > 5:
            recommendations.append(f"有 {p0_count} 个 P0 优先级任务，建议优先处理")
        
        # 基于任务数的建议
        if stats['total_tasks'] > stats['total_entries'] * 2:
            recommendations.append("平均每个条目包含多个任务，建议细化分解")
        
        # 基于标签的建议
        if stats['unique_tags'] > 20:
            recommendations.append("标签数量较多，建议整理合并相似标签")
        
        if not recommendations:
            recommendations.append("当前分类状态良好")
        
        return recommendations
    
    def _empty_report(self, category: str) -> Dict:
        """空分类报告"""
        return {
            "category": category,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_entries": 0,
                "total_tasks": 0,
                "unique_tags": 0,
                "top_tags": [],
                "priority_distribution": {}
            },
            "themes": [],
            "trends": {},
            "tasks": [],
            "recommendations": ["该分类暂无条目"]
        }
    
    def _save_report(self, category: str, report: Dict):
        """保存报告到文件"""
        import json
        from pathlib import Path
        
        report_dir = Path(self.root_dir) / category
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / "analysis_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
