# Шаблон решения модератора по спору

```
Case ID: <номер кейса>
Contract ID: <номер контракта>
Priority: <high/medium/low>
Participants:
  - Claimant: <profile_id / имя>
  - Respondent: <profile_id / имя>
Finance observer: <email / none>

Summary:
- Кратко опишите претензию (2-3 предложения).
- Укажите ключевые доказательства (ID загрузок, ссылки).

Findings:
1. <Факт / нарушение, ссылка на доказательство>
2. <Факт / нарушение>

Policy reference:
- <Документ/пункт политики, на основании которого принимается решение>

Recommended outcome:
- full_release / partial_release / refund
- Для partial_release укажите доли, например `{ "client_share": 0.3 }`

Customer communication:
- Сообщение для истца:
```
<текст>
```
- Сообщение для ответчика:
```
<текст>
```

Audit log:
- Staff members involved: <usernames>
- Время подготовки решения: <UTC timestamp>
```
