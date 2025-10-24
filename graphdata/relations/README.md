# Relations 关系文件

此目录存储图数据库中的所有关系（边）。

## 文件命名规则

- 格式: `{from}_{relation_type}_{to}_{timestamp}.json`
- 示例:
  - `PropertyController__HAS_METHOD__getPagedPropertyList_20251024210000.json`
  - `PropertyController__CONTAINS_SOQL__SELECT_20251024210001.json`

## 文件内容示例

```json
{
  "from_node": "class:PropertyController",
  "to_node": "method:PropertyController.getPagedPropertyList",
  "type": "HAS_METHOD",
  "properties": {
    "description": "Class contains method",
    "created_at": "2025-10-24T21:00:00.000000"
  }
}
```

## 关系类型

- **HAS_METHOD**: 类包含方法
- **CALLS**: 方法调用
- **CONTAINS_SOQL**: 包含 SOQL 查询
- **ACCESSES_SOBJECT**: 访问 Salesforce 对象
- **EXTENDS**: 继承关系
- **IMPLEMENTS**: 实现接口

## 自动清理

系统会定期清理重复的关系文件，保留最新版本。
