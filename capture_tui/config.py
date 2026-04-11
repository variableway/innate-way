"""配置管理模块"""

import os
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from pathlib import Path


@dataclass
class StorageConfig:
    """存储配置"""
    root_dir: str = "./ideas"
    max_categories: int = 10
    auto_create_category: bool = True
    archive_after_days: int = 90


@dataclass
class InputConfig:
    """输入配置"""
    default_category: str = "uncategorized"
    extract_tasks_auto: bool = True
    extract_tags_auto: bool = True


@dataclass
class AIConfig:
    """AI配置"""
    enabled: bool = True
    model: str = "kimi"
    summarize_on_analyze: bool = True
    auto_categorize: bool = False


@dataclass
class FeishuConfig:
    """飞书配置"""
    enabled: bool = False
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    default_table: Optional[str] = None


@dataclass
class ExportConfig:
    """导出配置"""
    formats: List[str] = field(default_factory=lambda: ["md", "csv", "json"])
    feishu: FeishuConfig = field(default_factory=FeishuConfig)


@dataclass
class SessionConfig:
    """会话配置"""
    capture_dir: str = "./docs/capture-tui/sessions"
    auto_capture: bool = True
    capture_thinking: bool = True
    max_duration: int = 3600  # 秒


@dataclass
class TutorialConfig:
    """Tutorial generator配置"""
    output_dir: str = "./output/tutorials"
    default_template: str = "md_script"
    claude_enabled: bool = True
    review_enabled: bool = False
    max_workers: int = 4
    retry_max: int = 3
    retry_backoff: float = 2.0
    fetch_timeout: int = 30
    user_agent: str = "InnateTutorialGenerator/1.0"
    queue_dir: str = ""  # defaults to {output_dir}/.tutorial


@dataclass
class Config:
    """全局配置"""
    version: str = "1.0"
    storage: StorageConfig = field(default_factory=StorageConfig)
    input: InputConfig = field(default_factory=InputConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    tutorial: TutorialConfig = field(default_factory=TutorialConfig)
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """加载配置"""
        if path is None:
            path = cls._find_config_file()
        
        if not path or not os.path.exists(path):
            return cls._create_default()
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 环境变量替换
        data = cls._expand_env_vars(data)
        
        return cls._from_dict(data)
    
    @classmethod
    def _find_config_file(cls) -> Optional[str]:
        """查找配置文件"""
        candidates = [
            "./.capture/config.yaml",
            "./ideas/.capture/config.yaml",
            os.path.expanduser("~/.capture/config.yaml"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None
    
    @classmethod
    def _create_default(cls) -> "Config":
        """创建默认配置"""
        return cls()
    
    @classmethod
    def _expand_env_vars(cls, data):
        """展开环境变量"""
        if isinstance(data, dict):
            return {k: cls._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls._expand_env_vars(v) for v in data]
        elif isinstance(data, str):
            return os.path.expandvars(data)
        return data
    
    @classmethod
    def _from_dict(cls, data: dict) -> "Config":
        """从字典创建配置"""
        return cls(
            version=data.get("version", "1.0"),
            storage=StorageConfig(**data.get("storage", {})),
            input=InputConfig(**data.get("input", {})),
            ai=AIConfig(**data.get("ai", {})),
            export=ExportConfig(
                formats=data.get("export", {}).get("formats", ["md", "csv", "json"]),
                feishu=FeishuConfig(**data.get("export", {}).get("feishu", {}))
            ),
            session=SessionConfig(**data.get("session", {})),
            tutorial=TutorialConfig(**data.get("tutorial", {}))
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "version": self.version,
            "storage": asdict(self.storage),
            "input": asdict(self.input),
            "ai": asdict(self.ai),
            "export": {
                "formats": self.export.formats,
                "feishu": asdict(self.export.feishu)
            },
            "session": asdict(self.session),
            "tutorial": asdict(self.tutorial)
        }
    
    def save(self, path: str):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def init_project(self, root_dir: str = "./ideas"):
        """初始化项目目录"""
        self.storage.root_dir = root_dir
        
        # 创建目录结构
        dirs = [
            root_dir,
            f"{root_dir}/.capture/templates",
            f"{root_dir}/.capture/sessions",
            f"{root_dir}/uncategorized",
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        
        # 保存配置
        self.save(f"{root_dir}/.capture/config.yaml")
        
        # 创建模板文件
        self._create_templates(root_dir)
        
        # 创建初始索引
        self._create_index(root_dir)
    
    def _create_templates(self, root_dir: str):
        """创建模板文件"""
        idea_template = """---
id: "{{id}}"
category: "{{category}}"
created_at: "{{created_at}}"
tags: {{tags}}
priority: "{{priority}}"
source: "{{source}}"
---

# {{title}}

{{content}}

{% if tasks %}
## 关联任务
{% for task in tasks %}
- [ ] {{task}}
{% endfor %}
{% endif %}
"""
        template_path = f"{root_dir}/.capture/templates/idea.md.tpl"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(idea_template)
    
    def _create_index(self, root_dir: str):
        """创建初始索引"""
        index = {
            "version": "1.0",
            "last_updated": None,
            "categories": [],
            "entries": [],
            "stats": {
                "total_entries": 0,
                "total_categories": 0,
                "pending_tasks": 0
            }
        }
        index_path = f"{root_dir}/.capture/index.json"
        import json
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def set_config(config: Config):
    """设置全局配置"""
    global _config
    _config = config
