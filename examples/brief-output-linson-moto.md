# Golden Reference: /ga4-brief Output

This is a reference output showing the ideal format for a what-changed brief.
Use this as a visual guide — the template in `commands/ga4-brief.md` Step 6 is authoritative.

---

## Linson Moto - Какво се промени
**Property:** linsonmoto.bg (365157221)
**Period:** Mar 14-20, 2026 vs Mar 7-13, 2026 (7 days)
**Context:** loaded | **Data quality:** 100/100
**Baselines:** CR 1.14% (current: 1.08%) | AOV 113.06 BGN (current: 98.50 BGN)

> **Organic Social удвои приходите, докато PMax кампаниите показват спад от 51% — необходима е проверка на ROAS в Google Ads.**
>
> **Context:** Direct трафик -57% е почистване на бот трафик (engagement rate 29%), не реален спад на потребители.

---

### Finding 1: Cross-network (PMax) приходи спад [NEW]

| Metric | This period | Previous | Change |
|--------|-----------|----------|--------|
| Cross-network revenue | 3,747 BGN | 7,726 BGN | -51.5% |
| Cross-network sessions | 1,142 | 1,389 | -17.8% |

**Pattern:** #19 - AOV changes
**Analysis:** Дневният тренд показва два дни с извънредно високи стойности в предходния период, които изкривяват сравнението. Сесиите спадат умерено (-17.8%), но приходите — много повече (-51.5%), което предполага промяна в AOV или продуктов микс. [Data: Mar 14-20, 2026]
**Verdict:** INCONCLUSIVE - Може да е нормална AOV вариация или реален PMax спад
**Action:** Проверете Google Ads: PMax ROAS за последните 14 дни и сравнете AOV по кампании [effort: quick]

---

### Finding 2: Organic Social удвояване на приходите [NEW]

| Metric | This period | Previous | Change |
|--------|-----------|----------|--------|
| Organic Social revenue | 778 BGN | 389 BGN | +99.9% |
| Organic Social sessions | 892 | 647 | +37.9% |
| Organic Social purchases | 8 | 4 | +100% |

**Pattern:** #2 - Channel quality shifts
**Analysis:** Трафикът расте +37.9% и приходите се удвояват — качеството на трафика се подобрява значително. Engagement rate остава стабилен (32% vs 30%), а конверсиите се удвояват. Това е истински растеж, не ефект от обем. [Data: Mar 14-20, 2026]
**Verdict:** CONFIRMED - Organic Social генерира повече и по-качествен трафик
**Action:** Идентифицирайте кои публикации водят покупки — мащабирайте успешния формат [effort: medium]

---

### Finding 3: Organic Search приходи спад [NEW]

| Metric | This period | Previous | Change |
|--------|-----------|----------|--------|
| Organic Search revenue | 4,012 BGN | 4,975 BGN | -19.3% |
| Organic Search sessions | 3,241 | 3,487 | -7.1% |

**Pattern:** #10 - Conversion rate vs volume divergence
**Analysis:** Сесиите спадат умерено (-7.1%), но приходите повече (-19.3%). Конверсионният процент намалява, което предполага промяна в landing page качеството или продуктовата наличност. Дневният тренд не показва внезапен срив — постепенен спад. [Data: Mar 14-20, 2026]
**Verdict:** INCONCLUSIVE - Нужна е проверка в Search Console за промени в позиции
**Action:** Проверете Search Console за промени в impressions/CTR на топ landing pages [effort: quick]

---

## Notable Mentions
- chatgpt.com: 142 сесии, 389 BGN приходи — нов AI search канал, малък но с високо качество
- Referral от facebook.com спад -23% — може да е свързан с промяна в алгоритъма

## Next Steps
1. Проверете Google Ads PMax ROAS за последните 14 дни [priority: high]
2. Идентифицирайте топ Organic Social публикации с покупки — мащабирайте формата [priority: high]
3. Проверете Search Console за промени в organic позиции и CTR [priority: medium]
4. Проследете chatgpt.com трафик — нов канал за мониторинг [priority: low]
