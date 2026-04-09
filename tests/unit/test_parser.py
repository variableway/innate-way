"""解析器单元测试"""

import pytest
import tempfile
import os
from capture_tui.parser.input_parser import InputParser, InputType
from capture_tui.parser.extractors import TaskExtractor, TagExtractor, PriorityExtractor


class TestInputParser:
    """输入解析器测试"""
    
    def test_parse_text_input(self):
        """测试解析文本输入"""
        parser = InputParser()
        result = parser.parse("这是一个测试想法 #feature #important")
        
        assert result.input_type == InputType.TEXT
        assert "测试想法" in result.title
        assert "feature" in result.tags
        assert "important" in result.tags
    
    def test_parse_file_input(self):
        """测试解析文件输入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# 测试文件\n\n这是文件内容。\n\n- [ ] 任务1\n")
            temp_path = f.name
        
        try:
            parser = InputParser()
            result = parser.parse(temp_path, InputType.FILE)
            
            assert result.input_type == InputType.FILE
            assert result.title == "测试文件"
            assert "任务1" in result.tasks
        finally:
            os.unlink(temp_path)
    
    def test_parse_markdown_with_frontmatter(self):
        """测试解析带 frontmatter 的 Markdown"""
        content = """---
title: "测试"
tags: ["tag1", "tag2"]
---

# 标题

内容
"""
        parser = InputParser()
        result = parser._parse_markdown(content)
        
        assert result.input_type == InputType.MARKDOWN
        assert "tag1" in result.tags
        assert "tag2" in result.tags
    
    def test_detect_type_file(self):
        """测试检测文件类型"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("测试")
            temp_path = f.name
        
        try:
            parser = InputParser()
            result_type = parser._detect_type(temp_path)
            assert result_type == InputType.FILE
        finally:
            os.unlink(temp_path)
    
    def test_detect_type_url(self):
        """测试检测 URL 类型"""
        parser = InputParser()
        result_type = parser._detect_type("https://example.com/test")
        assert result_type == InputType.URL
    
    def test_detect_type_markdown(self):
        """测试检测 Markdown 类型"""
        parser = InputParser()
        result_type = parser._detect_type("# 标题\n内容")
        assert result_type == InputType.MARKDOWN


class TestTaskExtractor:
    """任务提取器测试"""
    
    def test_extract_markdown_todo(self):
        """测试提取 Markdown 待办"""
        extractor = TaskExtractor()
        content = "- [ ] 完成任务\n- [ ] 另一个任务"
        
        tasks = extractor.extract(content)
        
        assert "完成任务" in tasks
        assert "另一个任务" in tasks
    
    def test_extract_todo_keyword(self):
        """测试提取 TODO 关键词"""
        extractor = TaskExtractor()
        content = "TODO: 需要完成的任务"
        
        tasks = extractor.extract(content)
        
        assert any("需要完成的任务" in t for t in tasks)
    
    def test_extract_chinese_task(self):
        """测试提取中文任务"""
        extractor = TaskExtractor()
        content = "任务: 完成设计文档"
        
        tasks = extractor.extract(content)
        
        assert any("完成设计文档" in t for t in tasks)
    
    def test_deduplicate_tasks(self):
        """测试任务去重"""
        extractor = TaskExtractor()
        content = "- [ ] 重复任务\n- [ ] 重复任务\n- [ ] 另一个任务"
        
        tasks = extractor.extract(content)
        
        assert len(tasks) == 2


class TestTagExtractor:
    """标签提取器测试"""
    
    def test_extract_hash_tags(self):
        """测试提取 #标签"""
        extractor = TagExtractor()
        content = "这是一个 #feature #important 的想法"
        
        tags = extractor.extract(content)
        
        assert "feature" in tags
        assert "important" in tags
    
    def test_tag_lowercase(self):
        """测试标签转小写"""
        extractor = TagExtractor()
        content = "#FEATURE #Important"
        
        tags = extractor.extract(content)
        
        assert "feature" in tags
        assert "important" in tags
        assert "FEATURE" not in tags
    
    def test_no_duplicates(self):
        """测试无重复标签"""
        extractor = TagExtractor()
        content = "#tag #tag #TAG"
        
        tags = extractor.extract(content)
        
        assert len(tags) == 1


class TestPriorityExtractor:
    """优先级提取器测试"""
    
    def test_extract_p0(self):
        """测试提取 P0"""
        extractor = PriorityExtractor()
        
        assert extractor.extract("这是一个 P0 任务") == "P0"
        assert extractor.extract("【紧急】需要处理") == "P0"
        assert extractor.extract("urgent task") == "P0"
    
    def test_extract_p1(self):
        """测试提取 P1"""
        extractor = PriorityExtractor()
        
        assert extractor.extract("这是一个 P1 任务") == "P1"
        assert extractor.extract("【重要】需要处理") == "P1"
        assert extractor.extract("important task") == "P1"
    
    def test_default_p2(self):
        """测试默认 P2"""
        extractor = PriorityExtractor()
        
        assert extractor.extract("普通任务") == "P2"
        assert extractor.extract("") == "P2"
