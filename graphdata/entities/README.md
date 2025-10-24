# Entities 实体文件

此目录存储图数据库中的所有实体（节点）。

## 文件命名规则

- 格式: `{type}_{name}_{timestamp}.json`
- 示例:
  - `ApexClass_PropertyController_20251024210000.json`
  - `ApexMethod_getPagedPropertyList_20251024210001.json`

## 文件内容示例

```json
{
  "node_id": "class:PropertyController",
  "attributes": {
    "type": "ApexClass",
    "name": "PropertyController",
    "simpleName": "PropertyController",
    "public": true,
    "withSharing": true,
    "fileName": "PropertyController.cls",
    "created_at": "2025-10-24T21:00:00.000000"
  }
}
```

## 实体类型

- **ApexClass**: Apex 类
- **ApexMethod**: Apex 方法
- **ApexField**: Apex 字段
- **SObject**: Salesforce 对象

## 自动清理

系统会定期清理重复的实体文件，保留最新版本。
