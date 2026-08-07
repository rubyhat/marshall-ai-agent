# Marshall AI Agent Skills

Личная библиотека reusable skills для Codex. Набор описывает не продуктовую логику конкретного проекта, а переносимые рабочие процессы: от загрузки контекста и формирования задачи до реализации, review, delivery и обслуживания проектной документации.

Сейчас в репозитории находятся 12 reusable skills, включая интерактивный `configure-project-workflow` для безопасной первоначальной настройки и последующей проверки проекта. Набор версионируется и выпускается как единый совместимый workflow kit.

## Основная идея

Рабочий процесс разделён на три слоя:

1. **Reusable skill** определяет универсальную процедуру, границы полномочий и точки передачи работы.
2. **Project configuration** хранит названия репозиториев, пути, статусы, Task ID, GitHub Project, локали, quality gates и другие значения конкретного проекта.
3. **Project instructions и docs** содержат постоянно активные правила, архитектуру, продуктовый контекст и локальные runbooks.

Skills не должны содержать жёсткую привязку к одному проекту. Полный workflow предполагает, что подключающий проект создаст собственные `AGENTS.md` и `.codex/project-workflow.yaml`.

## Первая настройка нового проекта

Этот раздел — рекомендуемый путь для разработчика, который использует готовый
workflow kit, но не разрабатывает сам `marshall-ai-agent`.

Не клонируйте этот репозиторий внутрь продуктового проекта. Установите только
bootstrap skill через системный `skill-installer` по exact release tag. Для
версии, выпускаемой этим изменением:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo rubyhat/marshall-ai-agent \
  --ref v0.3.0 \
  --path skills/configure-project-workflow
```

Для private repository installer использует существующие Git credentials либо
`GITHUB_TOKEN`/`GH_TOKEN`. Он устанавливает skill в
`${CODEX_HOME:-$HOME/.codex}/skills` и останавливается, если одноимённая папка
уже существует, поэтому не перезаписывает локальные изменения молча.

После установки откройте новую Codex-задачу именно в корне настраиваемого
проекта и отправьте:

```text
$configure-project-workflow
```

Если bootstrap skill уже установлен на этой машине, первый шаг можно
пропустить. После появления project routing повторную настройку можно вызывать
командой:

```text
--workflow-setup
```

Первоначальная настройка проходит поэтапно:

1. Агент объявляет обязательную safety boundary и спрашивает, нужны ли дополнительные пользовательские ограничения.
2. Проводит bounded read-only inspection папок, инструкций, безопасных manifests, repository metadata и существующей документации.
3. Создаёт только временный tracker `.codex/project-workflow.setup.json`.
4. Рекомендует workflow profile и применимые skills.
5. Проводит staged interview: по 7–10 вопросов на активный этап, сохраняя ответы и возвращаясь к незавершённым вопросам после любых detours.
6. Показывает точный mutation manifest: устанавливаемые skills, создаваемые и изменяемые файлы, aliases, templates и validation plan.
7. Только после подтверждения manifest устанавливает выбранные skills и создаёт project-specific configuration, instructions, компактную карту топологии и нужные docs.
8. Проверяет module dependencies, paths, topology coverage, aliases, managed instructions, active copies и representative dry-run routes.
9. При успешной настройке удаляет временный tracker и останавливается, не начиная обычную project task.

До подтверждения manifest skill не запускает project code, tests, builds, migrations, services или containers; не читает secrets и `.env`; не обращается к GitHub, production или другим внешним сервисам; не создаёт полную структуру `docs_ai` или `local_memory_ai`.

В продуктовый repository попадают только его собственные артефакты: managed
section в `AGENTS.md`, `.codex/project-workflow.yaml`, project topology map,
выбранные docs/memory routes, templates и каталог aliases. Канонический
workflow-kit остаётся внешним source, а active skills устанавливаются в Codex
skill directory. Другим разработчикам не нужно поддерживать или изменять этот
репозиторий.

Если настройка была прервана, повторный `$configure-project-workflow` или `--workflow-setup` продолжает её с первой незавершённой стадии. Read-only проверка уже настроенного проекта запускается через:

```text
--workflow-check
```

## Рекомендуемый основной flow

```mermaid
flowchart LR
    A["Загрузить контекст"] --> B["Сформировать outcome и scope"]
    B --> C{"Нужен frontend-flow?"}
    C -- "Да" --> D["Спроектировать interaction flow"]
    C -- "Нет" --> E["Создать task identity и tracker anchors"]
    D --> E
    E --> F["Создать task-spec"]
    F --> P{"Включена auto-delivery spec?"}
    P -- "Да" --> Q["PR и merge exact spec package"]
    P -- "Нет" --> S["Открыть новую Codex-сессию"]
    Q --> S
    S --> G{"Implementation явно разрешена?"}
    G -- "Да" --> H["Выполнить задачу"]
    G -- "Нет" --> I["Остановиться на готовой спецификации"]
    H --> J["Review и delivery"]
```

Соответствующие skills:

1. `load-project-context` — загрузить минимально достаточный контекст.
2. `shape-project-work` — согласовать outcome, scope, решения, риски и декомпозицию.
3. `design-frontend-flow` — при необходимости определить frontend interaction contract.
4. `manage-project-work` — создать или сверить Task ID, Issue, hierarchy и Project state.
5. `write-task-spec` — создать implementation-ready спецификацию и при
   включённой project policy передать только её exact documentation package в
   автоматический PR/merge fast path.
6. `execute-project-task` — выполнить одну явно разрешённую задачу и подготовить незакоммиченные изменения к local review.
7. `deliver-reviewed-change` — провести independent review, PR, bounded review cycle, merge и cleanup в пределах разрешённого endpoint.

`record-project-context` применяется в durable checkpoints по всему flow, а не только в конце. Готовая спецификация сама по себе не разрешает implementation, а выполненная implementation-задача сама по себе не разрешает commit, push или merge.

Если shaping начат через `--planning-session`, переход к implementation всегда
проходит через новую Codex-сессию. Проект может разрешить внутри planning
только узкую доставку exact specification documents; она не снимает sticky
implementation и ordinary-delivery lock.

## Дополнительные flows

### Frontend QA

```text
triage-frontend-qa
  → confirmed actionable defect
  → manage-project-work
  → write-task-spec
  → execute-project-task только при явном fix/implement request
  → deliver-reviewed-change
```

No-repro, expected behavior и unresolved ownership не должны автоматически создавать confirmed bug task или запускать реализацию.

### Анализ внешнего продукта

```text
analyze-product-reference
  → evidence и target implications
  → shape-project-work и/или design-frontend-flow
  → обычный task workflow только после отдельного решения
```

Внешний reference не является source of truth и не передаётся напрямую в implementation.

### Project context

- `load-project-context` — частая read-only ориентация перед новой или возобновлённой задачей.
- `record-project-context` — точечная запись durable или active knowledge через `skip → link → update → create`.
- `maintain-project-context` — редкий ручной аудит и отдельно подтверждённая cleanup-фаза по точному manifest.

Обычное завершение задачи не запускает broad context cleanup.

## Каталог skills

| Skill | Назначение |
| --- | --- |
| `configure-project-workflow` | Безопасно исследует проект, проводит resumable interview, создаёт project topology, устанавливает выбранные modules и формирует project workflow. |
| `load-project-context` | Загружает только контекст, необходимый для текущей содержательной задачи. |
| `record-project-context` | Сохраняет durable project knowledge без дублирования источников истины. |
| `maintain-project-context` | Аудирует, консолидирует и безопасно очищает project memory/documentation через двухфазный процесс. |
| `manage-project-work` | Управляет Task ID, hierarchy, GitHub Issues/Projects, статусами и связями task/spec/PR. |
| `shape-project-work` | Превращает идею или проблему в согласованный outcome, scope и conceptual work breakdown. |
| `write-task-spec` | Создаёт, обновляет и проверяет task specifications и при configured policy передаёт exact ready-spec package в fast path. |
| `execute-project-task` | Выполняет одну implementation-ready задачу в изолированном workspace до local-review handoff. |
| `deliver-reviewed-change` | Проводит точную задачу через reviewed flow либо строго ограниченный documentation-only fast path. |
| `design-frontend-flow` | Проектирует frontend surfaces, states, actions, recovery, responsive behavior и contract needs. |
| `triage-frontend-qa` | Воспроизводит и классифицирует один конкретный frontend-дефект. |
| `analyze-product-reference` | Исследует внешний продукт как bounded evidence и адаптирует findings к целевому проекту. |

Каждая папка skill содержит обязательный `SKILL.md`, UI metadata в `agents/openai.yaml` и только необходимые `references`, `scripts` или `assets`.

## Быстрые команды

Поддерживаемые workflow предусматривают следующие project aliases:

| Команда | Действие |
| --- | --- |
| `--workflow-setup` | Начать, продолжить или изменить guided project setup. |
| `--workflow-check` | Провести read-only audit текущей project workflow configuration. |
| `--context-audit [scope]` | Запустить только read-only аудит project context. |
| `--task-check <Task ID или Issue URL>` | Проверить согласованность одной задачи. |
| `--task-status <Task ID или Issue URL> <status>` | Изменить только статус одной точной задачи. |
| `--planning-session [scope]` | Зафиксировать sticky discussion/shaping профиль до конца текущей сессии. |
| `--shape-work <идея или task anchor>` | Запустить guided shaping без автоматических mutations. |
| `--shape-roadmap <идея или task anchor>` | Подготовить roadmap decomposition и mutation preview без full specs. |
| `--prepare-spec <Task ID или task anchor>` | Создать task-spec и при включённой policy автоматически доставить exact spec через PR. |
| `--next-spec [Epic, предыдущая задача или plan anchor]` | Проверить прошлую задачу и подготовить следующую spec из активного work graph. |
| `--accept-recommended` | Принять рекомендации только в текущем наборе вопросов. |
| `--design-flow <идея или task anchor>` | Обсудить frontend-flow без создания кода или артефакта. |
| `--qa-triage <report, URL или task anchor>` | Провести bounded triage конкретного frontend-дефекта. |
| `--reference-analysis <product, URL, artifact или вопрос>` | Выполнить chat-first анализ внешнего reference. |
| `--spec-check <Task ID или spec path>` | Провести read-only audit task-spec. |
| `--execute-task <Task ID, Issue URL или spec path>` | Выполнить локальную implementation одной ready-задачи. |
| `--deliver-task <Task ID, PR URL, spec path или current task>` | Запустить разрешённый delivery-flow одной точной задачи. |

Это plain-text соглашения проекта, а не встроенные пользовательские slash-команды Codex. Они начинают работать только после маршрутизации в project instructions и configuration. Alias не расширяет полномочия за пределы, явно описанные соответствующим skill и проектной политикой.

`--planning-session` создаёт жёсткую границу текущего разговора:
implementation и ordinary delivery требуют новой Codex-сессии. Узкая
configured доставка exact ready-spec документов может выполняться внутри
`--prepare-spec`; поздние
`--execute-task`, `--deliver-task` или эквивалентные natural-language запросы
не снимают planning/no-code lock.

Подробные contracts, защита от ошибочного порядка и рекомендуемые
последовательности собраны в
[`docs/workflow-aliases.md`](docs/workflow-aliases.md).

## Обновление и альтернативные режимы установки

Для первой настройки используйте описанный выше system `skill-installer` и
устанавливайте только `configure-project-workflow`. После manifest approval он
поможет установить выбранные modules из той же revision.

Стабильная project configuration должна сохранять exact release tag в
`workflow_kit.revision`. Для проверки ещё не выпущенного изменения допустим
полный commit SHA. Floating branch вроде `main` не считается воспроизводимой
revision.

Основной режим — `centralized`: released skills находятся в Codex skill
directory, а проект хранит только configuration и свои документы. `vendored`
подходит для осознанно изолированной project-local копии, `symlink` — только
для разработки самого workflow kit с явным portability warning.

Перед обновлением существующих copies запустите `--workflow-check`, выберите
exact target release и подтвердите предложенный reconciliation manifest.
Не удаляйте и не перезаписывайте установленную папку вслепую: system installer
намеренно отказывается писать поверх неё. Простая установка skill не создаёт
project configuration, `AGENTS.md`, topology, Task ID policy, templates или
GitHub integration.

## Версионирование и релизы

Весь repository имеет одну SemVer-версию. Один tag представляет совместимый
снимок всех skills, references, scripts и assets; отдельные skills не получают
независимые release versions.

Release Please поддерживает один Release PR:

1. обычные изменения попадают в `main` через Conventional Commit squash;
2. Release Please обновляет версию и `CHANGELOG.md`;
3. `Validate / Skills` проверяет Release PR;
4. ручной merge Release PR создаёт tag `vX.Y.Z` и опубликованный GitHub Release.

`schema_version` внутри configuration и bundled artifacts остаётся отдельной
версией формата и не заменяет SemVer workflow kit.

Подробности:

- [правила участия](CONTRIBUTING.md);
- [release runbook](docs/releasing.md);
- [релиз `v0.3.0`](https://github.com/rubyhat/marshall-ai-agent/releases/tag/v0.3.0);
- текущая development version — [version.txt](version.txt);
- история изменений — [CHANGELOG.md](CHANGELOG.md).

## Что должен определить подключающий проект

Как минимум:

- тип и назначение проекта;
- один или несколько repositories, components, их ownership, lifecycle,
  dependencies и deploy boundaries;
- project instructions и critical safety invariants;
- расположение memory, docs, task specs и templates;
- Task ID, hierarchy, Issue и Project policy;
- lifecycle statuses и разрешённые transitions;
- worktree, branch, review, merge и cleanup policy;
- localization, migration, security, privacy и production gates;
- включённые workflow modules и aliases;
- правила уточняющих вопросов и conflict/risk gate.

Эти значения не следует копировать из другого проекта без проверки.

## Границы безопасности

- Каждый skill работает только в своём scope и передаёт следующую фазу owning workflow.
- Read-only alias не разрешает исправления или внешние mutations.
- Task/spec readiness не означает разрешение на implementation.
- Implementation не означает разрешение на delivery или merge.
- Cleanup, destructive actions, production mutations и broad synchronization требуют отдельной применимой authority.
- Project-specific safety, privacy, tenant, billing, legal и deployment rules имеют приоритет над общим reusable flow.

## Структура репозитория

```text
marshall-ai-agent/
├── .github/workflows/
│   ├── release-please.yml
│   └── validate.yml
├── docs/
│   ├── releasing.md
│   └── workflow-aliases.md
├── scripts/
│   └── validate_repository.py
├── skills/
│   ├── analyze-product-reference/
│   ├── configure-project-workflow/
│   ├── deliver-reviewed-change/
│   ├── design-frontend-flow/
│   ├── execute-project-task/
│   ├── load-project-context/
│   ├── maintain-project-context/
│   ├── manage-project-work/
│   ├── record-project-context/
│   ├── shape-project-work/
│   ├── triage-frontend-qa/
│   └── write-task-spec/
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── release-please-config.json
├── version.txt
├── .gitignore
└── .release-please-manifest.json
```

## Развитие и проверка

Для создания и обновления skills используется системный `skill-creator`.

Минимальный цикл изменения:

1. Проверить trigger, exclusions и ownership boundaries.
2. Обновить `SKILL.md` и только необходимые bundled resources.
3. Убедиться, что `agents/openai.yaml` соответствует текущему skill.
4. Запустить `python3 scripts/validate_repository.py`.
5. Для изменённого skill запустить системный `quick_validate.py`.
6. Синхронизировать устанавливаемую копию только после успешной проверки.

Repository validator проверяет каталог skills, frontmatter, UI metadata,
относительные ссылки, JSON, Python syntax, portability и bundled script tests.

## Roadmap

- forward-test `configure-project-workflow` на новых single-repo и multi-repo проектах;
- стабилизировать sync/publishing policy между библиотекой и установленными copies;
- расширять schema и validation вместе с contract changes;
- дополнять reusable project templates только по подтверждённым сценариям;
- добавить сценарные проверки для single-repo, multi-repo и проектов без GitHub Projects;
- подготовить стабильный `v1.0.0` после начального forward-test.
