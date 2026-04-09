"""CLI 主入口"""

import click
import os
from pathlib import Path

from ..core.client import CaptureClient
from ..core.category_manager import CategoryManager
from ..config import Config
from ..session.manager import SessionManager


# 创建客户端实例
pass_client = click.make_pass_decorator(CaptureClient)


@click.group()
@click.option(
    '--config',
    '-c',
    type=click.Path(),
    help='配置文件路径'
)
@click.option(
    '--root-dir',
    '-r',
    type=click.Path(),
    help='数据根目录'
)
@click.pass_context
def cli(ctx, config, root_dir):
    """Capture TUI - 终端输入捕获与管理工具"""
    # 加载配置
    cfg = Config.load(config) if config else Config.load()
    
    if root_dir:
        cfg.storage.root_dir = root_dir
    
    # 创建客户端
    ctx.ensure_object(dict)
    ctx.obj['client'] = CaptureClient(cfg)
    ctx.obj['config'] = cfg


# ===== 添加命令 =====

@cli.command()
@click.argument('content', required=False)
@click.option('--category', '-c', help='分类名称')
@click.option('--tags', '-t', help='标签（逗号分隔）')
@click.option('--title', help='标题')
@click.option('--priority', '-p', type=click.Choice(['P0', 'P1', 'P2']), help='优先级')
@click.option('--file', '-f', type=click.Path(exists=True), help='从文件读取')
@click.pass_context
def add(ctx, content, category, tags, title, priority, file):
    """添加想法/任务"""
    client = ctx.obj['client']
    
    try:
        if file:
            # 从文件添加
            tag_list = tags.split(',') if tags else None
            entry = client.add_from_file(file, category, tag_list)
            click.echo(f"✓ 已从文件添加: {entry.id}")
        elif content:
            # 从命令行参数添加
            tag_list = tags.split(',') if tags else None
            entry = client.add_idea(
                content=content,
                category=category,
                tags=tag_list,
                title=title,
                priority=priority
            )
            click.echo(f"✓ 已添加: {entry.id}")
            click.echo(f"  分类: {entry.category}")
            click.echo(f"  标题: {entry.title}")
            if entry.tasks:
                click.echo(f"  任务: {len(entry.tasks)} 个")
        else:
            # 交互式输入
            click.echo("请输入内容 (Ctrl+D 结束):")
            content_lines = []
            while True:
                try:
                    line = input()
                    content_lines.append(line)
                except EOFError:
                    break
            
            if content_lines:
                content = '\n'.join(content_lines)
                tag_list = tags.split(',') if tags else None
                entry = client.add_idea(
                    content=content,
                    category=category,
                    tags=tag_list,
                    title=title,
                    priority=priority
                )
                click.echo(f"✓ 已添加: {entry.id}")
            else:
                click.echo("✗ 未输入内容")
    
    except ValueError as e:
        click.echo(f"✗ 错误: {e}", err=True)
        raise click.Abort()


# ===== 分类命令 =====

@cli.group()
def categories():
    """分类管理"""
    pass


@categories.command('list')
@click.pass_context
def list_categories(ctx):
    """列出所有分类"""
    client = ctx.obj['client']
    cats = client.list_categories()
    
    if not cats:
        click.echo("暂无分类")
        return
    
    click.echo(f"{'分类名称':<20} {'条目数':<10} {'最后更新':<20}")
    click.echo("-" * 50)
    
    for cat in cats:
        last_entry = cat.get('last_entry', 'N/A')
        if last_entry and last_entry != 'N/A':
            last_entry = last_entry[:19]  # 截取日期部分
        click.echo(f"{cat['name']:<20} {cat.get('count', 0):<10} {last_entry:<20}")
    
    click.echo(f"\n总计: {len(cats)} 个分类")


@categories.command('create')
@click.argument('name')
@click.option('--display-name', '-d', help='显示名称')
@click.option('--description', help='描述')
@click.pass_context
def create_category(ctx, name, display_name, description):
    """创建分类"""
    client = ctx.obj['client']
    
    try:
        category = client.create_category(name, display_name, description or "")
        click.echo(f"✓ 已创建分类: {category.name}")
    except ValueError as e:
        click.echo(f"✗ 错误: {e}", err=True)


@categories.command('show')
@click.argument('name')
@click.pass_context
def show_category(ctx, name):
    """显示分类详情"""
    client = ctx.obj['client']
    cat = client.get_category(name)
    
    if not cat:
        click.echo(f"✗ 分类不存在: {name}", err=True)
        return
    
    click.echo(f"分类: {cat['name']}")
    click.echo(f"显示名称: {cat.get('display_name', cat['name'])}")
    click.echo(f"条目数: {cat.get('count', 0)}")
    click.echo(f"描述: {cat.get('description', 'N/A')}")
    click.echo(f"创建时间: {cat.get('created_at', 'N/A')}")
    click.echo(f"最后更新: {cat.get('last_entry', 'N/A')}")
    
    # 列出条目
    entries = client.list_entries(category=name)
    if entries:
        click.echo(f"\n最近条目:")
        for entry in entries[:5]:
            click.echo(f"  - {entry['title'][:50]}")


# ===== 分析命令 =====

@cli.command()
@click.argument('category')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.pass_context
def analyze(ctx, category, output):
    """分析分类内容"""
    client = ctx.obj['client']
    
    click.echo(f"正在分析分类: {category}...")
    
    from ..ai.analyzer import CategoryAnalyzer
    analyzer = CategoryAnalyzer(client.config.storage.root_dir)
    
    report = analyzer.analyze(category)
    
    # 输出摘要
    click.echo(f"\n=== {category} 分析结果 ===")
    click.echo(f"总条目数: {report['statistics']['total_entries']}")
    click.echo(f"总任务数: {report['statistics']['total_tasks']}")
    click.echo(f"唯一标签: {report['statistics']['unique_tags']}")
    
    if report['statistics']['top_tags']:
        click.echo(f"\n热门标签:")
        for tag, count in report['statistics']['top_tags'][:5]:
            click.echo(f"  - {tag}: {count}")
    
    if output:
        # 生成 Markdown 报告
        md_content = analyzer.generate_summary_markdown(category)
        with open(output, 'w', encoding='utf-8') as f:
            f.write(md_content)
        click.echo(f"\n✓ 报告已保存: {output}")


# ===== 导出命令 =====

@cli.command()
@click.option('--format', '-f', 'fmt', type=click.Choice(['md', 'csv', 'json']), default='md', help='导出格式')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--category', '-c', help='按分类过滤')
@click.option('--tasks-only', is_flag=True, help='仅导出包含任务的条目')
@click.pass_context
def export(ctx, fmt, output, category, tasks_only):
    """导出数据"""
    client = ctx.obj['client']
    
    # 获取条目
    entries = client.list_entries(category=category, has_tasks=tasks_only if tasks_only else None)
    
    if not entries:
        click.echo("✗ 没有符合条件的条目")
        return
    
    click.echo(f"导出 {len(entries)} 条记录...")
    
    if fmt == 'csv':
        from ..exporters.csv_exporter import CSVExporter
        exporter = CSVExporter()
        if tasks_only:
            exporter.export_tasks(entries, output)
        else:
            exporter.export_entries(entries, output)
    
    elif fmt == 'json':
        from ..exporters.json_exporter import JSONExporter
        exporter = JSONExporter()
        exporter.export_entries(entries, output)
    
    else:  # markdown
        from ..exporters.markdown_exporter import MarkdownExporter
        exporter = MarkdownExporter()
        if tasks_only:
            exporter.export_todo_list(entries, output)
        else:
            exporter.export_entries(entries, output, title="导出文档")
    
    click.echo(f"✓ 已导出到: {output}")


# ===== 会话命令 =====

@cli.group()
def session():
    """会话管理"""
    pass


@session.command('start')
@click.option('--name', '-n', required=True, help='会话名称')
@click.option('--goal', '-g', help='会话目标')
@click.pass_context
def start_session(ctx, name, goal):
    """开始新会话"""
    cfg = ctx.obj['config']
    manager = SessionManager(cfg.session.capture_dir)
    
    session = manager.start_session(name=name, goal=goal)
    click.echo(f"✓ 会话已启动: {session.id}")
    click.echo(f"  名称: {session.name}")
    if session.goal:
        click.echo(f"  目标: {session.goal}")


@session.command('end')
@click.option('--summary', '-s', help='会话总结')
@click.pass_context
def end_session(ctx, summary):
    """结束当前会话"""
    cfg = ctx.obj['config']
    manager = SessionManager(cfg.session.capture_dir)
    
    session = manager.end_session(summary)
    if session:
        click.echo(f"✓ 会话已结束: {session.id}")
        click.echo(f"  持续时间: {int(session.duration)} 秒")
        click.echo(f"  对话轮次: {len(session.turns)}")
    else:
        click.echo("✗ 没有活动的会话")


@session.command('list')
@click.pass_context
def list_sessions(ctx):
    """列出会话"""
    cfg = ctx.obj['config']
    manager = SessionManager(cfg.session.capture_dir)
    
    sessions = manager.list_sessions()
    
    if not sessions:
        click.echo("暂无会话记录")
        return
    
    click.echo(f"{'会话 ID':<30} {'名称':<30} {'轮次':<8} {'时间':<20}")
    click.echo("-" * 88)
    
    for s in sessions:
        name = s['name'][:28] if len(s['name']) > 28 else s['name']
        click.echo(f"{s['id']:<30} {name:<30} {s['turn_count']:<8} {s['start_time'][:19]:<20}")


# ===== 初始化命令 =====

@cli.command()
@click.option('--root-dir', '-r', default='./ideas', help='数据根目录')
def init(root_dir):
    """初始化项目"""
    cfg = Config()
    cfg.init_project(root_dir)
    
    click.echo(f"✓ 项目已初始化")
    click.echo(f"  数据目录: {root_dir}")
    click.echo(f"  配置文件: {root_dir}/.capture/config.yaml")


# ===== 统计命令 =====

@cli.command()
@click.pass_context
def stats(ctx):
    """显示统计信息"""
    client = ctx.obj['client']
    stats = client.get_stats()
    
    click.echo("=== Capture TUI 统计 ===")
    click.echo(f"总条目数: {stats.get('total_entries', 0)}")
    click.echo(f"总分类数: {stats.get('total_categories', 0)}")
    click.echo(f"待办任务: {stats.get('pending_tasks', 0)}")


if __name__ == '__main__':
    cli()
