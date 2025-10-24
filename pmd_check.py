import os
import platform
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional


def get_pmd_command():
    """
    環境に応じて適切なPMDコマンドを判定する関数
    
    Returns:
        str: PMDコマンドのパス（pmd.batまたはpmd）
    """
    # スクリプトの現在のディレクトリを取得
    current_dir = Path(__file__).parent
    analyzer_dir = current_dir / "analyzer" / "bin"
    
    # OS判定
    system = platform.system()
    
    if system == "Windows":
        pmd_cmd = analyzer_dir / "pmd.bat"
    else:
        # Unix系 (Linux, macOS, etc.)
        pmd_cmd = analyzer_dir / "pmd"
    
    return str(pmd_cmd)


def check_pmd_environment():
    """
    PMD環境をチェックし、必要なファイルが存在するかを確認する関数
    
    Returns:
        dict: 環境チェック結果
    """
    result = {
        "os": platform.system(),
        "pmd_command": None,
        "command_exists": False,
        "lib_dir_exists": False,
        "conf_dir_exists": False,
        "java_available": False,
        "java_version": None,
        "ready": False
    }
    
    try:
        # Javaの確認
        try:
            java_check = subprocess.run(
                ["java", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            if java_check.returncode == 0:
                result["java_available"] = True
                # Javaバージョン情報は通常stderrに出力される
                version_output = java_check.stderr if java_check.stderr else java_check.stdout
                result["java_version"] = version_output.split('\n')[0] if version_output else "不明"
        except FileNotFoundError:
            result["java_available"] = False
            result["java_version"] = "Javaが見つかりません"
        
        # PMDコマンドパスを取得
        pmd_cmd = get_pmd_command()
        result["pmd_command"] = pmd_cmd
        
        # PMDコマンドファイルの存在確認
        if os.path.exists(pmd_cmd):
            result["command_exists"] = True
        
        # 必要なディレクトリの存在確認
        current_dir = Path(__file__).parent
        analyzer_dir = current_dir / "analyzer"
        
        lib_dir = analyzer_dir / "lib"
        conf_dir = analyzer_dir / "conf"
        
        result["lib_dir_exists"] = lib_dir.exists()
        result["conf_dir_exists"] = conf_dir.exists()
        
        # 全ての条件が満たされているかチェック
        result["ready"] = (result["command_exists"] and 
                          result["lib_dir_exists"] and 
                          result["conf_dir_exists"] and
                          result["java_available"])
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def is_windows():
    """
    Windows環境かどうかを判定する関数
    
    Returns:
        bool: Windowsの場合True、それ以外False
    """
    return platform.system() == "Windows"


def get_pmd_executable_name():
    """
    OS別のPMD実行ファイル名を取得する関数
    
    Returns:
        str: PMD実行ファイル名（pmd.batまたはpmd）
    """
    return "pmd.bat" if is_windows() else "pmd"


def find_apex_files(directory: str) -> List[str]:
    """
    指定されたディレクトリ内のすべてのApexファイル(.cls)を検索する関数
    
    Args:
        directory: 検索対象のディレクトリパス
    
    Returns:
        List[str]: 検出されたApexファイルのパスリスト
    """
    apex_files = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"警告: ディレクトリが存在しません: {directory}")
        return apex_files
    
    # classes ディレクトリを再帰的に検索
    for cls_file in dir_path.rglob("*.cls"):
        apex_files.append(str(cls_file))
    
    return apex_files


def parse_apex_ast(
    apex_file_or_dir: str,
    output_file: Optional[str] = None,
    format: str = "text"
) -> Dict:
    """
    PMDを使用してApexコードを解析し、ASTを出力する関数
    
    Args:
        apex_file_or_dir: 解析対象のApexファイルまたはディレクトリパス
        output_file: AST出力先ファイルパス（Noneの場合は標準出力）
        format: 出力フォーマット（"text"または"xml"）
    
    Returns:
        Dict: 実行結果の情報
    """
    result = {
        "success": False,
        "files_processed": 0,
        "output_file": output_file,
        "command": None,
        "error": None
    }
    
    try:
        # PMD環境チェック
        env_check = check_pmd_environment()
        if not env_check["ready"]:
            result["error"] = "PMD環境が準備できていません"
            return result
        
        pmd_cmd = get_pmd_command()
        
        # 対象ファイルの取得
        target_path = Path(apex_file_or_dir)
        if target_path.is_file():
            files_to_process = [str(target_path)]
        elif target_path.is_dir():
            files_to_process = find_apex_files(str(target_path))
        else:
            result["error"] = f"パスが存在しません: {apex_file_or_dir}"
            return result
        
        if not files_to_process:
            result["error"] = "処理対象のApexファイルが見つかりません"
            return result
        
        result["files_processed"] = len(files_to_process)
        
        # PMD ast-dumpコマンドの構築
        # PMD 7.x では ast-dump コマンドを使用
        cmd_args = [pmd_cmd, "ast-dump", "--language", "apex"]
        
        # フォーマット指定
        if format == "xml":
            cmd_args.extend(["--format", "xml"])
        
        # ファイルを指定
        cmd_args.extend(["--file"] + files_to_process)
        
        result["command"] = " ".join(cmd_args)
        
        # 実行フラグ（デフォルトでは実行しない）
        # 実行する場合は execute_pmd_ast 関数を使用してください
        result["success"] = True
        result["note"] = "コマンドは構築されましたが、実行されていません"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def execute_pmd_ast(
    apex_file_or_dir: str,
    output_file: Optional[str] = None,
    format: str = "text"
) -> Dict:
    """
    PMDを実際に実行してApexコードを解析し、ASTを出力する関数
    
    Args:
        apex_file_or_dir: 解析対象のApexファイルまたはディレクトリパス
        output_file: AST出力先ファイルパス（Noneの場合は標準出力）
        format: 出力フォーマット（"text"または"xml"）
    
    Returns:
        Dict: 実行結果の情報（出力内容を含む）
    """
    result = {
        "success": False,
        "files_processed": 0,
        "output_file": output_file,
        "command": None,
        "error": None,
        "output": None
    }
    
    try:
        # PMD環境チェック
        env_check = check_pmd_environment()
        if not env_check["ready"]:
            result["error"] = "PMD環境が準備できていません"
            return result
        
        pmd_cmd = get_pmd_command()
        
        # 対象ファイルの取得
        target_path = Path(apex_file_or_dir)
        if target_path.is_file():
            files_to_process = [str(target_path)]
        elif target_path.is_dir():
            files_to_process = find_apex_files(str(target_path))
        else:
            result["error"] = f"パスが存在しません: {apex_file_or_dir}"
            return result
        
        if not files_to_process:
            result["error"] = "処理対象のApexファイルが見つかりません"
            return result
        
        result["files_processed"] = len(files_to_process)
        
        # PMD ast-dumpコマンドの構築
        cmd_args = [pmd_cmd, "ast-dump", "--language", "apex"]
        
        # フォーマット指定
        if format == "xml":
            cmd_args.extend(["--format", "xml"])
        
        # ファイルを指定
        cmd_args.extend(["--file"] + files_to_process)
        
        result["command"] = " ".join(cmd_args)
        
        # 出力先の指定と実行
        if output_file:
            # 出力ディレクトリの作成
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                process = subprocess.run(
                    cmd_args,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
        else:
            process = subprocess.run(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
        
        if process.returncode == 0:
            result["success"] = True
            if not output_file:
                result["output"] = process.stdout
            else:
                result["output"] = f"ASTがファイルに出力されました: {output_file}"
        else:
            result["error"] = process.stderr if process.stderr else "不明なエラー"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def parse_apex_classes_directory(
    classes_dir: str,
    output_dir: Optional[str] = None,
    format: str = "text",
    execute: bool = False
) -> Dict:
    """
    classesディレクトリ内のすべてのApexファイルを解析してASTを出力する関数
    
    Args:
        classes_dir: classesディレクトリのパス
        output_dir: AST出力先ディレクトリ（Noneの場合は標準出力）
        format: 出力フォーマット（"text"または"xml"）
        execute: 実際にPMDを実行するかどうか（デフォルト: False）
    
    Returns:
        Dict: 実行結果の情報
    """
    result = {
        "success": False,
        "total_files": 0,
        "processed_files": [],
        "output_directory": output_dir,
        "errors": [],
        "executed": execute
    }
    
    try:
        # Apexファイルを検索
        apex_files = find_apex_files(classes_dir)
        result["total_files"] = len(apex_files)
        
        if not apex_files:
            result["error"] = f"Apexファイルが見つかりません: {classes_dir}"
            return result
        
        # 出力ディレクトリの作成
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # 各ファイルを処理
        for apex_file in apex_files:
            file_name = Path(apex_file).stem
            
            if output_dir:
                ext = "xml" if format == "xml" else "txt"
                output_file = str(Path(output_dir) / f"{file_name}_ast.{ext}")
            else:
                output_file = None
            
            # execute フラグに応じて実行または準備のみ
            if execute:
                parse_result = execute_pmd_ast(apex_file, output_file, format)
            else:
                parse_result = parse_apex_ast(apex_file, output_file, format)
            
            if parse_result["success"]:
                result["processed_files"].append({
                    "file": apex_file,
                    "output": output_file,
                    "command": parse_result["command"]
                })
            else:
                result["errors"].append({
                    "file": apex_file,
                    "error": parse_result.get("error", "Unknown error")
                })
        
        result["success"] = len(result["errors"]) == 0
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


if __name__ == "__main__":
    # テスト実行用
    print("=" * 80)
    print("PMD環境チェック結果:")
    print("=" * 80)
    env_check = check_pmd_environment()
    
    for key, value in env_check.items():
        print(f"  {key}: {value}")
    
    print(f"\n推奨PMDコマンド: {get_pmd_command()}")
    print(f"実行ファイル名: {get_pmd_executable_name()}")
    print(f"Windows環境: {is_windows()}")
    
    # Apexファイル解析のテスト
    print("\n" + "=" * 80)
    print("Apexファイル解析テスト:")
    print("=" * 80)
    
    # classesディレクトリのパス
    classes_dir = Path(__file__).parent / "project" / "dreamhouse-lwc" / "force-app" / "main" / "default" / "classes"
    
    if classes_dir.exists():
        print(f"\nclassesディレクトリ: {classes_dir}")
        
        # Apexファイルの検索
        apex_files = find_apex_files(str(classes_dir))
        print(f"\n検出されたApexファイル数: {len(apex_files)}")
        
        if apex_files:
            print("\nApexファイル一覧:")
            for i, apex_file in enumerate(apex_files, 1):
                print(f"  {i}. {Path(apex_file).name}")
            
            # AST解析の準備（実行はしない）
            print("\n" + "-" * 80)
            print("AST解析準備:")
            print("-" * 80)
            
            output_dir = Path(__file__).parent / "output" / "ast"
            result = parse_apex_classes_directory(
                str(classes_dir),
                str(output_dir),
                format="text"
            )
            
            print(f"\n処理対象ファイル数: {result['total_files']}")
            print(f"出力ディレクトリ: {result['output_directory']}")
            
            if result['processed_files']:
                print(f"\n準備完了ファイル数: {len(result['processed_files'])}")
                print("\n最初のファイルのコマンド例:")
                if result['processed_files']:
                    first_file = result['processed_files'][0]
                    print(f"  ファイル: {Path(first_file['file']).name}")
                    print(f"  出力先: {first_file['output']}")
                    print(f"  コマンド: {first_file['command'][:100]}...")
            
            if result['errors']:
                print(f"\nエラー数: {len(result['errors'])}")
            
            # 単一ファイルのAST解析テスト（実際に実行）
            print("\n" + "=" * 80)
            print("単一ファイルのAST解析テスト（実行）:")
            print("=" * 80)
            
            test_file = apex_files[0]  # 最初のファイルをテスト
            print(f"\nテストファイル: {Path(test_file).name}")
            
            output_dir = Path(__file__).parent / "output" / "ast"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = str(output_dir / f"{Path(test_file).stem}_ast.txt")
            
            print(f"出力先: {output_file}")
            print("\nPMDを実行中...")
            
            exec_result = execute_pmd_ast(test_file, output_file, format="text")
            
            if exec_result["success"]:
                print("✓ AST解析成功!")
                print(f"\n出力ファイルが作成されました: {output_file}")
                
                # 出力ファイルの最初の数行を表示
                if Path(output_file).exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:20]
                        print(f"\nAST出力プレビュー（最初の20行）:")
                        print("-" * 80)
                        print("".join(lines))
                        if len(lines) == 20:
                            print("...")
            else:
                print(f"✗ エラー: {exec_result['error']}")
    else:
        print(f"\nclassesディレクトリが見つかりません: {classes_dir}")
