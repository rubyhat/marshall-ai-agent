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
Natural-language запрос проходит тот же capability gate, что и alias.

## Основной workflow

```text
--planning-session
  → --shape-work <идея>
  → --shape-roadmap <idea или feature anchor>
  → отдельное подтверждение точного roadmap mutation preview
  → --prepare-spec <Task ID>

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

Planning, roadmap, frontend-design, reference-analysis, ADR, task-check и
specification aliases могут разрешить только свои bounded
non-implementation workflows. `--execute-task`, `--deliver-task` и
эквивалентные natural-language запросы не отменяют профиль. Агент
останавливается до mutations и требует новую сессию.

### `--shape-work <идея или task anchor>`

Запускает `shape-project-work` для одной идеи, функции, проблемы, research
initiative или крупной задачи.

Результат: согласованный outcome, scope, решения, риски и shaping verdict.
Alias не создаёт файлы, Issues или полноценную specification.

### `--shape-roadmap <идея или task anchor>`

Запускает roadmap shaping и conceptual decomposition:

- Epic, Features/Stories и implementation-task candidates;
- repository или deployable ownership;
- dependencies, ordering и parallel tracks;
- acceptance outline, integration gates и риски.

После разрешения decision-changing вопросов агент показывает точный preview
предлагаемых tracker и optional durable-document mutations. Создание Task IDs,
Issues, Project items или coordination artifact начинается только после
отдельного подтверждения этого preview. Полные task-spec не создаются.

Отдельный coordination artifact нужен только при уникальной durable ценности,
например для shared contract, rollout order или cross-repository decisions. Не
следует дублировать в нём Issue bodies и будущие task-spec.

### `--prepare-spec <Task ID или exact task anchor>`

Запускает единый многошаговый workflow:

1. проверка Task identity, roadmap position и dependency stability;
2. bounded shaping точной задачи;
3. объяснение предлагаемого направления;
4. decision-changing questions;
5. создание требуемых project anchors;
6. создание и проверка full или lightweight task specification;
7. linkage и разрешённый operational status;
8. стандартизированный specification handoff.

Alias является явным запросом на specification, поэтому после разрешения
вопросов повторное подтверждение «создавать ли spec» не требуется. Alias не
разрешает implementation или delivery.

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
   `--prepare-spec`.

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

## Implementation и delivery

### `--execute-task <Task ID, Issue URL или spec path>`

Команда доступна только в разговоре без активного planning/no-code
implementation lock. Если такой lock существует, агент останавливается до
task lookup, status transition, Git, dependency и file mutations и рекомендует
новую сессию.

Выполняет одну exact implementation-ready задачу через
`execute-project-task`:

- проверяет `Ready for implementation`;
- выбирает только затронутые repositories;
- создаёт или возобновляет isolated task workspaces;
- защищает параллельную работу;
- пишет task-scoped код;
- выполняет relevant quality gates;
- передаёт незакоммиченные изменения на independent local review.

Не разрешает commit, push, PR, merge, deploy, production mutation или cleanup.

### `--deliver-task <Task ID, Issue URL, PR URL, spec path или current task>`

Команда доступна только в разговоре без активного planning/no-delivery lock.
Конфликтующий профиль блокирует review fixes, commit, push, PR actions,
heartbeat, merge, tracker mutations и cleanup.

Проводит точную задачу через configured independent review и delivery flow.
Точная конечная точка может быть сужена дополнительным текстом пользователя.

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

## Architecture decisions

### `--adr-review <ADR или task anchor>`

Запускает read-only necessity или applicability review через
`record-architecture-decision`.

Агент проверяет semantic status, scope, assumptions, decision drivers, review
triggers и текущие evidence. Результат `review required` или `unclear`
останавливает зависимую shaping/specification/implementation границу; команда
не изменяет ADR, index, task или project context.

### `--record-adr <decision anchor>`

Запускает guided lifecycle workflow одного материального архитектурного
решения. Команда может подготовить proposal, зафиксировать подтверждённое
accept/reject решение, выполнить non-material clarification, deprecation или
supersession в пределах project-configured authority.

Alias не означает автоматическое принятие решения. Для material изменения
accepted ADR создаётся replacement ADR, старый получает semantic state
`superseded` и backlink, а исходное rationale не переписывается. Persistence
выполняется через `record-project-context` только для точного ADR/index
mutation set.

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
tracker artifacts. Затем каждая implementation task обсуждается через
`--prepare-spec`, а продолжение уже активной последовательности — через
`--next-spec`.

### Материальное архитектурное решение

```text
--adr-review <ADR или task anchor>
--record-adr <decision anchor>
```

Первую команду используют для read-only проверки. Вторая требуется только
когда решение действительно достойно ADR или существующий ADR нужно
уточнить, отклонить, deprecated либо supersede.

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
- ADR paths, identifiers, semantic status mapping, decision authority и
  lifecycle policy;
- worktree, branch, test и delivery policy;
- production, security, privacy и domain restrictions.

Alias, owning skill или dependency, не включённые в project configuration,
считаются недоступными. Агент должен предложить `--workflow-setup` или другой
явный способ конфигурации, а не имитировать отсутствующий workflow.

## Переход с workflow schema v1

Релиз с guarded aliases использует `schema_version: 2`. Проект на schema v1
должен запустить `--workflow-setup` в режиме reconfigure и подтвердить manifest,
который:

- меняет `schema_version` на `2`;
- добавляет обязательный `commands.sequence_guard`;
- включает только aliases выбранных modules;
- устанавливает `shape-project-work` как dependency для `write-task-spec`.

До завершения migration нельзя считать новые aliases полностью настроенными.

Незавершённый `.codex/project-workflow.setup.json` schema v1 также требует
явной migration preview: сохранить подтверждённые ответы, добавить точный
`modules.enabled_aliases` и только после подтверждения изменить его
`schema_version` на `2`.
