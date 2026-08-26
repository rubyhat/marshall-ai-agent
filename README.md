# Marshall AI Agent Skills — archived experiment

> **Статус с 2026-08-27:** эксперимент завершён, repository переведён в
> archived/read-only state. Набор больше не развивается, не выпускается и не
> рекомендуется для установки либо нового project adoption.

`marshall-ai-agent` был попыткой вынести рабочий процесс FastyShop в 13
переиспользуемых Codex skills: от загрузки контекста и shaping до task-spec,
implementation, review, delivery и обслуживания project memory.

Эксперимент дал полезные наблюдения и отдельные технические решения, но основной
подход признан неудачным. Lifecycle orchestration через связанный набор skills,
общую project configuration и aliases сделала поведение агента чрезмерно
императивным, создала скрытую workflow-фазу, ложные blockers, повторные проверки
и дорогие review/correction loops. Добавление новых правил для очередных edge
cases увеличивало систему быстрее, чем повышало её надёжность.

Подробное заключение, evidence и правила допустимого исторического
использования находятся в
[ретроспективе эксперимента](docs/experiment-retrospective.md).

## Что сохранено

- исходный код 13 skills, schemas, scripts, fixtures и release history;
- последняя опубликованная версия `v0.10.0`;
- [манифест проектирования skills](docs/skill-design-manifesto.md) как
  исторический результат, а не active standard;
- Git history, Pull Requests и releases как evidence эволюции подхода;
- выводы о самостоятельности агента, достижимом завершении, proportional
  verification и точных runbooks для действительно хрупких операций.

## Historical package catalog

Папки сохранены как исходный материал эксперимента, а не как доступные для
установки modules:

| Package | Историческое назначение |
|---|---|
| `configure-project-workflow` | Setup и validation project workflow configuration. |
| `load-project-context` | Загрузка минимального task context. |
| `record-project-context` | Запись durable project knowledge. |
| `maintain-project-context` | Audit и cleanup project memory. |
| `manage-project-work` | GitHub Issues/Projects и task identity. |
| `shape-project-work` | Outcome, scope и decomposition. |
| `write-task-spec` | Создание task specification. |
| `publish-planning-change` | Review и публикация planning artifact. |
| `execute-project-task` | Implementation одной ready-задачи. |
| `deliver-reviewed-change` | Review, PR, merge и cleanup. |
| `design-frontend-flow` | Frontend interaction contract. |
| `triage-frontend-qa` | Диагностика frontend defect. |
| `analyze-product-reference` | Bounded product-reference analysis. |

## Что прекращено

- новые commits и releases после final archival revision;
- исправление или расширение lifecycle skills;
- установка либо синхронизация workflow kit в новые проекты;
- использование repository как active source of truth;
- перенос текущих skills, aliases или configuration schema в новый workflow.

## Допустимое дальнейшее использование

Repository можно читать как postmortem и reference pack. Отдельную идею можно
переосмыслить в другом проекте только после независимой проверки её назначения,
риска и поведения на реальных сценариях. Копирование существующего lifecycle
flow или package целиком не считается допустимым reuse.

Для следующей итерации FastyShop выбран другой уровень abstraction:

1. короткий project-local `AGENTS.md` с always-on invariants и настоящими
   authority/safety boundaries;
2. независимые Markdown guides для отдельных видов работы без обязательной
   глобальной последовательности;
3. exact runbooks или scripts только там, где порядок действительно является
   частью safety либо внешнего protocol.

Новый процесс проектируется с нуля. Этот repository не является его шаблоном.
