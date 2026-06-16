## 🔖 技术文章知识库

```dataview
LIST
FROM "技术文章-DailyTech"
WHERE contains(tags, "tech-article")
SORT file.cday DESC
```

### 标签统计

```dataview
LIST rows.file.link
FROM "技术文章-DailyTech"
WHERE contains(tags, "tech-article")
FLATTEN tags
GROUP BY tags
SORT rows.length DESC
```

---

```dataview
list 
from ""
where contains(file.name,"期货")
```

```dataview
TABLE deadline AS 完成截止, owner AS 负责人 FROM #project WHERE status = "已完成" SORT deadline DESC
```