## Deferred from: code review of story 2.4 (2026-06-12)

- 比赛名包含 `{name}` 字面量时弹窗文案异常 — 极低概率
- 网络断开时前端显示"删除失败"但后端已删除 — DELETE 幂等性已处理
- parseCustomScoring 前端校验不足 — pre-existing from Story 2.3
- Dashboard 401 认证过期未单独处理 — pre-existing 模式
- StatusBadge Unicode 图标无障碍替代文本缺失 — pre-existing

## Deferred from: code review of story 3.1-scoring-engine (2026-06-12)

- AC-5 示例描述中数字笔误（"5 points for the 6th position" 应为 "1 point"） — 代码实现正确，仅故事文件示例数字需调整

## Deferred from: one-shot mobile fixes (2026-07-08)

- 移动端管理下拉菜单在低屏幕高度设备上可能溢出视口 — dropdown positioning boundary check
- 桌面版 scroll-container 的 `position: fixed` 在移动端渲染模式下的 slot 布局待确认

