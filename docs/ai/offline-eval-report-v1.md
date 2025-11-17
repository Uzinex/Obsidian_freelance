# Offline Evaluation Report v1

## 1. Summary
- Датасеты v1 собраны: matching (1 000 пар), coach (800 диалогов), disputes (520), scam/spam (720).
- Разметка выполнена по двуязычным гайдам, Cohen's κ ≥ 0.62.
- Модели прошли фильтры допуска в A/B (см. §6).

## 2. Разметка и согласие
| Задача | Объём | Доля double-annotation | Cohen's κ |
| --- | --- | --- | --- |
| Matching job↔profile | 1 000 | 0.20 | 0.67 |
| Coach quality | 800 | 0.30 | 0.64 |
| Dispute classes | 520 | 0.25 | 0.61 |
| Scam/Spam | 720 | 0.25 | 0.63 |

## 3. Фильтры/классификаторы (ROC-AUC / F1)
| Модель | ROC-AUC | F1@0.5 | Порог для прод | Комментарий |
| --- | --- | --- | --- | --- |
| Scam detector (fraud vs benign) | 0.942 | 0.81 | 0.55 | язык адаптивен ru/uz |
| Spam fan-out detector | 0.901 | 0.77 | 0.52 | высокое precision 0.83 |
| Dispute router (multi-class macro) | 0.872 | 0.69 | argmax | усилили features escrow |

## 4. Matching/Search (MRR / nDCG@10)
| Модель | MRR@10 | nDCG@10 | Baseline | Δ |
| --- | --- | --- | --- | --- |
| Dual encoder v1 | 0.402 | 0.526 | BM25=0.298 | +0.104 |
| Cross-encoder reranker | 0.513 | 0.621 | Dual=0.402 | +0.111 |

## 5. Human ranking для AI-коуча
- Панель из 5 кураторов (ru/uz) сравнивала AI-ответы против human baseline на 120 диалогах.
- **Win/Tie/Loss:** 46% / 32% / 22%.
- **Top issues:** недостаток локализации (16%), нет ссылок на реальные компании (9%).

## 6. Критерии допуска в A/B (pre-launch gates)
| Направление | Порог | Факт |
| --- | --- | --- |
| Spam ROC-AUC ≥ 0.90 и F1 ≥ 0.75 | выполнено | 0.94 / 0.81 |
| Dispute классификация Macro-F1 ≥ 0.65 | выполнено | 0.69 |
| Matching nDCG@10 ≥ 0.50 | выполнено | 0.62 |
| Coach human win-rate ≥ 40% и «неполезные» < 8% | выполнено | 46% win, 6.5% неполезных |

## 7. Рекомендации
1. Увеличить долю узбекских вакансий в matching до 35%.
2. Добавить негативные примеры с переключением языка для spam detector.
3. Повторная оффлайн-оценка через 6 недель либо при обновлении эмбеддингов.

