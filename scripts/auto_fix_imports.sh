#!/bin/bash
# 一键修复 Python 包导入路径脚本，适配AI Chat项目
# 用于将 from models/ from models. 批量修正为 from backend.models/ from backend.models.

set -e

WORKDIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$WORKDIR"

echo "[auto-fix] 正在修复 backend/utils 及子目录下的包导入..."

find backend/utils -type f -name "*.py" | while read file; do
  if grep -qE "from models(\.| |$)" "$file"; then
    echo "[auto-fix] 修复 $file ..."
    sed -i 's/from models\./from backend.models./g' "$file"
    sed -i 's/from models /from backend.models /g' "$file"
  fi
  if grep -qE "import models(\.| |$)" "$file"; then
    echo "[auto-fix] 修复 $file ..."
    sed -i 's/import models\./import backend.models./g' "$file"
    sed -i 's/import models /import backend.models /g' "$file"
  fi
  # 可扩展：如需修正其他裸包名，也可在此添加
  # 例如：sed -i 's/from utils\./from backend.utils./g' "$file"
done

echo "[auto-fix] 修复完成！如有需要请重启服务。" 