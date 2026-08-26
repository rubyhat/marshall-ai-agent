# Ретроспектива эксперимента `marshall-ai-agent`

- **Период активной разработки:** 2026-07-28 — 2026-08-13
- **Дата завершения эксперимента:** 2026-08-27
- **Последний опубликованный release:** `v0.10.0`
- **Статус:** archived/read-only; дальнейшая разработка и adoption прекращены
- **Решение:** lifecycle workflow через текущий набор reusable skills признан
  неудачным уровнем abstraction

## 1. Исходная гипотеза

Эксперимент начался с разумной задачи: отделить универсальные способы работы
агента от FastyShop-specific контекста и сделать их переносимыми между
проектами.

Предполагалось, что:

1. каждый этап работы можно выразить отдельным reusable skill;
2. project configuration предоставит repositories, paths, aliases, authority,
   quality gates и внешние integrations;
3. skills будут передавать друг другу проверяемые artifacts;
4. общая последовательность от shaping до delivery снизит число пропущенных
   шагов и сделает поведение воспроизводимым;
5. edge cases можно безопасно закрывать новыми contracts, validators и tests.

Результатом стали 13 skills, bootstrap/configuration layer, project aliases,
schemas, validators, templates и детализированные review/delivery state
machines.

## 2. Что было создано

На последнем active release repository содержал:

- 13 lifecycle и domain workflow skills;
- 169 tracked files;
- configuration schema и guided setup для подключаемого проекта;
- scripts и fixtures для structural/contract validation;
- единый SemVer release flow;
- 30 releases от `v0.1.0` до `v0.10.0` менее чем за 17 суток;
- 71 commit и 68 merged Pull Requests до archival documentation change.

Большая часть releases была реакцией на найденный workflow edge case,
несогласованность contract или новый failure trace. Эти числа не являются сами
по себе доказательством провала, но показывают скорость роста correction
surface относительно короткого периода реального использования.

## 3. Что оказалось полезным

Эксперимент не был бесполезным. Он дал несколько устойчивых выводов.

### Project-specific факты не должны жить в reusable procedure

Repositories, paths, production identities, localization rules, Task ID и
provider fields должны принадлежать проекту. Попытка отделить эти значения от
generic procedure была правильной по направлению, хотя итоговая configuration
стала слишком крупным workflow engine.

### Safety-critical операции требуют точности

Migration, production deploy, destructive cleanup, release publication и
другие хрупкие protocols действительно выигрывают от exact inputs,
checkpoints, idempotency, recovery и terminal verification. Ошибка была не в
самой точности, а в распространении такой точности на весь вариативный
lifecycle.

### Artifact и authority должны быть явными

Transferable report должен сохраняться как artifact, exact target и authority
нельзя угадывать, а существенная внешняя mutation требует явного разрешения.
Эти свойства полезны и без глобальной workflow-фазы.

### Review должен иметь достижимый конец

Finding обязан указывать конкретный дефект или риск. Исправляется exact finding
и проверяется correction, а не заново открывается весь процесс ради
ритуального `CLEAN`. Повтор одного спора без новой evidence требует решения, а
не нового цикла.

### Сохранность пользовательской работы важнее удобства automation

Exact manifests, отдельные worktrees, отказ от force/reset и readback внешних
mutations остаются полезными практиками, когда они пропорциональны реальному
риску.

## 4. Подтверждённые failure classes

### 4.1. Неверный уровень abstraction

Lifecycle агента — не стабильный protocol с конечным числом заранее известных
состояний. Shaping, specification, implementation и review содержат
контекстные решения, которые нельзя надёжно разложить в обязательную линейную
цепочку skills.

Попытка сделать это создала глобальную workflow-фазу. Наличие готового artifact
перестало быть достаточным: агент часто пытался доказать, был ли формально
запущен предыдущий этап, какая authority наследуется и какой skill должен
подтвердить readiness другого skill.

### 4.2. Императивность вытеснила рассуждение

Instructions описывали всё больше точных шагов, precedence rules и stop
conditions. В normal case это выглядело дисциплинированно, но при встрече с
неучтённым edge case агент переставал выбирать разумный безопасный путь:

- останавливался на формальном missing prerequisite;
- требовал повторного подтверждения уже наблюдаемого состояния;
- возвращал задачу предыдущему workflow owner;
- воспринимал неоднозначность как blocker, даже когда существовало обратимое
  решение внутри scope.

В результате skills управляли ходом рассуждения вместо передачи цели,
ограничений и полезных tools.

### 4.3. Edge-case accretion увеличивал связанность

Каждый incident приводил к новому полю configuration, дополнительной фазе,
cross-skill exception, validator либо state transition. Локальное исправление
одного поведения требовало синхронно менять несколько skills, consumer config,
project copies, global copies, aliases и tests.

Система стала хрупкой именно из-за попытки заранее сделать её исчерпывающей.
Новый edge case не просто добавлял знание — он менял общую модель authority и
готовности.

### 4.4. False blockers и необоснованные остановки

Safety gates смешались с preference и workflow ordering. Агент fail-closed
останавливал безопасную работу из-за:

- отсутствующей формальной фазы;
- incomplete persisted state, который не влиял на outcome;
- несущественного расхождения между дублирующими sources;
- исчерпанного process budget после фактически исправленного результата;
- невозможности получить идеальное доказательство вне реального риска задачи.

Такое поведение снижало самостоятельность и перекладывало обычные рабочие
решения обратно на пользователя.

### 4.5. Review и correction loops

На крупной FastyShop-задаче workflow прошёл десять полных local review verdicts
и получил 38 actionable findings. Повторные full-diff reviews находили всё более
глубокие варианты нескольких одних и тех же contract domains. Вместо раннего
возврата к границам задачи процесс продолжал correction loop.

Позднее разделение local и GitHub budgets не устранило проблему полностью:
обычный GitHub correction снова запускал полный local model review всего PR.
Один такой повторный review занял около 124 секунд и 322 092 tokens и открыл
три unrelated contract gaps после точечного two-finding correction package.

Формальные лимиты остановили цикл только после затрат, но не исправили
абстракцию, которая повторно открывала весь diff.

### 4.6. Contract и validation стали важнее outcome

Structural tests успешно доказывали наличие полей, aliases, counters, schema
fragments и transition rules. Они почти не доказывали, что агент:

- задаёт меньше лишних вопросов;
- принимает разумные обратимые решения;
- завершает работу быстрее;
- правильно ведёт себя на незнакомом edge case;
- расходует пропорциональное число tool calls и tokens.

Validation оптимизировала внутреннюю согласованность workflow kit, тогда как
главная проблема находилась в его реальном поведении.

### 4.7. Стоимость синхронизации и контекста

Одно изменение требовало согласовать canonical source, release, project copy,
global active copy, project configuration, instructions и routing docs. Агент
загружал большие contracts до начала содержательной работы и неоднократно
проверял одни и те же facts на границах skills.

Время, tokens и внимание тратились на поддержание workflow состояния, а не на
пользовательский outcome.

### 4.8. Поздние правильные принципы не исправили построенную систему

Манифест проектирования сформулировал outcome-first, самостоятельность skills,
настоящие blockers и proportional precision. Эти принципы полезны, но появились
после того, как repository уже был построен вокруг связанного lifecycle.

Приведение 13 skills и consumer configuration к manifesto потребовало бы ещё
одной крупной переработки той же abstraction. Повторные реальные задачи уже
показали системные проблемы, поэтому новый experiment cycle не оправдан.

## 5. Evidence

Основные FastyShop incident reports:

- [planning-session boundary violation and report-delivery failure](https://github.com/rubyhat/fastyshop/blob/main/docs_ai/reports/2026-07-28_agent_workflow_planning_session_boundary_incident.md);
- [specification drift and unbounded review loop](https://github.com/rubyhat/fastyshop/blob/main/docs_ai/reports/2026-08-05_fe-plat-nct-legal-01_specification-drift-review-loop-incident.md);
- [повторное полное local review внутри GitHub correction loop](https://github.com/rubyhat/fastyshop/blob/main/docs_ai/reports/2026-08-09_pr-correction-local-rereview-loop-incident.md);
- [решение о clean-slate decommission](https://github.com/rubyhat/fastyshop/issues/1109).

Дополнительное evidence находится в Git history, merged PR discussions,
release sequence и validators этого repository. Исторические documents
описывают состояние на дату своих snapshots и не являются active workflow.

## 6. Почему repository заморожен, а не удалён

Удаление скрыло бы важные failure traces и создало риск повторить тот же подход
под другим именем. Archived repository сохраняет:

- исходную гипотезу и фактическую реализацию;
- положительные engineering ideas;
- масштаб сложности, возникшей из lifecycle orchestration;
- последовательность corrections и releases;
- материал для сравнения с будущим более простым процессом.

GitHub archive делает remote repository read-only. Local clones, branches и
worktrees могут сохраняться как evidence; их cleanup не является условием
архивирования и не должен уничтожать неизвестную пользовательскую работу.

## 7. Решение и границы reuse

С даты архивирования:

- новые commits, Pull Requests, releases и workflow adoption прекращены;
- текущие 13 skills не исправляются по одному incident за раз;
- release `v0.10.0` остаётся последним published workflow kit;
- skills, aliases и configuration schema не копируются в новый процесс;
- manifesto сохраняется как historical design artifact, а не active standard;
- конкретная идея может быть использована только после независимого
  переосмысления, без наследования существующей state machine.

Final archival revision — последний commit default branch `main`, который
добавляет этот retrospective и archive notices. Его exact SHA записывается
после merge в `rubyhat/fastyshop#1109`: сам commit не может надёжно содержать
собственный hash.

## 8. Направление следующей итерации

Новая система FastyShop создаётся с нуля и не обязана переиспользовать
структуру этого repository.

Базовая модель:

1. короткий always-on `AGENTS.md`;
2. отдельные project-local Markdown guides по видам работы;
3. отсутствие обязательной глобальной workflow-фазы;
4. вход по наблюдаемому artifact/state, а не по истории вызовов;
5. самостоятельное решение безопасных и обратимых вопросов внутри scope;
6. вопросы пользователю только для decision-changing выбора или настоящей
   authority/risk boundary;
7. review exact findings с достижимыми terminal outcomes;
8. imperative runbooks только для хрупких safety/protocol operations.

Новые lifecycle agent skills в этой итерации не создаются.

## 9. Заключение

`marshall-ai-agent` был полезным, но неудачным экспериментом. Он помог увидеть,
что попытка систематизировать работу агента может сама стать главным источником
сложности: формально согласованный workflow не гарантирует хорошего
рассуждения, самостоятельности или завершения результата.

Главный вывод — стандартизировать нужно не весь путь мысли, а устойчивые
границы: outcome, sources of truth, authority, существенные risks и проверяемый
результат. Всё остальное агент должен адаптировать к текущей задаче.
