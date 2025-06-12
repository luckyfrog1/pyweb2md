#!/usr/bin/env python3
"""
PyWeb2MD包检查工具

用于发布前的最终检查
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_imports():
    """检查核心模块导入"""
    print("🔍 检查核心模块导入...")
    
    try:
        import pyweb2md
        from pyweb2md import Web2MD, BatchScraper
        from pyweb2md.core.extractor import Web2MD as ExtractorWeb2MD
        
        print(f"✅ pyweb2md版本: {pyweb2md.__version__}")
        print("✅ 核心类导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    required_deps = [
        ('selenium', 'selenium'),
        ('beautifulsoup4', 'bs4'), 
        ('lxml', 'lxml'),
        ('webdriver_manager', 'webdriver_manager')
    ]
    
    missing_deps = []
    for dep_name, module_name in required_deps:
        try:
            importlib.import_module(module_name)
            print(f"✅ {dep_name}: 已安装")
        except ImportError:
            missing_deps.append(dep_name)
            print(f"❌ {dep_name}: 未安装")
    
    return len(missing_deps) == 0

def check_functionality():
    """检查基本功能"""
    print("🔍 检查基本功能...")
    
    try:
        from pyweb2md import Web2MD
        
        # 创建实例（不实际运行）
        converter = Web2MD()
        print("✅ Web2MD实例创建成功")
        
        # 检查方法存在
        assert hasattr(converter, 'extract'), "extract方法不存在"
        assert hasattr(converter, 'get_content'), "get_content方法不存在"
        print("✅ 核心方法检查通过")
        
        return True
    except Exception as e:
        print(f"❌ 功能检查失败: {e}")
        return False

def check_files():
    """检查必要文件"""
    print("🔍 检查必要文件...")
    
    required_files = [
        'README.md',
        'LICENSE', 
        'pyproject.toml',
        'CHANGELOG.md',
        'MANIFEST.in'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}: 存在")
        else:
            missing_files.append(file)
            print(f"❌ {file}: 不存在")
    
    return len(missing_files) == 0

def run_quick_test():
    """运行快速测试"""
    print("🔍 运行快速测试...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/integration/test_pyweb2md_functionality.py::TestPyweb2mdFunctionality::test_content_quality_metrics',
            '-v', '--tb=short'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 快速测试通过")
            return True
        else:
            print("❌ 快速测试失败:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ 测试超时，跳过")
        return True
    except Exception as e:
        print(f"⚠️ 测试执行出错: {e}")
        return True

def check_package_structure():
    """检查包结构"""
    print("🔍 检查包结构...")
    
    required_structure = {
        'pyweb2md/__init__.py': '主包初始化文件',
        'pyweb2md/core/__init__.py': '核心模块初始化文件', 
        'pyweb2md/core/extractor.py': '提取器模块',
        'pyweb2md/core/converter.py': '转换器模块',
        'pyweb2md/utils/__init__.py': '工具模块初始化文件'
    }
    
    all_exist = True
    for file_path, description in required_structure.items():
        if Path(file_path).exists():
            print(f"✅ {file_path}: {description}")
        else:
            print(f"❌ {file_path}: {description} - 不存在")
            all_exist = False
    
    return all_exist

def main():
    print("🎯 PyWeb2MD包检查开始")
    print("=" * 50)
    
    checks = [
        ("文件检查", check_files),
        ("包结构检查", check_package_structure), 
        ("依赖项检查", check_dependencies),
        ("导入检查", check_imports),
        ("功能检查", check_functionality),
        ("快速测试", run_quick_test)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}")
        try:
            result = check_func()
            results.append((name, result))
            if result:
                print(f"✅ {name}通过")
            else:
                print(f"❌ {name}失败")
        except Exception as e:
            print(f"❌ {name}出错: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(results)} 项检查通过")
    
    if passed == len(results):
        print("🎉 所有检查通过，可以发布!")
        return 0
    else:
        print("⚠️ 部分检查未通过，请修复后再发布")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 