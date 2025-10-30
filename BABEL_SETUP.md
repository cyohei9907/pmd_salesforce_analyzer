# Babel パーサーのセットアップ

LWC (Lightning Web Components) の JavaScript ファイルを解析するために、Babel パーサーを使用します。

## 前提条件

- Node.js (v14 以上推奨)
- npm (Node.js に含まれています)

Node.js がインストールされているか確認：
```bash
node --version
npm --version
```

## インストール

### Windows の場合

```bash
setup_babel.bat
```

### Linux/Mac の場合

```bash
chmod +x setup_babel.sh
./setup_babel.sh
```

または手動でインストール：

```bash
npm install
```

## 使用方法

### コマンドラインから直接使用

```bash
node js_ast_parser.js <input.js> <output.xml>
```

例：
```bash
node js_ast_parser.js ./project/dreamhouse-lwc/force-app/main/default/lwc/barcodeScanner/barcodeScanner.js ./output/barcodeScanner_ast.xml
```

### Git サービス経由で自動使用

LWC コンポーネントを解析すると、自動的に Babel パーサーが使用されます：

1. Git リポジトリをクローン
2. LWC コンポーネントを検出
3. JavaScript ファイルを Babel で解析
4. AST XML ファイルを生成

## 生成される AST の構造

Babel パーサーは以下の情報を抽出します：

- **Imports**: すべての import 文
- **Exports**: export された要素（デフォルト、名前付き）
- **Classes**: クラス定義、メソッド、プロパティ
- **Functions**: 関数定義
- **Properties**: クラスプロパティ

### XML 出力例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<JavaScriptFile name="barcodeScanner.js">
  <Imports>
    <Import source="lwc">
      <Specifier type="named" imported="LightningElement" local="LightningElement" />
    </Import>
  </Imports>
  <Exports>
    <Export type="default" name="BarcodeScanner" />
  </Exports>
  <Classes>
    <Class name="BarcodeScanner" superClass="LightningElement">
      <Properties>
        <Property name="myScanner" static="false" />
        <Property name="scanButtonEnabled" static="false" />
      </Properties>
      <Methods>
        <Method name="connectedCallback" kind="method" async="false" static="false">
        </Method>
        <Method name="handleBeginScanClick" kind="method" async="true" static="false">
        </Method>
      </Methods>
    </Class>
  </Classes>
</JavaScriptFile>
```

## トラブルシューティング

### Node.js がインストールされていない

[Node.js 公式サイト](https://nodejs.org/) からダウンロードしてインストールしてください。

### npm install がエラーになる

1. Node.js と npm のバージョンを確認
2. プロキシ設定が必要な場合は設定
3. `npm cache clean --force` を実行後、再度インストール

### Babel パーサーが見つからない

Git サービスは以下の順序でパーサーを探します：

1. プロジェクトルートの `js_ast_parser.js` (Babel)
2. 見つからない場合は PMD にフォールバック（ES5 のみサポート）

## サポートされる構文

Babel パーサーは以下の ES6+ 構文をサポートします：

- ✅ Import/Export (ES Modules)
- ✅ Arrow functions
- ✅ Async/Await
- ✅ Class properties
- ✅ Destructuring
- ✅ Template literals
- ✅ Optional chaining (?.)
- ✅ Nullish coalescing (??)
- ✅ Dynamic import
- ✅ BigInt
- ✅ JSX (React/LWC テンプレート)

## 依存パッケージ

- `@babel/parser`: JavaScript パーサー
- `@babel/traverse`: AST トラバーサル
