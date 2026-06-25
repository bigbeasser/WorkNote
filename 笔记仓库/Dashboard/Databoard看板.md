## 🔖 技术文章知识库

```dataview
LIST
FROM "大厂技术文章-DailyTech/文章"
WHERE contains(tags, "tech-article")
SORT file.cday DESC
```

### 标签统计

```dataview
TABLE length(rows) AS 篇数
FROM "大厂技术文章-DailyTech/文章"
WHERE contains(tags, "tech-article")
FLATTEN tags AS tag
WHERE tag != "tech-article"
GROUP BY tag
SORT length(rows) DESC
```

> 专题导航见 [[../大厂技术文章-DailyTech/📋 文章索引|📋 技术文章索引]]

---

```dataview
list 
from ""
where contains(file.name,"期货")
```

```dataview
TABLE deadline AS 完成截止, owner AS 负责人 FROM #project WHERE status = "已完成" SORT deadline DESC
```
