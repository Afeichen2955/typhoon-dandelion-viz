#!/bin/bash
echo "🌪️ 台风蒲公英项目环境设置"
echo "=========================="

# 检查当前目录
if [ ! -f "typhoon_dandelion.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 删除旧的虚拟环境（如果存在）
if [ -d "typhoon_env" ]; then
    echo "🗑️ 删除旧的虚拟环境..."
    rm -rf typhoon_env
fi

# 创建新的虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv typhoon_env

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source typhoon_env/bin/activate

# 验证虚拟环境
echo "✅ 当前Python路径: $(which python)"
echo "✅ 当前Python版本: $(python --version)"

# 升级pip
echo "⬆️ 升级pip..."
python -m pip install --upgrade pip

# 安装依赖包
echo "📚 安装核心依赖..."
python -m pip install matplotlib pandas numpy requests Pillow PyYAML

# 验证安装
echo "🔍 验证安装..."
python -c "
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import requests
    from PIL import Image
    import yaml
    print('✅ 所有模块导入成功!')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
"

# 创建VS Code配置
echo "⚙️ 配置VS Code..."
mkdir -p .vscode

# 获取虚拟环境的完整路径
VENV_PATH=$(pwd)/typhoon_env/bin/python

cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "${VENV_PATH}",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.formatting.provider": "autopep8",
    "editor.formatOnSave": false,
    "files.encoding": "utf8",
    "editor.tabSize": 4,
    "editor.insertSpaces": true
}
EOF

echo "✅ VS Code配置已创建"
echo "📍 Python解释器路径: ${VENV_PATH}"

# 创建激活脚本
cat > activate_env.sh << 'EOF'
#!/bin/bash
echo "🔄 激活台风蒲公英项目环境..."
source typhoon_env/bin/activate
echo "✅ 环境已激活"
echo "💡 现在可以运行: python typhoon_dandelion.py"
EOF

chmod +x activate_env.sh

echo ""
echo "🎉 设置完成！"
echo "💡 使用方法："
echo "   1. 运行: source activate_env.sh"
echo "   2. 或者: source typhoon_env/bin/activate"
echo "   3. 然后: python typhoon_dandelion.py"
echo ""
echo "📝 VS Code用户："
echo "   1. 重启VS Code"
echo "   2. 按 Cmd+Shift+P"
echo "   3. 选择 'Python: Select Interpreter'"
echo "   4. 选择 ./typhoon_env/bin/python"