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
- материализует provisional `Ready for implementation` до review manifest;
- формирует точный allowlisted publication manifest;
- запускает fresh independent bounded spec review только через canonical
  authoritative-session runner;
- объединяет все terminal findings stable attempt и разрешает один technical
  retry только после settled отсутствия authoritative result;
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
  current capture-contract provenance, merged canonical revision и ancestry
  specification-owner authority base;
- для component repository с отдельной Git history проверяет recorded tuple из
  Task ID, spec-owner repository, canonical spec path, merged revision,
  publication attempt, result hash и matched reviewer sessions без требования
  невозможной общей ancestry;
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

До создания PR baseline, local counter и local history сохраняются одним
machine-readable state block в текущей Codex-задаче и перечитываются после
каждого local transition. При создании heartbeat нового PR этот state
копируется без пересборки, после чего GitHub counter и history данного PR
инициализируются нулём и пустым списком. Другая сессия без доказуемого state не
продолжает существующий review автоматически.

Перед каждой следующей GitHub generation workflow повторно читает authoritative
local counter/history из task block, проверяет тот же baseline и обновляет ими
heartbeat exact PR. PR-owned GitHub counter, history, fingerprints и technical
state при этом сохраняются без изменений и не копируются обратно в task block
либо в другой PR.

В multi-repository delivery каждый PR имеет собственный GitHub correction
counter и ordered history. Первый review generation нового PR начинается с
нуля; новый head того же PR сохраняет его counter; другой PR начинает отдельные
пять раундов с нуля. Counters, histories, dismissed-finding fingerprints и
heartbeat state разных PR не синхронизируются.

Пока review активен, GitHub state хранится в heartbeat точного PR. Перед
отправкой review request workflow сначала создаёт и перечитывает provisional
heartbeat этого PR, затем добавляет в него доказанный request identity и снова
перечитывает state. Поэтому между remote request и мониторингом не возникает
неперсистентного состояния. Тот же переход обязателен для initial request,
technical retry и contextual re-review.

При clean review, исчерпании budget или другом review-terminal state открытого
PR workflow сохраняет terminal reason и отдельный `terminal_head_sha` прямо в
heartbeat точного PR, перечитывает state и ставит этот heartbeat на pause. Он не
создаёт terminal snapshot и не переносит PR-owned state в текущую Codex-задачу.
На неизменённом terminal head workflow возвращает уже зафиксированный outcome
без нового review request. Авторизованный более поздний head того же PR повторно
активирует тот же heartbeat с сохранёнными GitHub counter, history и
fingerprints. Перед workflow-owned push, который изменит head, этот exact
heartbeat обязательно сохраняется и перечитывается в paused finding state;
поэтому monitor не может ошибочно финализировать controlled push как внешний
`head_mismatch`. Удалить heartbeat можно только после provider-доказательства,
что точный PR merged или closed. Если identity PR или обязательный state нельзя
доказать, heartbeat остаётся paused без удаления и без выдуманного state.

Все terminal branches выбирают reason из единой матрицы и вызывают
`finalize_codex_review_state`; pause/reactivation/delete правила не копируются
в отдельные ветки workflow.

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
`schema_version: 4`. Он требует guarded aliases и sequence rules, а для
`publish-planning-change` — authoritative-session runner, полный bound-review
provenance contract и completion gates. Legacy baseline остаётся audit input и
не разрешает implementation workspace. Другие project schema versions не
считаются частично настроенными и не
получают compatibility defaults: `--workflow-check` возвращает setup drift, а
`--publish-spec` останавливается до mutations. Исправление выполняется только
через подтверждённый `--workflow-setup` reconfiguration manifest.

`schema_version` незавершённого `.codex/project-workflow.setup.json` является
версией отдельного setup-state формата и не обозначает поддерживаемую версию
project configuration.

### Историческая заметка: workflow kit v0.7.0

В v0.7.0 тогдашний schema-v3 contract для `publish-planning-change` требовал
положительный `planning_publication.independent_review.max_correction_rounds`;
значение по умолчанию для новой конфигурации — `5`. После пятого пакета
исправлений corrected head всё ещё проходит обязательное ревью, но новый пакет
изменений уже не начинается: workflow останавливается с анализом цикла.

В соответствующем release-переходе проект с выбранным
`publish-planning-change` синхронизировал все skills на exact tag v0.7.0,
использовал тогдашний `schema_version: 3` и материализовал
`max_correction_rounds: 5`. Это описание сохраняется только как release
history и не является инструкцией для current schema 4.

### Историческая заметка: workflow kit v0.7.2

В v0.7.2 тогдашний schema-v3 contract дополнительно требовал
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
В том contract content-changing correction сначала понижала verdict старого
clean-reviewed head с `Ready for implementation` до `Spec ready`. Schema 4
отменила этот downgrade/re-promotion lifecycle. Если в planning worktree
остаётся excluded dirty path, workflow останавливается до checkpoint и выдаёт
точный preservation/recovery handoff, не включая и не удаляя чужое изменение.

При обновлении всего набора skills на exact tag v0.7.2 в этот объект нужно явно
добавить разрешение checkpoint commit, обязательность deterministic checks и
exact manifest, а `push_before_clean_review` установить в `false`. Отсутствующий
или неполный объект делает `--publish-spec` невалидным до mutations.

### Переход на schema 4

Schema 4 материализует provisional target verdict до первого review и удаляет
verdict-only review. Canonical runner связывает каждую invocation с exact outer
session UUID, читает terminal JSON только из matched review child, ждёт
terminal settlement и stable rescans, объединяет findings всех invocations и
сохраняет normalized result hash, publication attempt и matched session set.

`legacy_ready_adoption.enabled` обязан быть `false`; implementation evidence и
workspace creation принимают только complete ordinary schema-4 publication.
Old evidence получает typed `publication_upgrade_required` и exact
`--publish-spec <Task ID>`. Cutover понижает только exact operational
`Готово к реализации`; остальные configured statuses остаются audit-only и не
откатываются. Direct `--publish-spec` не принимает schema 3; existing project
переходит one-way через отдельно проверенный workflow-sync implementation PR.

### Переход на workflow kit v0.8.2

В v0.8.2 schema-v3 contract для выбранного `deliver-reviewed-change` требует
корневую секцию `review` с четырьмя полными группами:

```json
{
  "review": {
    "scope_binding": {
      "exact_task_contract_required": true,
      "required_context": [
        "task_id",
        "issue",
        "specification_or_equivalent_contract",
        "specification_revision_or_not_applicable",
        "acceptance_criteria",
        "non_goals",
        "repositories",
        "worktrees",
        "branches",
        "target_branches",
        "initial_diff_manifest",
        "initial_diff_stats"
      ],
      "initial_diff_baseline_required": true,
      "baseline_immutable_for_delivery_attempt": true,
      "actionable_finding_requires_concrete_current_task_failure": true,
      "speculative_or_general_hardening_is_non_actionable": true,
      "material_scope_or_contract_change_returns_to_owner": true,
      "material_cumulative_diff_growth_stops_for_analysis": true
    },
    "correction_policy": {
      "round_unit": "review_driven_correction_package",
      "separate_local_and_github_counters": true,
      "multiple_findings_in_one_result_consume_one_round": true,
      "technical_retry_consumes_no_round": true,
      "unchanged_head_contextual_rereview_consumes_no_round": true,
      "final_allowed_round_receives_review": true,
      "next_required_round_stops_before_mutation": true,
      "new_head_resets_request_attempts_only": true,
      "ordered_history_required": true,
      "pre_pr_state_store": "current_codex_task",
      "persist_and_read_back_after_each_local_transition": true,
      "refresh_local_state_before_each_github_generation": true,
      "github_correction_budget_scope": "pull_request",
      "github_counter_owner": "exact_pr_state",
      "github_state_store": "exact_pr_heartbeat",
      "open_pull_request_terminal_state_pauses_heartbeat": true,
      "same_pull_request_resume_reactivates_heartbeat": true,
      "owned_head_changing_push_requires_paused_heartbeat": true,
      "heartbeat_deletion_requires_pull_request_terminal": true,
      "terminal_head_records_observed_pr_head": true,
      "terminal_finalization_procedure": "finalize_codex_review_state",
      "terminal_state_matrix_required": true,
      "terminal_rules_must_not_be_duplicated": true,
      "new_pull_request_starts_github_counter_at_zero": true,
      "different_pull_requests_do_not_share_counters_or_histories": true,
      "different_pull_requests_do_not_share_terminal_state": true,
      "github_dismissed_finding_fingerprints_scope": "pull_request",
      "github_heartbeat_state_scope": "pull_request",
      "github_heartbeat_exists_before_review_request": true,
      "same_terminal_head_forbids_new_request": true,
      "different_conversation_requires_proven_state": true,
      "resume_requires_provable_counters_and_history": true,
      "lost_history_stops_delivery": true,
      "bounded_cycle_analysis_required": true
    },
    "local": {
      "max_correction_rounds": 5,
      "fresh_review_after_each_correction_package": true
    },
    "github_codex": {
      "max_correction_rounds": 5,
      "fresh_generation_after_each_correction_package": true,
      "new_head_resets_request_budget_only": true,
      "heartbeat": {
        "delete_on_review_terminal_state": false,
        "delete_after_pr_terminal": true
      },
      "state_machine": {
        "states": [
          "request_not_created",
          "request_pending",
          "not_started",
          "in_progress",
          "findings_received",
          "scope_disagreement",
          "transient_error",
          "clean",
          "stopped",
          "terminal",
          "pr_terminal",
          "head_mismatch",
          "unclassified_response"
        ]
      },
      "post_clean": {
        "delete_review_heartbeat_immediately": false
      }
    }
  }
}
```

Эти три вложенные группы обязательны: schema не принимает удаление heartbeat на
review-terminal transition, требует его удаление после доказанного
`pr_terminal` и полный lifecycle states для provisional request, monitoring и
terminal finalization.

Этот migration contract публикуется Release Please в v0.8.2. До появления
exact tag v0.8.2 установку по этой инструкции не выполнять; unreleased testing
разрешён только по полному commit SHA.

Для тогдашнего schema-v3 проекта release-переход требовал подтверждённый
`--workflow-setup`: exact tag v0.8.2, `workflow_kit.revision: v0.8.2`,
материализовать указанный `review` contract
и выполнить validation записанной revision, активных skill copies и
project configuration. Это описание сохраняется как release history; current
reconfiguration обязана создать полный schema-4 candidate и не может сохранять
schema 3 либо рассчитывать на compatibility defaults.

Если reconfiguration нельзя завершить, `--deliver-task` остаётся fail-closed до
устранения drift. Безопасный откат требует вернуть и project configuration, и
весь выбранный набор skills на один прежний exact release tag; удалять `review`
при оставленных skills v0.8.2 или смешивать revisions нельзя.
