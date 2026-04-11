#!/usr/bin/env python3
"""Capture TUI - Typer CLI 版本

使用 Typer 框架的现代化 CLI 实现。
"""

import typer
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from capture_tui.core.client import CaptureClient
from capture_tui.config import Config
from capture_tui.session.manager import SessionManager

# 创建主应用
app = typer.Typer(
    name="capture",
    help="Capture TUI - 终端输入捕获与管理工具",
    rich_markup_mode="rich",
)

# 创建子命令组
categories_app = typer.Typer(help="分类管理")
session_app = typer.Typer(help="会话管理")
tutorial_app = typer.Typer(help="Executable tutorial generator")

app.add_typer(categories_app, name="categories")
app.add_typer(session_app, name="session")
app.add_typer(tutorial_app, name="tutorial")


# 全局选项回调
@app.callback()
def global_options(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="配置文件路径"
    ),
    root_dir: Optional[Path] = typer.Option(
        None, "--root-dir", "-r", help="数据根目录"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="启用详细输出"
    ),
):
    """全局选项"""
    ctx.ensure_object(dict)
    
    cfg = Config.load(str(config) if config else None)
    if root_dir:
        cfg.storage.root_dir = str(root_dir)
    
    ctx.obj["config"] = cfg
    ctx.obj["client"] = CaptureClient(cfg)
    ctx.obj["verbose"] = verbose


@app.command()
def init(
    ctx: typer.Context,
    root_dir: Path = typer.Option(
        "./ideas", "--root-dir", "-r", help="数据根目录"
    ),
    force: bool = typer.Option(
        False, "--force", help="强制重新初始化"
    ),
):
    """初始化项目"""
    cfg = Config()
    cfg.storage.root_dir = str(root_dir)
    
    # 检查是否已存在
    config_path = Path(root_dir) / ".capture" / "config.yaml"
    if config_path.exists() and not force:
        typer.echo("⚠️ 项目已存在。使用 --force 强制重新初始化。", err=True)
        raise typer.Exit(1)
    
    cfg.init_project(str(root_dir))
    typer.echo(f"✅ 项目已初始化: {root_dir}")


@app.command()
def add(
    ctx: typer.Context,
    content: Optional[str] = typer.Argument(
        None, help="想法内容（省略则进入交互模式）"
    ),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="分类名称"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tags", "-t", help="标签列表"
    ),
    title: Optional[str] = typer.Option(
        None, "--title", help="指定标题"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", "-p", help="优先级: P0, P1, P2"
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="从文件读取内容"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="交互式输入"
    ),
):
    """添加想法/任务"""
    client = ctx.obj["client"]
    
    try:
        if file:
            # 从文件添加
            entry = client.add_from_file(
                str(file),
                category=category,
                tags=tags
            )
        elif content:
            # 直接添加
            entry = client.add_idea(
                content=content,
                category=category,
                tags=tags,
                title=title,
                priority=priority
            )
        else:
            # 交互式输入
            typer.echo("请输入内容 (Ctrl+D 结束):")
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            if not lines:
                typer.echo("❌ 未输入内容", err=True)
                raise typer.Exit(1)
            
            content = "\n".join(lines)
            entry = client.add_idea(
                content=content,
                category=category,
                tags=tags,
                title=title,
                priority=priority
            )
        
        typer.echo(f"✅ 已添加: {entry.id}")
        typer.echo(f"   分类: {entry.category}")
        typer.echo(f"   标题: {entry.title}")
        if entry.tasks:
            typer.echo(f"   任务: {len(entry.tasks)} 个")
    
    except ValueError as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(1)


@categories_app.command("list")
def categories_list(
    ctx: typer.Context,
):
    """列出所有分类"""
    client = ctx.obj["client"]
    cats = client.list_categories()
    
    if not cats:
        typer.echo("暂无分类")
        return
    
    # 使用 rich table 输出
    from rich.table import Table
    from rich.console import Console
    
    console = Console()
    table = Table(title="分类列表")
    table.add_column("分类名称", style="cyan")
    table.add_column("条目数", justify="right", style="green")
    table.add_column("最后更新", style="yellow")
    
    for cat in cats:
        last = cat.get("last_entry", "N/A")[:19] if cat.get("last_entry") else "N/A"
        table.add_row(
            cat["name"],
            str(cat.get("count", 0)),
            last
        )
    
    console.print(table)
    typer.echo(f"\n总计: {len(cats)} 个分类")


@categories_app.command("create")
def categories_create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="分类名称"),
    display_name: Optional[str] = typer.Option(
        None, "--display-name", "-d", help="显示名称"
    ),
    description: Optional[str] = typer.Option(
        "", "--description", help="描述"
    ),
):
    """创建分类"""
    client = ctx.obj["client"]
    
    try:
        category = client.create_category(name, display_name, description)
        typer.echo(f"✅ 已创建分类: {category.name}")
    except ValueError as e:
        typer.echo(f"❌ 错误: {e}", err=True)
        raise typer.Exit(1)


@categories_app.command("show")
def categories_show(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="分类名称"),
):
    """显示分类详情"""
    client = ctx.obj["client"]
    cat = client.get_category(name)
    
    if not cat:
        typer.echo(f"❌ 分类不存在: {name}", err=True)
        raise typer.Exit(1)
    
    from rich.panel import Panel
    from rich.console import Console
    
    console = Console()
    
    info = f"""[bold]名称:[/] {cat['name']}
[bold]显示名称:[/] {cat.get('display_name', cat['name'])}
[bold]条目数:[/] {cat.get('count', 0)}
[bold]描述:[/] {cat.get('description', 'N/A')}
[bold]创建时间:[/] {cat.get('created_at', 'N/A')[:19]}
[bold]最后更新:[/] {cat.get('last_entry', 'N/A')[:19] if cat.get('last_entry') else 'N/A'}"""
    
    console.print(Panel(info, title=f"分类: {name}"))


@app.command()
def analyze(
    ctx: typer.Context,
    category: str = typer.Argument(..., help="分类名称"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="输出文件路径"
    ),
    format: str = typer.Option(
        "markdown", "--format", "-f", help="输出格式: markdown, json"
    ),
):
    """分析分类内容"""
    client = ctx.obj["client"]
    
    typer.echo(f"正在分析分类: {category}...")
    
    from capture_tui.ai.analyzer import CategoryAnalyzer
    analyzer = CategoryAnalyzer(client.config.storage.root_dir)
    
    report = analyzer.analyze(category)
    
    # 输出摘要
    typer.echo(f"\n📊 {category} 分析结果:")
    typer.echo(f"   总条目数: {report['statistics']['total_entries']}")
    typer.echo(f"   总任务数: {report['statistics']['total_tasks']}")
    typer.echo(f"   唯一标签: {report['statistics']['unique_tags']}")
    
    if report['statistics']['top_tags']:
        typer.echo(f"\n🏷️ 热门标签:")
        for tag, count in report['statistics']['top_tags'][:5]:
            typer.echo(f"   - {tag}: {count}")
    
    if output:
        md_content = analyzer.generate_summary_markdown(category)
        output.write_text(md_content, encoding='utf-8')
        typer.echo(f"\n✅ 报告已保存: {output}")


@app.command()
def export(
    ctx: typer.Context,
    format: str = typer.Option(
        "markdown", "--format", "-f", help="导出格式: md, csv, json"
    ),
    output: Path = typer.Option(
        ..., "--output", "-o", help="输出文件路径"
    ),
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="按分类过滤"
    ),
    tasks_only: bool = typer.Option(
        False, "--tasks-only", help="仅导出包含任务的条目"
    ),
):
    """导出数据"""
    client = ctx.obj["client"]
    
    entries = client.list_entries(
        category=category,
        has_tasks=tasks_only if tasks_only else None
    )
    
    if not entries:
        typer.echo("❌ 没有符合条件的条目", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"导出 {len(entries)} 条记录...")
    
    if format == "csv":
        from capture_tui.exporters.csv_exporter import CSVExporter
        exporter = CSVExporter()
        if tasks_only:
            exporter.export_tasks(entries, str(output))
        else:
            exporter.export_entries(entries, str(output))
    elif format == "json":
        from capture_tui.exporters.json_exporter import JSONExporter
        exporter = JSONExporter()
        exporter.export_entries(entries, str(output))
    else:
        from capture_tui.exporters.markdown_exporter import MarkdownExporter
        exporter = MarkdownExporter()
        if tasks_only:
            exporter.export_todo_list(entries, str(output))
        else:
            exporter.export_entries(entries, str(output))
    
    typer.echo(f"✅ 已导出到: {output}")


@session_app.command("start")
def session_start(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="会话名称"),
    goal: Optional[str] = typer.Option(
        None, "--goal", "-g", help="会话目标"
    ),
):
    """开始新会话"""
    cfg = ctx.obj["config"]
    manager = SessionManager(cfg.session.capture_dir)
    
    session = manager.start_session(name=name, goal=goal)
    typer.echo(f"✅ 会话已启动: {session.id}")
    typer.echo(f"   名称: {session.name}")
    if session.goal:
        typer.echo(f"   目标: {session.goal}")


@session_app.command("end")
def session_end(
    ctx: typer.Context,
    summary: Optional[str] = typer.Option(
        None, "--summary", "-s", help="会话总结"
    ),
):
    """结束当前会话"""
    cfg = ctx.obj["config"]
    manager = SessionManager(cfg.session.capture_dir)
    
    session = manager.end_session(summary)
    if session:
        typer.echo(f"✅ 会话已结束: {session.id}")
        typer.echo(f"   持续时间: {int(session.duration)} 秒")
        typer.echo(f"   对话轮次: {len(session.turns)}")
    else:
        typer.echo("❌ 没有活动的会话", err=True)
        raise typer.Exit(1)


@session_app.command("list")
def session_list(
    ctx: typer.Context,
):
    """列出会话"""
    cfg = ctx.obj["config"]
    manager = SessionManager(cfg.session.capture_dir)
    
    sessions = manager.list_sessions()
    
    if not sessions:
        typer.echo("暂无会话记录")
        return
    
    from rich.table import Table
    from rich.console import Console
    
    console = Console()
    table = Table(title="会话列表")
    table.add_column("会话 ID", style="cyan", overflow="fold")
    table.add_column("名称", style="green")
    table.add_column("轮次", justify="right")
    table.add_column("时间", style="yellow")
    
    for s in sessions[:20]:  # 最多显示20条
        table.add_row(
            s['id'],
            s['name'][:30],
            str(s['turn_count']),
            s['start_time'][:19]
        )
    
    console.print(table)


@app.command()
def stats(
    ctx: typer.Context,
):
    """显示统计信息"""
    client = ctx.obj["client"]
    stats = client.get_stats()
    
    from rich.panel import Panel
    from rich.console import Console
    
    console = Console()
    
    info = f"""[bold]总条目数:[/] {stats.get('total_entries', 0)}
[bold]总分类数:[/] {stats.get('total_categories', 0)}
[bold]待办任务:[/] {stats.get('pending_tasks', 0)}"""
    
    console.print(Panel(info, title="Capture TUI 统计"))


if __name__ == "__main__":
    app()


# --- Tutorial subcommands ---

@tutorial_app.command("generate")
def tutorial_generate(
    ctx: typer.Context,
    source: str = typer.Argument(..., help="URL, file path, or text content"),
    template: str = typer.Option("md_script", "--template", "-t",
        help="Output template: md_script, md_only, script_only"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory"),
    review: bool = typer.Option(
        False, "--review", help="Enable human review before final output"),
    no_claude: bool = typer.Option(
        False, "--no-claude", help="Disable Claude-assisted stages"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed stage progress"),
):
    """Generate an executable tutorial from a URL, file, or text."""
    from capture_tui.tutorial.generator import TutorialGenerator

    cfg = ctx.obj["config"]
    gen = TutorialGenerator(cfg.tutorial)

    try:
        tutorial = gen.generate(
            source=source,
            template=template,
            output_dir=str(output_dir) if output_dir else None,
            review=review,
            claude_enabled=not no_claude,
        )

        typer.echo(f"Generated tutorial: {tutorial.title}")
        typer.echo(f"  ID: {tutorial.id}")
        typer.echo(f"  Slug: {tutorial.slug}")
        typer.echo(f"  Code blocks: {len(tutorial.code_blocks)}")
        typer.echo(f"  Scripts: {len(tutorial.scripts)}")
        if tutorial.source_url:
            typer.echo(f"  Source: {tutorial.source_url}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@tutorial_app.command("batch")
def tutorial_batch(
    ctx: typer.Context,
    batch_file: Path = typer.Argument(...,
        help="JSON file with sources to process"),
    template: str = typer.Option("md_script", "--template", "-t"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output base directory"),
    workers: int = typer.Option(4, "--workers", "-w",
        help="Number of parallel workers"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be processed"),
):
    """Batch generate tutorials from a JSON file."""
    import json
    from capture_tui.pipeline.queue import Job
    from capture_tui.tutorial.generator import TutorialGenerator

    cfg = ctx.obj["config"]

    with open(batch_file, "r", encoding="utf-8") as f:
        sources = json.load(f)

    if dry_run:
        typer.echo(f"Would process {len(sources)} sources:")
        for s in sources:
            src = s if isinstance(s, str) else s.get("source", "")
            typer.echo(f"  - {src[:80]}")
        return

    gen = TutorialGenerator(cfg.tutorial)
    result = gen.generate_batch(
        sources=sources,
        template=template,
        output_dir=str(output_dir) if output_dir else None,
        max_workers=workers,
    )

    typer.echo(f"Batch complete: {result.succeeded}/{result.total} succeeded")
    if result.errors:
        for err in result.errors:
            typer.echo(f"  Error: {err}", err=True)


@tutorial_app.command("queue")
def tutorial_queue(
    ctx: typer.Context,
    action: str = typer.Argument("status",
        help="Queue action: status, retry, clear"),
):
    """Manage the tutorial job queue."""
    from capture_tui.pipeline.queue import JobQueue, JobStatus

    cfg = ctx.obj["config"]
    queue_dir = cfg.tutorial.queue_dir or f"{cfg.tutorial.output_dir}/.tutorial"
    queue = JobQueue(queue_dir)

    if action == "status":
        jobs = queue.list_jobs()
        if not jobs:
            typer.echo("Queue is empty")
            return

        from rich.table import Table
        from rich.console import Console
        console = Console()
        table = Table(title="Tutorial Job Queue")
        table.add_column("ID", style="cyan", overflow="fold")
        table.add_column("Status", style="green")
        table.add_column("Source", style="yellow", overflow="fold")
        table.add_column("Created", style="dim")

        for j in jobs[:20]:
            table.add_row(
                j.id[:20],
                j.status,
                j.input_ref[:50],
                j.created_at[:19],
            )
        console.print(table)

    elif action == "clear":
        queue.clear()
        typer.echo("Cleared completed/failed jobs")

    else:
        typer.echo(f"Unknown action: {action}", err=True)
        raise typer.Exit(1)


@tutorial_app.command("templates")
def tutorial_templates(
    ctx: typer.Context,
    action: str = typer.Argument("list",
        help="Template action: list, show"),
    name: Optional[str] = typer.Argument(None, help="Template name"),
):
    """List or show tutorial templates."""
    from capture_tui.tutorial.templates import TEMPLATES

    if action == "list":
        for tname, cls in TEMPLATES.items():
            t = cls()
            typer.echo(f"  {tname}: outputs {t.output_files}")
    elif action == "show":
        if not name:
            typer.echo("Specify a template name", err=True)
            raise typer.Exit(1)
        from capture_tui.tutorial.templates import get_template
        t = get_template(name)
        typer.echo(f"Template: {t.name}")
        typer.echo(f"Output files: {t.output_files}")
    else:
        typer.echo(f"Unknown action: {action}", err=True)
        raise typer.Exit(1)
