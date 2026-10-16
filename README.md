# Ying 智能订阅日历 v4

这是一个可托管在 GitHub 的苹果日历订阅项目，支持：

- 中国农历传统节日
- 二十四节气
- 中国大陆法定休假/补班数据槽位
- 全球通用节日
- AI 简报入口：OpenRouter、ChatGPT/OpenAI、Codex、OpenClaw
- 大陆院线电影入口：猫眼、淘票票
- 插件化扩展：以后新增模块只需要放入 `plugins/`

## 快速使用

1. 新建 GitHub 仓库。
2. 上传本项目全部文件。
3. 在仓库 Actions 页面启用 workflow。
4. 手动运行一次 `Update Smart Calendar`。
5. 订阅：

```text
https://raw.githubusercontent.com/你的用户名/你的仓库名/main/calendar.ics
```

iPhone 路径：

```text
设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅的日历
```

## 值班安排与同步

`daily_life` 插件读取 `config.json` 中的 `duty_schedule`：从
2026-10-15 起每 3 天一次全天值班，长期有效。日历使用单个
`RRULE:FREQ=DAILY;INTERVAL=3` 事件，不受 `years_ahead` 限制。
固定 UID（`daily-life-duty` 的哈希）确保再次生成或订阅刷新时更新同一事件。
调整安排时修改配置并重新生成，不要另外导入同一份 ICS。

订阅地址：

```text
https://raw.githubusercontent.com/Yingzi920/iponerili/main/calendar.ics
```

更新配置或插件后，运行 `python generate_calendar.py` 并提交 `calendar.ics`，
或在 Actions → Update Smart Calendar → Run workflow 中选择 `main`。
现有 workflow 也会每天 UTC 22:20（北京时间次日 06:20）更新；代码提交
本身不会触发该 workflow。已订阅此链接的苹果日历等待或手动刷新即可；
首次使用按上面的 iPhone 路径订阅一次。仓库更新不能验证设备已刷新。

验证值班规则：`python -m unittest discover -s tests -v`。

## 扩展方式

新增一个插件：

```text
plugins/legal_deadlines.py
```

实现：

```python
from .base import CalendarEvent

def plugin_name():
    return "legal_deadlines"

def generate(config):
    return [
        CalendarEvent(
            title="示例事件",
            start="2026-05-01",
            all_day=True,
            description="说明",
            categories=["扩展模块"],
            uid_seed="legal-deadlines-demo"
        )
    ]
```

然后在 `config.json` 的 `enabled_plugins` 里加入：

```json
"legal_deadlines"
```

## 设计原则

- 插件之间互不影响
- 抓取失败不破坏已有 calendar.ics
- 动态数据先缓存，再写入日历
- 苹果日历只订阅一个稳定 Raw 链接
- 以后可接 Notion、Telegram、OpenClaw、财务账单、案件期限

## 邮箱与自述日程

`mail_events` 读取 `data/mail_events.json` 的已核实全天单次事项，通过中央生成器发布。
以业务事项和实际服务周期指定稳定 `identity`；改日期保留 identity，不以邮件ID建事件。
同一事项跨邮件/来源合并 source_hashes，不存邮件正文、账号、主机IP、密码或支付信息。
不同真实周期分别建记录；状态 confirmed 生成，pending_confirmation / cancelled 保留数据但不生成。
当前接口仅支持有明确日期的全天事项；有具体时刻的安排须先扩展并验证时区支持，不能丢弃时刻。
不要把账单创建日当付款状态，也不把服务期结束日推算为自动扣款日。每次更新运行完整生成器并核对原事件保留。


