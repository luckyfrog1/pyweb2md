#!/usr/bin/env python3
"""
PyWeb2MD PyPI发布自动化脚本

使用方法:
  python scripts/build_and_upload.py --test    # 上传到TestPyPI
  python scripts/build_and_upload.py --prod    # 上传到PyPI
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """执行命令并输出结果"""
    print(f"🔄 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"❌ 命令执行失败: {cmd}")
        sys.exit(1)
    
    return result

def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  删除目录: {path}")
            else:
                path.unlink()
                print(f"  删除文件: {path}")

def check_version():
    """检查版本一致性"""
    print("🔍 检查版本一致性...")
    
    # 检查pyproject.toml版本
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        pyproject_content = f.read()
        
    # 检查__init__.py版本
    sys.path.insert(0, 'pyweb2md')
    import pyweb2md
    
    print(f"  pyproject.toml: 需要手动确认")
    print(f"  __init__.py: {pyweb2md.__version__}")
    
    return pyweb2md.__version__

def run_tests():
    """运行测试套件"""
    print("🧪 运行测试套件...")
    
    # 运行核心测试
    result = run_command("python -m pytest tests/integration/test_pyweb2md_functionality.py -v", check=False)
    if result.returncode != 0:
        print("❌ 功能测试失败")
        return False
    
    # 运行简单网站测试
    result = run_command("python -m pytest tests/integration/test_pyweb2md_simple_sites.py -v", check=False)
    if result.returncode != 0:
        print("⚠️ 简单网站测试失败，但可以继续")
    
    print("✅ 核心测试通过")
    return True

def build_package():
    """构建包"""
    print("📦 构建包...")
    
    # 安装构建依赖
    run_command("pip install --upgrade build twine")
    
    # 构建包
    run_command("python -m build")
    
    # 检查包
    result = run_command("python -m twine check dist/*", check=False)
    if result.returncode != 0:
        print("❌ 包检查失败")
        return False
    
    print("✅ 包构建成功")
    return True

def upload_package(test_mode=True):
    """上传包"""
    if test_mode:
        print("🚀 上传到TestPyPI...")
        repository_url = "https://test.pypi.org/legacy/"
        index_url = "https://test.pypi.org/simple/"
        print("注意: 需要设置TESTPYPI_TOKEN环境变量")
        
        # 上传到TestPyPI
        run_command("python -m twine upload --repository testpypi dist/*")
        
        print(f"✅ 上传到TestPyPI成功!")
        print(f"📖 查看: https://test.pypi.org/project/pyweb2md/")
        print(f"🔧 测试安装: pip install --index-url {index_url} pyweb2md")
        
    else:
        print("🚀 上传到PyPI...")
        print("注意: 需要设置PYPI_TOKEN环境变量")
        
        # 确认上传
        confirm = input("⚠️ 确认上传到正式PyPI? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 用户取消上传")
            return False
        
        # 上传到PyPI
        run_command("python -m twine upload dist/*")
        
        print(f"✅ 上传到PyPI成功!")
        print(f"📖 查看: https://pypi.org/project/pyweb2md/")
        print(f"🔧 安装: pip install pyweb2md")

def main():
    parser = argparse.ArgumentParser(description='PyWeb2MD PyPI发布工具')
    parser.add_argument('--test', action='store_true', help='上传到TestPyPI')
    parser.add_argument('--prod', action='store_true', help='上传到PyPI')
    parser.add_argument('--skip-tests', action='store_true', help='跳过测试')
    parser.add_argument('--skip-clean', action='store_true', help='跳过清理')
    
    args = parser.parse_args()
    
    if not (args.test or args.prod):
        print("❌ 请指定 --test 或 --prod")
        sys.exit(1)
    
    print("🎯 PyWeb2MD PyPI发布流程开始")
    print("=" * 50)
    
    try:
        # 1. 清理构建文件
        if not args.skip_clean:
            clean_build()
        
        # 2. 检查版本
        version = check_version()
        print(f"📋 当前版本: {version}")
        
        # 3. 运行测试
        if not args.skip_tests:
            if not run_tests():
                print("❌ 测试失败，停止发布")
                sys.exit(1)
        
        # 4. 构建包
        if not build_package():
            print("❌ 构建失败，停止发布")
            sys.exit(1)
        
        # 5. 上传包
        upload_package(test_mode=args.test)
        
        print("=" * 50)
        print("🎉 发布流程完成!")
        
        if args.test:
            print("📝 后续步骤:")
            print("1. 测试TestPyPI上的包")
            print("2. 确认无误后运行: python scripts/build_and_upload.py --prod")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断发布流程")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发布过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 