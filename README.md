# PMD Apex AST Analyzer

このツールは、PMDを使用してApexコードを解析し、抽象構文木（AST）を出力します。

## 前提条件

- **Java**: PMDを実行するにはJavaが必要です（Java 8以降）
- **Python**: Python 3.6以降

## 主要な関数

### 1. `get_pmd_command()`
環境に応じて適切なPMDコマンドのパスを返します。

```python
pmd_cmd = get_pmd_command()
# Windows: D:\workspace\project018_pmd\pmd_analyzer\analyzer\bin\pmd.bat
# Unix: /workspace/project018_pmd/pmd_analyzer/analyzer/bin/pmd
```

### 2. `check_pmd_environment()`
PMD実行環境の完全チェックを行います。

```python
env_check = check_pmd_environment()
print(f"環境準備完了: {env_check['ready']}")
print(f"Java利用可能: {env_check['java_available']}")
```

**チェック項目:**
- OS種別
- PMDコマンドファイルの存在
- libディレクトリの存在
- confディレクトリの存在
- Java実行環境の可用性
- Javaバージョン

### 3. `find_apex_files(directory)`
指定されたディレクトリ内のすべてのApexファイル（.cls）を再帰的に検索します。

```python
classes_dir = "project/dreamhouse-lwc/force-app/main/default/classes"
apex_files = find_apex_files(classes_dir)
print(f"検出されたファイル数: {len(apex_files)}")
```

### 4. `parse_apex_ast(apex_file_or_dir, output_file, format)`
PMD AST解析コマンドを構築します（実行はしません）。

```python
result = parse_apex_ast(
    "SampleDataController.cls",
    "output/ast/SampleDataController_ast.txt",
    format="text"
)
print(f"コマンド: {result['command']}")
```

**パラメータ:**
- `apex_file_or_dir`: 解析対象のファイルまたはディレクトリ
- `output_file`: 出力ファイルパス（Noneの場合は標準出力）
- `format`: 出力フォーマット（"text" または "xml"）

### 5. `execute_pmd_ast(apex_file_or_dir, output_file, format)`
PMDを実際に実行してASTを生成します。

```python
result = execute_pmd_ast(
    "SampleDataController.cls",
    "output/ast/SampleDataController_ast.txt",
    format="text"
)

if result["success"]:
    print("AST解析成功!")
    print(result["output"])
else:
    print(f"エラー: {result['error']}")
```

### 6. `parse_apex_classes_directory(classes_dir, output_dir, format, execute)`
classesディレクトリ内のすべてのApexファイルを一括処理します。

```python
# コマンドの構築のみ（実行なし）
result = parse_apex_classes_directory(
    "project/dreamhouse-lwc/force-app/main/default/classes",
    "output/ast",
    format="text",
    execute=False
)

# 実際に実行
result = parse_apex_classes_directory(
    "project/dreamhouse-lwc/force-app/main/default/classes",
    "output/ast",
    format="text",
    execute=True
)

print(f"処理ファイル数: {result['total_files']}")
print(f"成功: {len(result['processed_files'])}")
print(f"エラー: {len(result['errors'])}")
```

**パラメータ:**
- `classes_dir`: classesディレクトリのパス
- `output_dir`: AST出力先ディレクトリ
- `format`: 出力フォーマット（"text" または "xml"）
- `execute`: 実際にPMDを実行するか（デフォルト: False）

## 使用例

### 例1: 環境チェック

```python
from pmd_check import check_pmd_environment

env = check_pmd_environment()
if env["ready"]:
    print("PMD環境は準備完了です")
else:
    if not env["java_available"]:
        print("エラー: Javaがインストールされていません")
    if not env["command_exists"]:
        print("エラー: PMDコマンドが見つかりません")
```

### 例2: 単一ファイルのAST解析

```python
from pmd_check import execute_pmd_ast

result = execute_pmd_ast(
    apex_file_or_dir="project/dreamhouse-lwc/force-app/main/default/classes/SampleDataController.cls",
    output_file="output/SampleDataController_ast.txt",
    format="text"
)

if result["success"]:
    print(f"AST出力完了: {result['output_file']}")
```

### 例3: 複数ファイルの一括処理

```python
from pmd_check import parse_apex_classes_directory

# コマンド生成のみ（テスト用）
result = parse_apex_classes_directory(
    classes_dir="project/dreamhouse-lwc/force-app/main/default/classes",
    output_dir="output/ast",
    format="text",
    execute=False  # コマンドを生成するが実行しない
)

print(f"処理予定ファイル数: {result['total_files']}")
for file_info in result['processed_files']:
    print(f"ファイル: {file_info['file']}")
    print(f"コマンド: {file_info['command']}")
    print(f"出力先: {file_info['output']}")
    print()

# 実際に実行
result = parse_apex_classes_directory(
    classes_dir="project/dreamhouse-lwc/force-app/main/default/classes",
    output_dir="output/ast",
    format="xml",  # XML形式で出力
    execute=True   # 実際に実行
)

if result["success"]:
    print(f"✓ 全ファイルの処理が完了しました")
else:
    print(f"✗ {len(result['errors'])}個のエラーが発生しました")
    for error in result['errors']:
        print(f"  - {error['file']}: {error['error']}")
```

### 例4: 特定のディレクトリからApexファイルを検索

```python
from pmd_check import find_apex_files

apex_files = find_apex_files("project/dreamhouse-lwc")
print(f"検出されたApexファイル: {len(apex_files)}")
for apex_file in apex_files:
    print(f"  - {apex_file}")
```

## 出力フォーマット

### テキスト形式 (format="text")
```
└── ASTRoot
    ├── UserClass
    │   ├── ModifierNode
    │   ├── Identifier: SampleDataController
    │   └── ClassBody
    │       └── Method
    │           ├── ModifierNode
    │           ├── Identifier: importSampleData
    │           └── BlockStatement
    ...
```

### XML形式 (format="xml")
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ASTRoot>
  <UserClass>
    <ModifierNode>public</ModifierNode>
    <Identifier>SampleDataController</Identifier>
    <ClassBody>
      <Method>
        <Identifier>importSampleData</Identifier>
        ...
      </Method>
    </ClassBody>
  </UserClass>
</ASTRoot>
```

## トラブルシューティング

### Javaが見つからない場合

```bash
# Javaがインストールされているか確認
java -version

# Javaがインストールされていない場合はインストール
# Windows: https://www.oracle.com/java/technologies/downloads/
# または OpenJDK: https://adoptium.net/
```

### PMDコマンドが見つからない場合

PMDが正しく配置されているか確認：
```
pmd_analyzer/
  ├── analyzer/
  │   ├── bin/
  │   │   ├── pmd (Unix)
  │   │   └── pmd.bat (Windows)
  │   ├── lib/
  │   └── conf/
  └── pmd_check.py
```

## PMDコマンドライン例

以下は、`parse_apex_ast`や`execute_pmd_ast`が生成するコマンドの例です：

```bash
# Windows
D:\workspace\project018_pmd\pmd_analyzer\analyzer\bin\pmd.bat ast-dump --language apex --file SampleDataController.cls

# Unix/Linux/macOS
/workspace/project018_pmd/pmd_analyzer/analyzer/bin/pmd ast-dump --language apex --file SampleDataController.cls

# 複数ファイル
pmd.bat ast-dump --language apex --file File1.cls File2.cls File3.cls

# XML形式で出力
pmd.bat ast-dump --language apex --format xml --file SampleDataController.cls
```

## 注意事項

1. **Java必須**: PMDの実行にはJavaが必要です
2. **ファイルパス**: Windowsでは絶対パスにバックスラッシュ (`\`) が含まれます
3. **エンコーディング**: 出力はUTF-8エンコーディングで保存されます
4. **大きなプロジェクト**: 多数のファイルを処理する場合は時間がかかる可能性があります

## ライセンス

このツールはPMD (BSD-style license) を使用しています。
