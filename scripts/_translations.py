"""
Data Arsenal v1 - Translations
EN + BG translations for all report text.
"""

TRANSLATIONS = {
    'en': {
        'report_title': 'GA4 Health Check',
        'health_score': 'Health Score',
        'what_to_fix': 'What to Fix',
        'critical_issues_summary': '{count} critical issue(s) found. Fix these before trusting your data.',
        'warnings_summary': '{count} warning(s). Review and address when possible.',
        'all_passed': 'All checks passed. Data quality looks good.',
        'priority_critical': 'CRITICAL',
        'priority_recommended': 'Recommended',
        'priority_info': 'Info',
        'footer_note': 'These are 20 health checks using Data API only. For a comprehensive 50-check audit including Admin API settings, GTM analysis, and consent mode verification, visit audit.dataarsenal.com',
        'table_headers': {
            'num': '#',
            'check': 'Check',
            'status': 'Status',
            'details': 'Details',
        },
        'status_labels': {
            'PASS': 'Pass',
            'WARN': 'Warning',
            'FAIL': 'Fail',
            'SKIP': 'Skipped',
            'INFO': 'Info',
        },
        'check_names': {
            'Data Volume': 'Data Volume',
            'Duplicate Tracking': 'Duplicate Tracking',
            'Enhanced Measurement': 'Enhanced Measurement',
            'Conversion Events': 'Conversion Events',
            'E-commerce Completeness': 'E-commerce Completeness',
            'Referral Spam': 'Referral Spam',
            'Self-Referral': 'Self-Referral',
            '(not set) Landing Pages': '(not set) Landing Pages',
            'High Bounce Pages': 'High Bounce Pages',
            'Event Variety': 'Event Variety',
            'Event Naming': 'Event Naming',
            'Recommended Events': 'Recommended Events',
            'Payment Gateway Referral': 'Payment Gateway Referral',
            'Channel Diversification': 'Channel Diversification',
            'Hostname Pollution': 'Hostname Pollution',
            'PII in URLs': 'PII in URLs',
            'Bot Traffic': 'Bot Traffic',
            'Event Quality': 'Event Quality',
            'Direct Traffic': 'Direct Traffic',
            'Engagement Rate Anomalies': 'Engagement Rate Anomalies',
        },
        'remediation': {
            'Data Volume': {
                'FAIL': 'Property has very little traffic. Wait for more data or check that the GA4 tag is firing on all pages.',
                'WARN': 'Low traffic limits statistical significance. Be cautious with segment-level analysis.',
            },
            'Duplicate Tracking': {
                'FAIL': 'Remove the duplicate GA4 tag. Check GTM for multiple GA4 config tags, or a hardcoded gtag.js plus GTM firing together.',
                'WARN': 'Verify there is only one GA4 measurement ID active. Check GTM and page source for duplicate tags.',
            },
            'Enhanced Measurement': {
                'WARN': 'Enable missing events in GA4 Admin > Data Streams > Enhanced Measurement. Toggle on scroll, outbound clicks, site search, file downloads, video engagement.',
            },
            'Conversion Events': {
                'WARN': 'Mark your most important events as key events in GA4 Admin > Events. Common choices: form submissions, purchases, sign-ups, contact clicks.',
            },
            'E-commerce Completeness': {
                'FAIL': 'Funnel step counts are inverted — a later step has more events than an earlier one. This indicates a tracking error: duplicate tags, misconfigured triggers, or events firing on wrong pages. Audit your GTM triggers for each funnel event.',
                'WARN': 'Implement missing e-commerce funnel events (view_item, add_to_cart, begin_checkout) in your dataLayer or GTM. GA4 needs the full funnel for monetization reports.',
            },
            'Referral Spam': {
                'WARN': 'Create a data filter in GA4 Admin > Data Streams > Data Filters to exclude known spam domains. Or add a referral exclusion list.',
            },
            'Self-Referral': {
                'FAIL': 'Your own domain is appearing as a referral source for >5% of traffic. Add all your domains to GA4 Admin > Data Streams > Configure Tag Settings > List Unwanted Referrals. Also check for missing cross-domain tracking if you use multiple domains.',
                'WARN': 'Add your own domain(s) to the referral exclusion list in GA4 Admin > Data Streams > Configure Tag Settings > List Unwanted Referrals.',
            },
            '(not set) Landing Pages': {
                'FAIL': 'High (not set) rate usually means events firing without a page_view, or session timeout issues. Check that page_view fires on every page load before other events.',
                'WARN': 'Some (not set) landing pages are normal. If above 10%, investigate events that fire without a preceding page_view.',
            },
            'High Bounce Pages': {
                'WARN': 'Review these pages for slow load times, misleading ad copy, or poor mobile experience. High bounce on landing pages directly impacts campaign ROI.',
            },
            'Event Variety': {
                'WARN': 'Under-tracked: add events for key user actions (form fills, button clicks, scroll depth). Over-tracked: consolidate redundant events to stay under GA4 limits.',
            },
            'Event Naming': {
                'FAIL': 'Rename events to use lowercase_with_underscores (GA4 convention). Mixed case causes reporting fragmentation and breaks BigQuery exports.',
                'WARN': 'A few events use non-standard naming. Rename to lowercase_with_underscores for consistency.',
            },
            'Recommended Events': {
                'WARN': 'Implement GA4 recommended events for your property type. This unlocks built-in reports and audience suggestions. See: https://support.google.com/analytics/answer/9267735',
                'INFO': 'Property is in early stages. As you add features, implement GA4 recommended events to unlock built-in reports.',
            },
            'Payment Gateway Referral': {
                'FAIL': 'Add payment gateway domains (stripe.com, paypal.com, etc.) to your referral exclusion list. They break attribution by creating new sessions after payment.',
                'WARN': 'Payment gateway appearing in referrals at low volume. Add to referral exclusion list to prevent attribution erosion as traffic grows.',
            },
            'Channel Diversification': {
                'FAIL': 'Critical dependency on one channel. Diversify acquisition: if organic-heavy, invest in paid/email; if paid-heavy, invest in SEO/content.',
                'WARN': 'Over-reliance on one channel creates risk. Start testing secondary channels before the primary one underperforms.',
            },
            'Hostname Pollution': {
                'FAIL': 'Dev/staging traffic is polluting production data. Create separate GA4 properties for dev environments, or add hostname data filters.',
                'WARN': 'Minor dev/test traffic detected. Consider data filters or separate measurement IDs for non-production environments.',
            },
            'PII in URLs': {
                'FAIL': 'PII in URLs violates GA4 Terms of Service and privacy regulations (GDPR/CCPA). Fix form submissions to use POST instead of GET, and redact URL parameters in GTM before they reach GA4.',
                'WARN': 'Potential phone numbers in URLs. Review forms and redirects to ensure personal data is not passed in URL parameters.',
            },
            'Bot Traffic': {
                'FAIL': 'Over 15% of traffic shows bot-like behavior (near-zero engagement, instant bounces). Create audience exclusions or data filters. Check for scrapers, monitoring tools, or purchased traffic.',
                'WARN': 'Some traffic sources show bot-like patterns. Monitor these sources and consider filtering if they grow.',
            },
            'Event Quality': {
                'FAIL': 'An event is firing >10x per session — likely a tag loop or misconfigured trigger. Check GTM for auto-firing triggers on this event. This inflates event counts and may hit GA4 limits.',
                'WARN': 'Minor event quality issues detected. Review test events and near-duplicate names to keep your event schema clean.',
            },
            'Direct Traffic': {
                'FAIL': 'Over 60% direct traffic usually means UTM parameters are missing from campaigns, or cross-domain tracking is broken. Tag all campaigns with UTMs and verify cross-domain setup.',
                'WARN': 'Direct traffic above 40% suggests UTM gaps. Review email campaigns, social posts, and paid ads for proper UTM tagging.',
            },
            'Engagement Rate Anomalies': {
                'FAIL': 'Average engagement rate below 25% indicates a critical tracking issue (tag firing incorrectly) or severe bot traffic problem.',
                'WARN': 'Engagement rate shows unusual patterns. Investigate days with anomalous values for tracking changes or traffic spikes.',
            },
        },
        'brief': {
            'title': 'What Changed',
            'period': 'Period',
            'context': 'Context',
            'data_quality': 'Data quality',
            'key_insight': 'Key Insight',
            'finding': 'Finding',
            'next_steps': 'Next Steps',
            'notable': 'Notable Mentions',
            'baselines': 'Baselines',
            'context_note': 'Context',
            'analysis': 'Analysis',
            'pattern': 'Pattern',
            'verdict': 'Verdict',
            'action': 'Action',
            'effort': 'Effort',
            'quiet_period': 'Quiet period - no significant changes detected.',
            'no_action': 'No action needed this period.',
            'vs': 'vs',
            'days': 'days',
            'current': 'Current',
            'previous': 'Previous',
            'change': 'Change',
            'cr': 'CR',
            'aov': 'AOV',
        },
        'tags': {
            'NEW': 'NEW',
            'ONGOING': 'ONGOING',
            'WORSENING': 'WORSENING',
            'IMPROVING': 'IMPROVING',
        },
        'verdicts': {
            'CONFIRMED': 'CONFIRMED',
            'REFUTED': 'REFUTED',
            'INCONCLUSIVE': 'INCONCLUSIVE',
        },
        'priority': {
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
        },
        'effort': {
            'quick': 'quick',
            'medium': 'medium',
            'project': 'project',
        },
        'pdf': {
            'generated_by': 'Generated by Data Arsenal',
            'footer': 'audit.dataarsenal.com',
            'page': 'Page',
        },
    },
    'bg': {
        'report_title': 'GA4 Health Check',
        'health_score': 'Здравен резултат',
        'what_to_fix': 'Какво да поправите',
        'critical_issues_summary': '{count} критичен проблем(а). Поправете преди да разчитате на данните.',
        'warnings_summary': '{count} предупреждение(я). Прегледайте и адресирайте при възможност.',
        'all_passed': 'Всички проверки преминаха. Качеството на данните изглежда добро.',
        'priority_critical': 'КРИТИЧНО',
        'priority_recommended': 'Препоръчително',
        'priority_info': 'Инфо',
        'footer_note': 'Това са 20 проверки използващи само Data API. За цялостен одит с 50 проверки включващ Admin API настройки, GTM анализ и верификация на consent mode, посетете audit.dataarsenal.com',
        'table_headers': {
            'num': '#',
            'check': 'Проверка',
            'status': 'Статус',
            'details': 'Детайли',
        },
        'status_labels': {
            'PASS': 'OK',
            'WARN': 'Внимание',
            'FAIL': 'Проблем',
            'SKIP': 'Пропуснато',
            'INFO': 'Инфо',
        },
        'check_names': {
            'Data Volume': 'Обем на данните',
            'Duplicate Tracking': 'Дублиран тракинг',
            'Enhanced Measurement': 'Enhanced Measurement',
            'Conversion Events': 'Конверсии',
            'E-commerce Completeness': 'E-commerce пълнота',
            'Referral Spam': 'Referral спам',
            'Self-Referral': 'Self-referral',
            '(not set) Landing Pages': '(not set) Landing Pages',
            'High Bounce Pages': 'Страници с висок bounce',
            'Event Variety': 'Разнообразие на събития',
            'Event Naming': 'Именуване на събития',
            'Recommended Events': 'Препоръчани събития',
            'Payment Gateway Referral': 'Payment Gateway Referral',
            'Channel Diversification': 'Диверсификация на канали',
            'Hostname Pollution': 'Hostname замърсяване',
            'PII in URLs': 'PII в URL адреси',
            'Bot Traffic': 'Бот трафик',
            'Event Quality': 'Качество на събитията',
            'Direct Traffic': 'Директен трафик',
            'Engagement Rate Anomalies': 'Аномалии в engagement rate',
        },
        'remediation': {
            'Data Volume': {
                'FAIL': 'Много малко трафик. Изчакайте повече данни или проверете дали GA4 тагът се зарежда на всички страници.',
                'WARN': 'Нисък трафик ограничава статистическата значимост. Бъдете внимателни при анализ по сегменти.',
            },
            'Duplicate Tracking': {
                'FAIL': 'Премахнете дублирания GA4 таг. Проверете GTM за множество GA4 config тагове или gtag.js и GTM работещи едновременно.',
                'WARN': 'Проверете дали има само един активен GA4 measurement ID. Проверете GTM и кода на страницата за дублирани тагове.',
            },
            'Enhanced Measurement': {
                'WARN': 'Включете липсващите събития в GA4 Admin > Data Streams > Enhanced Measurement. Включете scroll, outbound clicks, site search, file downloads, video engagement.',
            },
            'Conversion Events': {
                'WARN': 'Маркирайте най-важните събития като key events в GA4 Admin > Events. Чести избори: form submissions, purchases, sign-ups, contact clicks.',
            },
            'E-commerce Completeness': {
                'FAIL': 'Броят на събитията в фунията е обърнат — по-късна стъпка има повече събития от по-ранна. Това индикира грешка в тракинга: дублирани тагове, грешни тригери или събития на грешни страници. Проверете GTM тригерите за всяко funnel събитие.',
                'WARN': 'Имплементирайте липсващите e-commerce funnel събития (view_item, add_to_cart, begin_checkout) в dataLayer или GTM. GA4 изисква пълната фуния за monetization reports.',
            },
            'Referral Spam': {
                'WARN': 'Създайте data filter в GA4 Admin > Data Streams > Data Filters за изключване на известни спам домейни.',
            },
            'Self-Referral': {
                'FAIL': 'Собственият ви домейн се появява като referral източник за >5% от трафика. Добавете всички домейни в GA4 Admin > Data Streams > Configure Tag Settings > List Unwanted Referrals. Проверете и за липсващ cross-domain tracking.',
                'WARN': 'Добавете собствения домейн(и) в referral exclusion list в GA4 Admin > Data Streams > Configure Tag Settings > List Unwanted Referrals.',
            },
            '(not set) Landing Pages': {
                'FAIL': 'Висок (not set) процент обикновено означава събития без page_view или проблеми със session timeout. Проверете дали page_view се задейства на всяка страница преди другите събития.',
                'WARN': 'Някои (not set) landing pages са нормални. Ако са над 10%, проверете за събития без предшестващ page_view.',
            },
            'High Bounce Pages': {
                'WARN': 'Прегледайте тези страници за бавно зареждане, подвеждащи рекламни текстове или лошо мобилно изживяване.',
            },
            'Event Variety': {
                'WARN': 'Под-проследено: добавете събития за ключови действия (попълване на формуляри, кликове, scroll depth). Пре-проследено: консолидирайте излишните събития.',
            },
            'Event Naming': {
                'FAIL': 'Преименувайте събитията да използват lowercase_with_underscores (GA4 конвенция). Смесен регистър причинява фрагментация в отчетите и чупи BigQuery exports.',
                'WARN': 'Няколко събития използват нестандартно именуване. Преименувайте към lowercase_with_underscores за консистентност.',
            },
            'Recommended Events': {
                'WARN': 'Имплементирайте GA4 препоръчани събития за вашия тип имот. Това отключва вградени отчети и audience suggestions.',
                'INFO': 'Имотът е в ранен стадий. С добавянето на функционалности, имплементирайте GA4 препоръчани събития.',
            },
            'Payment Gateway Referral': {
                'FAIL': 'Добавете домейните на payment gateway (stripe.com, paypal.com и др.) в referral exclusion list. Те нарушават attribution като създават нови сесии след плащане.',
                'WARN': 'Payment gateway присъства в referrals с нисък обем. Добавете в referral exclusion list преди обемът да нарасне.',
            },
            'Channel Diversification': {
                'FAIL': 'Критична зависимост от един канал. Диверсифицирайте: ако е organic-heavy, инвестирайте в paid/email; ако е paid-heavy, инвестирайте в SEO/content.',
                'WARN': 'Прекомерна зависимост от един канал създава риск. Започнете тестване на вторични канали.',
            },
            'Hostname Pollution': {
                'FAIL': 'Dev/staging трафик замърсява production данните. Създайте отделни GA4 properties за dev среди или добавете hostname data filters.',
                'WARN': 'Открит малък dev/test трафик. Обмислете data filters или отделни measurement ID за не-production среди.',
            },
            'PII in URLs': {
                'FAIL': 'PII в URL адреси нарушава GA4 Terms of Service и privacy регулации (GDPR/CCPA). Поправете form submissions да използват POST вместо GET и редактирайте URL параметри в GTM.',
                'WARN': 'Потенциални телефонни номера в URL адреси. Прегледайте формуляри и пренасочвания.',
            },
            'Bot Traffic': {
                'FAIL': 'Над 15% от трафика показва бот-подобно поведение (нулев engagement, мигновен bounce). Създайте audience exclusions или data filters. Проверете за скрейпъри, мониторинг инструменти или купен трафик.',
                'WARN': 'Някои източници на трафик показват бот-подобни модели. Наблюдавайте и филтрирайте при необходимост.',
            },
            'Event Quality': {
                'FAIL': 'Събитие се задейства >10x на сесия — вероятно tag loop или грешен тригер. Проверете GTM за auto-firing тригери. Това изкуствено увеличава event counts и може да удари GA4 лимити.',
                'WARN': 'Открити незначителни проблеми с качеството на събитията. Прегледайте тестови събития и близко-дублирани имена.',
            },
            'Direct Traffic': {
                'FAIL': 'Над 60% директен трафик обикновено означава липсващи UTM параметри в кампаниите или проблем с cross-domain tracking. Тагнете всички кампании с UTM и проверете cross-domain настройките.',
                'WARN': 'Директен трафик над 40% подсказва UTM пропуски. Прегледайте email кампании, социални постове и платени реклами за правилно UTM тагване.',
            },
            'Engagement Rate Anomalies': {
                'FAIL': 'Среден engagement rate под 25% индикира критичен проблем с тракинга (таг задействащ се некоректно) или сериозен проблем с бот трафик.',
                'WARN': 'Engagement rate показва необичайни модели. Проверете дните с аномални стойности за промени в тракинга или трафик спайкове.',
            },
        },
        'brief': {
            'title': 'Какво се промени',
            'period': 'Период',
            'context': 'Контекст',
            'data_quality': 'Качество на данните',
            'key_insight': 'Ключов извод',
            'finding': 'Находка',
            'next_steps': 'Следващи стъпки',
            'notable': 'Забележителни',
            'baselines': 'Базови стойности',
            'context_note': 'Контекст',
            'analysis': 'Анализ',
            'pattern': 'Модел',
            'verdict': 'Заключение',
            'action': 'Действие',
            'effort': 'Усилие',
            'quiet_period': 'Спокоен период - няма значителни промени.',
            'no_action': 'Не са необходими действия за този период.',
            'vs': 'спрямо',
            'days': 'дни',
            'current': 'Текущ',
            'previous': 'Предишен',
            'change': 'Промяна',
            'cr': 'CR',
            'aov': 'AOV',
        },
        'tags': {
            'NEW': 'НОВО',
            'ONGOING': 'ПРОДЪЛЖАВА',
            'WORSENING': 'ВЛОШАВА СЕ',
            'IMPROVING': 'ПОДОБРЯВА СЕ',
        },
        'verdicts': {
            'CONFIRMED': 'ПОТВЪРДЕНО',
            'REFUTED': 'ОПРОВЕРГАНО',
            'INCONCLUSIVE': 'НЕОПРЕДЕЛЕНО',
        },
        'priority': {
            'high': 'висок',
            'medium': 'среден',
            'low': 'нисък',
        },
        'effort': {
            'quick': 'бързо',
            'medium': 'средно',
            'project': 'проект',
        },
        'pdf': {
            'generated_by': 'Генерирано от Data Arsenal',
            'footer': 'audit.dataarsenal.com',
            'page': 'Страница',
        },
    },
}


def get_translator(lang_code):
    """Return translation dict for given language code, fallback to English."""
    return TRANSLATIONS.get(lang_code, TRANSLATIONS['en'])
