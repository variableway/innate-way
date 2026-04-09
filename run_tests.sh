#!/bin/bash
# 运行测试脚本

echo "=== Capture TUI 测试运行器 ==="

# 检查是否安装了 pytest
if ! command -v pytest &> /dev/null; then
    echo "正在安装 pytest..."
    pip install pytest pytest-cov pytest-mock
fi

# 运行单元测试
echo ""
echo "=== 运行单元测试 ==="
pytest tests/unit -v --cov=capture_tui --cov-report=term-missing

# 运行集成测试
echo ""
echo "=== 运行集成测试 ==="
pytest tests/integration -v

# 生成覆盖率报告
echo ""
echo "=== 生成覆盖率报告 ==="
pytest --cov=capture_tui --cov-report=html --cov-report=term

echo ""
echo "=== 测试完成 ==="
