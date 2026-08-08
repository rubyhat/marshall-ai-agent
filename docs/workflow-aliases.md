# Быстрые команды workflow kit

## Что такое alias

Workflow alias — короткий plain-text trigger в формате
`--lowercase-kebab-case`. Пользователь отправляет его обычным сообщением, а
project instructions и configuration маршрутизируют запрос в owning skill.

Alias:

- не является shell-командой;
- не является встроенной slash-командой Codex;
- не заменяет `SKILL.md` полным скрытым промтом;
- не расширяет полномочия owning skill;
- не отменяет readiness, safety и approval gates;
- начинает работать только после включения в конкретном проекте.

Точная процедура хранится в owning `SKILL.md`. Project-specific значения,
prerequisites и разрешённые mutations находятся в
`.codex/project-workflow.yaml`. Project-local каталог команд должен ссылаться
на эти источники, а не копировать их целиком.

## Защита последовательности

Перед выполнением каждого alias агент обязан определить текущую фазу workflow
и проверить:

- активные sticky constraints текущего разговора;
- capability запрошенного действия;
- точный idea, Task, Issue, spec или PR anchor;
- readiness текущей фазы;
- обязательные зависимости и их стабильность;
- наличие owning skill и необходимых modules;
- разрешённые alias mutations;
- отсутствие конфликта с активными решениями, архитектурой и safety policy.

Если команда преждевременна, устарела, неоднозначна или вызвана не в той фазе,
агент должен остановиться до mutations и сообщить:

1. какой alias получен;
2. какое текущее состояние установлено;
3. какой prerequisite не выполнен;
4. какой alias или шаг рекомендуется следующим;
5. что должно произойти, чтобы исходную команду можно было безопасно повторить.

Агент не должен механически требовать завершения всех предыдущих
implementation-задач. Downstream specification блокируется только тогда,
когда незавершённая зависимость оставляет outcome, contract, scope, ownership
или acceptance behavior существенно нестабильными.

Sticky negative constraint проверяется раньше alias authority и readiness.
Поздний alias может сузить полномочия, но не может неявно снять
planning/no-code/no-implementation/no-delivery/read-only ограничение.
Отдельно настроенный `--publish-spec` может разрешить только публикацию одного
exact planning-artifact manifest и не снимает planning lock для implementation
или ordinary delivery.
Natural-language запрос проходит тот же capability gate, что и alias.

## Основной workflow

```text
--planning-session
  → --shape-work <идея>
  → --shape-roadmap <сформированный outcome или exact anchor>
  → отдельное подтверждение semantic roadmap mutation preview
  → --prepare-spec <Task ID>
  → --publish-spec <Task ID>

=== ДЛЯ РЕАЛИЗАЦИИ КАЖДОЙ SPEC НУЖНА НОВАЯ СЕССИЯ CODEX ===

--execute-task <Task ID>
  → --deliver-task <Task ID>

=== ВОЗВРАТ В ИСХОДНУЮ PLANNING-СЕССИЮ ===

--next-spec [Epic, previous Task или plan anchor]
  ↺ следующая implementation снова выполняется в отдельной сессии
```

`--accept-recommended` можно использовать внутри текущего clarification round.
Domain-команды подключаются только при применимом типе работы.

## Planning и work definition

### `--planning-session [scope]`

Устанавливает для текущего разговора discussion/shaping-oriented профиль.

Разрешает обсуждение идей, архитектуры, бизнес-процессов, roadmap,
декомпозиции и подготовки спецификаций. Не разрешает сам по себе создание
файлов, Issues, task-spec, кода или delivery actions.

Это workflow profile, а не переключатель системного Plan mode Codex. Профиль
является sticky constraint и действует до конца текущего разговора.

Planning, roadmap, frontend-design, reference-analysis, task-check и
specification aliases могут разрешить только свои bounded
non-implementation workflows. Настроенный `--publish-spec` может провести
exact reviewed specification через отдельный planning-publication flow, не
разрешая код. `--execute-task`, `--deliver-task` и
эквивалентные natural-language запросы не отменяют профиль. Агент
останавливается до mutations и требует новую сессию.

### `--shape-work <идея или task anchor>`

Запускает `shape-project-work` для одной идеи, функции, проблемы, research
initiative или крупной задачи.

Результат: согласованный outcome, scope, решения, риски и shaping verdict.
Alias не создаёт файлы, Issues или полноценную specification.

### `--shape-roadmap <сформированный outcome или exact anchor>`

Получает уже согласованный результат `--shape-work` и одной итерацией решает,
как оформить его в tracker:

- Epic, Features/Stories и implementation-task candidates;
- repository или deployable ownership;
- dependencies, ordering и parallel tracks;
- acceptance outline, integration gates и риски.

Alias не переоткрывает вопрос «что делаем?». Если outcome, scope, решения или
риски ещё нестабильны, агент останавливается и рекомендует `--shape-work`.
Уточняются только границы Epic/Features/Tasks, их описание, ownership,
dependencies, порядок и integration gates; Epic и все дочерние задачи
показываются как единое целое.

После вопросов агент показывает один exact semantic mutation preview с
устойчивым roadmap-operation key. Для каждого узла он содержит create/update
action, стабильный semantic key, title, полный concise Issue body, type,
parent, repository, dependencies, Project fields и status. Будущие GitHub
Issue numbers и окончательные Task IDs не угадываются. После одного отдельного
подтверждения `manage-project-work` создаёт или обновляет graph в topological
order одновременно по hierarchy (`parent → child`) и dependencies
(`predecessor → dependent`) и возвращает mapping
`semantic key → Task ID → Issue`.

Для любой новой задачи с provider-number-derived identity Issue создаётся
первым с детерминированным semantic marker, одинаковым при каждом retry. После
ответа GitHub агент получает неизменяемый Issue number, механически строит из
configured prefix/domain и этого номера финальный Task ID, сразу обновляет
Issue и продолжает hierarchy/Project mutations. Существующие legacy Task IDs
не переименовываются.

Если reconciliation меняет смысл, количество задач, create/update action,
title/body scope, parent, repository, dependencies или Project fields, нужен
новый preview. Выданный GitHub номер и Task ID, механически полученный из него,
повторного подтверждения не требуют.

Alias не создаёт локальные roadmap, memory, coordination или documentation
files и не создаёт full task-spec. GitHub Issues и Project остаются roadmap
source of truth. Shared contract, rollout или cross-repository deliverable
оформляется отдельной tracked task, а детали позже фиксируются в её task-spec.

### `--prepare-spec <Task ID или exact task anchor>`

Запускает единый многошаговый workflow:

1. проверка Task identity, roadmap position и dependency stability;
2. bounded shaping точной задачи;
3. объяснение предлагаемого направления;
4. decision-changing questions;
5. создание требуемых project anchors;
6. создание и проверка full или lightweight task specification;
7. pre-publication linkage и разрешённый operational status;
8. стандартизированный specification handoff.

Alias является явным запросом на specification, поэтому после разрешения
вопросов повторное подтверждение «создавать ли spec» не требуется. Alias не
разрешает Git publication, implementation или delivery. Если настроен
`publish-planning-change`, tracked spec создаётся в isolated planning worktree,
а результатом авторской проверки становится максимум `Spec ready`; следующий
шаг — `--publish-spec <Task ID>`.

### `--next-spec [Epic, предыдущая Task или exact plan anchor]`

Продолжает активную последовательность подготовки specifications без
обязательного повторения Task ID завершённой задачи.

Агент:

1. определяет последнюю задачу, для которой в текущем разговоре была
   подготовлена specification, и её канонический Epic/work graph;
2. использует optional anchor только для безопасного разрешения
   неоднозначности;
3. через `manage-project-work` read-only проверяет completion state, Issue,
   Project и связанные PR предыдущей задачи, но ничего в них не исправляет;
4. выбирает следующую незавершённую и разблокированную задачу по dependency
   graph, а не по Task ID;
5. при одном кандидате объясняет предлагаемое направление и задаёт
   decision-changing вопросы;
6. при нескольких равноправных parallel candidates показывает варианты,
   рекомендует один и ждёт выбор;
7. после ответов выполняет тот же specification handoff, что и
   `--prepare-spec`, включая isolated planning workspace и последующий
   `--publish-spec`, когда planning publication настроена.

Если active Epic или предыдущая задача не определяются однозначно, агент не
ищет просто «последнюю» задачу во всём проекте, а запрашивает exact anchor.
Незавершённая предыдущая задача блокирует продолжение только когда следующий
outcome, contract, scope, ownership или acceptance behavior остаются
существенно нестабильными.

Alias является явным разрешением создать следующую specification после
уточняющих вопросов. Он не разрешает implementation, delivery, изменение
статуса предыдущей задачи или автоматическое исправление completion evidence.

### `--accept-recommended`

Выбирает каждый явно рекомендованный вариант только в последнем текущем
неотвеченном пронумерованном наборе вопросов.

Alias не отвечает на factual questions, не распространяется на будущие
вопросы, не принимает неописанные material risks и не выдаёт дополнительные
разрешения. Если у вопроса нет однозначной рекомендации, агент отдельно
уточняет только его.

### `--spec-check <Task ID или spec path>`

Запускает read-only completeness и readiness audit через `write-task-spec`.
Не изменяет specification, tracker или status.

### `--publish-spec <Task ID, Issue URL или spec path>`

Запускает `publish-planning-change` для одной exact specification:

- проверяет isolated planning workspace и полный diff;
- формирует точный allowlisted publication manifest;
- запускает fresh independent bounded spec review;
- возвращает реальные content findings в `write-task-spec` и повторяет review
  только после изменений;
- выполняет deterministic documentation gates;
- делает intentional commit и push без force;
- создаёт или сверяет Pull Request в canonical target branch;
- ждёт обязательные checks и merge только при configured authority;
- проверяет merged canonical revision, обновляет exact task linkage/status,
  синхронизирует и очищает planning workspace.

Alias можно использовать в активной planning-сессии только через отдельную
capability `planning_artifact_publication`. Он не снимает planning lock, не
разрешает implementation, обычный `--deliver-task`, закрытие implementation
Issue, release, deploy или production mutations. Более узкий запрос ограничивает
endpoint, но unmerged PR не делает specification доступной для implementation.

## Implementation и delivery

### `--execute-task <Task ID, Issue URL или spec path>`

Команда доступна только в разговоре без активного planning/no-code
implementation lock. Если такой lock существует, агент останавливается до
task lookup, status transition, Git, dependency и file mutations и рекомендует
новую сессию.

Выполняет одну exact implementation-ready задачу через
`execute-project-task`:

- проверяет `Ready for implementation`;
- при configured planning publication проверяет independent spec review,
  merged canonical revision и ancestry specification-owner authority base;
- для component repository с отдельной Git history проверяет recorded tuple из
  Task ID, spec-owner repository, canonical spec path и merged revision без
  требования невозможной общей ancestry;
- после успешного readiness переводит exact task в configured implementation
  status и только затем создаёт или возобновляет worktree и feature branch;
- выбирает только затронутые repositories;
- создаёт или возобновляет isolated task workspaces;
- защищает параллельную работу;
- пишет task-scoped код;
- выполняет relevant quality gates;
- передаёт незакоммиченные изменения на independent local review.

Когда canonical planning publication настроена и во время implementation
меняется task-owned specification или annex, предыдущий publication record
сразу перестаёт подтверждать readiness. Агент останавливает task-code edits,
проводит correction через `write-task-spec` и `publish-planning-change`, затем
повторяет полный readiness preflight по новому persisted record. Проверка
сравнивает полный path/blob-OID manifest record не только со старым merged
revision, но и с текущим specification-owner authority base. Локального
изменения spec, verdict `Spec ready` или непривязанного merged PR недостаточно
для продолжения.

Не разрешает commit, push, PR, merge, deploy, production mutation или cleanup.

### `--deliver-task <Task ID, Issue URL, PR URL, spec path или current task>`

Команда доступна только в разговоре без активного planning/no-delivery lock.
Конфликтующий профиль блокирует review fixes, commit, push, PR actions,
heartbeat, merge, tracker mutations и cleanup.

Проводит точную задачу через configured independent review и delivery flow.
Точная конечная точка может быть сужена дополнительным текстом пользователя.

До первого local review фиксирует immutable delivery baseline: Task ID,
specification или эквивалентный contract, acceptance criteria, non-goals,
начальный полный diff manifest и статистику. Reviewer получает этот bounded
контекст без истории реализации и должен связать actionable finding с
конкретным дефектом текущей задачи или обязательным достоверным риском.

Local independent review и GitHub Pull Request review имеют отдельные bounded
циклы исправлений — не более пяти correction packages каждый.
Один пакет может закрывать несколько findings одного review result. Технический
retry, clean review, ответ без изменения кода и contextual re-review
неизменённого head раунд не расходуют. Новый PR head обнуляет только technical
request budget, но не GitHub correction counter и не историю.

До создания PR baseline, оба счётчика и истории сохраняются одним
machine-readable state block в текущей Codex-задаче и перечитываются после
каждого local transition. При старте GitHub review этот state без пересборки
копируется в heartbeat. Другая сессия без доказуемого state не обнуляет и не
продолжает counters автоматически.

Head после пятого разрешённого пакета всё равно проходит review. Если ему нужна
шестая правка, workflow останавливается до edit, commit, push или нового review
request и возвращает cycle analysis: исходный и текущий diff, все findings и
пакеты, review-only growth, повторяющиеся категории и признаки scope drift.
General hardening, недоказанные edge cases, unrelated defects и необъяснимый
рост diff не расширяют задачу автоматически.

Не разрешает bypass review/CI, force-push, deploy, production data mutation или
работу с unrelated PR.

## Task management

### `--task-check <Task ID или Issue URL>`

Read-only проверка identity, hierarchy, tracker fields, status и links одной
задачи.

### `--task-status <Task ID или Issue URL> <status>`

Меняет только status одной точной задачи после configured transition check.

## Context

### `--context-audit [scope]`

Запускает только read-only context audit. Cleanup требует отдельного exact
manifest и подтверждения.

## Domain workflows

### `--design-flow <идея или task anchor>`

Проектирует или проверяет frontend interaction flow без создания task-spec,
visual artifact или кода.

### `--qa-triage <report, URL или task anchor>`

Воспроизводит и классифицирует один frontend defect. Не разрешает
implementation или production data mutation.

### `--reference-analysis <product, URL, artifact или вопрос>`

Выполняет bounded external product-reference analysis. По умолчанию возвращает
chat-first результат без project artifacts.

## Настройка workflow

### `--workflow-setup`

Начинает, продолжает или изменяет guided project setup. Final mutations требуют
approval точного manifest.

### `--workflow-check`

Проводит read-only audit установленного workflow kit.

## Рекомендуемые сценарии

### Новая функция или Epic

```text
--planning-session
--shape-work <идея>
--shape-roadmap <сформированная функция>
```

После roadmap preview пользователь отдельно подтверждает создание configured
tracker graph. Затем каждая implementation task обсуждается через
`--prepare-spec`, а продолжение уже активной последовательности — через
`--next-spec`.

### Подготовка следующей task-spec

```text
--next-spec
```

Если текущая planning continuity неоднозначна:

```text
--next-spec <Epic, previous Task или plan anchor>
```

Для первой или заранее выбранной точной задачи по-прежнему используется:

```text
--prepare-spec <Task ID>
```

Если рекомендации подходят:

```text
--accept-recommended
```

После создания spec агент обязан показать Task ID и title, Issue, spec path,
repositories, content verdict, Project status, expected outcome, следующий
task/action и material warnings.

Если настроена planning publication, следующий шаг после `Spec ready`:

```text
--publish-spec <Task ID>
```

Только после independent review и merge spec в canonical branch задача может
получить operational implementation-ready status.

### Реализация готовой задачи

В новой task session достаточно:

```text
--execute-task <Task ID>
```

Отдельный implementation-session bootstrap обычно не нужен: Task ID и spec
должны определить repositories, worktrees, constraints и quality gates.

После локальной реализации:

```text
--deliver-task <Task ID>
```

### Ошибочный вызов

Если `--execute-task` отправлен до готовой specification, агент не должен
начинать код. Он сообщает текущий verdict и рекомендует, например:

```text
--prepare-spec <Task ID>
```

Если specification готова локально, но не опубликована в canonical branch,
агент останавливается до task lookup и workspace mutations и рекомендует:

```text
--publish-spec <Task ID>
```

Если `--deliver-task` отправлен до завершённой implementation и local-review
handoff, агент сообщает недостающий checkpoint и рекомендует сначала:

```text
--execute-task <Task ID>
```

Если `--execute-task` или `--deliver-task` отправлен в активной
planning-сессии, readiness не проверяется и mutations не выполняются. Агент
называет активный профиль и просит открыть новую сессию.

## Что настраивается в проекте

Reusable aliases сохраняют одинаковый смысл, но конкретный проект определяет:

- включённые modules и aliases;
- session profiles, capabilities, lifetime, precedence и release semantics;
- persistent report destinations и output-form rules;
- repositories, services и ownership;
- Task ID и hierarchy policy;
- task tracker, fields и statuses;
- spec templates и readiness gates;
- canonical spec owner, default `docs_ai/tasks`, planning worktree,
  independent spec review и publication policy;
- worktree, branch, test и delivery policy;
- production, security, privacy и domain restrictions.

Alias, owning skill или dependency, не включённые в project configuration,
считаются недоступными. Агент должен предложить `--workflow-setup` или другой
явный способ конфигурации, а не имитировать отсутствующий workflow.

## Текущий workflow schema contract

Workflow kit поддерживает один актуальный формат project configuration:
`schema_version: 3`. Он требует guarded aliases и sequence rules, а для
`publish-planning-change` — полный bound-review evidence contract и completion
gates. Другие project schema versions не считаются частично настроенными и не
получают compatibility defaults: `--workflow-check` возвращает setup drift, а
`--publish-spec` останавливается до mutations. Исправление выполняется только
через подтверждённый `--workflow-setup` reconfiguration manifest.

`schema_version` незавершённого `.codex/project-workflow.setup.json` является
версией отдельного setup-state формата и не обозначает поддерживаемую версию
project configuration.

### Переход на workflow kit v0.7.0

В v0.7.0 текущий schema-v3 contract для `publish-planning-change` требует
положительный `planning_publication.independent_review.max_correction_rounds`;
значение по умолчанию для новой конфигурации — `5`. После пятого пакета
исправлений corrected head всё ещё проходит обязательное ревью, но новый пакет
изменений уже не начинается: workflow останавливается с анализом цикла.

Проект с выбранным `publish-planning-change`, в конфигурации которого поля нет,
считается невалидным и должен быть прямо перенастроен: синхронизировать все
выбранные skills на один exact tag v0.7.0, сохранить `schema_version: 3`, добавить
`max_correction_rounds: 5` и выполнить validation. Compatibility layer и
автоматическая миграция не предусмотрены. Откат безопасен только совместно для
конфигурации и всего набора skills на один прежний exact release tag.

### Переход на workflow kit v0.7.2

В v0.7.2 schema-v3 contract дополнительно требует
`planning_publication.independent_review.committed_correction_review`. Текущая
поддерживаемая стратегия — `local_checkpoint_committed_base_diff`: после
correction package после non-clean review для publication manifest, уже имеющего
собственный commit в planning branch, агент выполняет deterministic checks,
создаёт exact-manifest локальный checkpoint commit, проверяет его полным diff от
canonical base и не пушит до clean review. До первого independent review полный
uncommitted candidate разрешён и при наличии раннего in-scope commit; для него,
как и для ещё не закоммиченного manifest, обязательна path/blob-OID equivalence.
Объект materialized при setup как dormant policy, чтобы не менять конфигурацию
посреди publication; наличие объекта само по себе не активирует checkpoint path.
Content-changing correction сначала понижает verdict старого clean-reviewed
head с `Ready for implementation` до `Spec ready`. Если в planning worktree
остаётся excluded dirty path, workflow останавливается до checkpoint и выдаёт
точный preservation/recovery handoff, не включая и не удаляя чужое изменение.

При обновлении всего набора skills на exact tag v0.7.2 в этот объект нужно явно
добавить разрешение checkpoint commit, обязательность deterministic checks и
exact manifest, а `push_before_clean_review` установить в `false`. Отсутствующий
или неполный объект делает `--publish-spec` невалидным до mutations.
