# AGENTS.md

## Назначение репозитория

`marshall-ai-agent` — канонический source repository переиспользуемых Codex
skills. Папка `skills/` хранит reusable behavior; активные копии в
`~/.codex/skills` и project-local copies являются installations, а не
источниками истины.

Human-facing документация репозитория ведётся на русском языке. Reusable
`SKILL.md`, references, scripts, schemas и templates должны оставаться
project-neutral; для процедурных инструкций сохранять текущий английский язык,
если пользователь явно не утвердил общую смену политики.

## Создание и изменение skills

Для создания или содержательного изменения skill обязательно использовать
системный `skill-creator`:

- `~/.codex/skills/.system/skill-creator/SKILL.md`

До проектирования или изменения поведения полностью прочитать
`docs/skill-design-manifesto.md`. Манифест является каноническим стандартом
responsibility, самостоятельности, decision policy, handoff, stop conditions и
защиты от бесконечных workflow/review loops. Если предлагаемое решение ему
противоречит, сначала явно согласовать изменение самого манифеста либо
обоснованное exact исключение.

Перед реализацией нового skill сначала согласовать с пользователем:

1. responsibility и owning boundary;
2. triggers и exclusions;
3. handoffs к соседним skills;
4. необходимые references, scripts и assets;
5. спорные решения, риски и уточняющие вопросы.

Без отдельного запроса не смешивать создание нескольких skills в одной
итерации. Обновляя существующий skill:

- сохранять одно чёткое назначение и минимально достаточный контекст;
- держать trigger information в frontmatter `description`;
- оставлять во frontmatter только `name` и `description`;
- синхронизировать `agents/openai.yaml` с фактическим поведением;
- добавлять только необходимые `references`, `scripts` и `assets`;
- не создавать внутри skill `README.md`, `CHANGELOG.md` и другие
  вспомогательные документы;
- не добавлять FastyShop-specific правила, абсолютные пользовательские пути,
  secrets, credentials или неявные зависимости от локальной машины.

Если изменение затрагивает ownership, authority, alias, configuration contract
или handoff, проверить все связанные skills и README-каталог на конфликты.

## Проверка

Перед handoff запустить:

```bash
python3 scripts/validate_repository.py
```

Для каждого изменённого skill дополнительно запустить системный validator:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill-name>
```

Добавленные или изменённые scripts нужно выполнять на representative fixtures.
Нельзя объявлять skill провалидированным, если обязательная проверка не
запустилась; dependency limitation нужно назвать явно.

## Синхронизация и установка

Стабильная установка использует один exact release tag для всех выбранных
skills. Для unreleased testing допустим полный commit SHA; floating branch не
является воспроизводимой revision.

Перед заменой active или project-local copy:

1. сравнить source и destination рекурсивно;
2. остановиться при локальных изменениях или конфликте;
3. показать exact mutation scope;
4. синхронизировать только после явного разрешения;
5. повторно проверить destination.

Не редактировать `~/.codex/skills` или project-local copies как способ изменить
канонический reusable behavior.

## Версионирование и релизы

Канонический release runbook:

- `docs/releasing.md`

Использовать единый SemVer всего workflow kit и Conventional Commits. В обычном
feature/fix PR не редактировать вручную:

- `version.txt`;
- `.release-please-manifest.json`;
- release sections в `CHANGELOG.md`.

Release создаётся только через Release Please после ручного merge Release PR.
Не создавать поверх этого процесса ручные tags или GitHub Releases. Внешние
GitHub Actions закреплять полным commit SHA.

Описание Release Please PR является machine-managed частью release protocol:
не редактировать его вручную, в том числе ради перевода, подробного описания или
migration notes. До merge авторские дополнения к релизу вносить только коммитом
в `CHANGELOG.md` release-ветки; обсуждение вести в PR comments. После публикации
расширенное русское описание при необходимости добавлять в notes самого GitHub
Release, не возвращаясь к body Release Please PR.

Коммит, push, изменение GitHub settings, создание token/secret и публикация
релиза требуют отдельной явной команды пользователя.

## Документация и источники истины

- `README.md` — human-facing обзор, каталог и основной flow.
- `CONTRIBUTING.md` — правила contribution и Conventional Commits.
- `docs/skill-design-manifesto.md` — канонические принципы и критерии качества
  при проектировании reusable skills.
- `docs/releasing.md` — канонический versioning/release runbook.
- `docs/workflow-aliases.md` — human-facing contracts быстрых команд,
  sequence guards и рекомендуемые последовательности.
- `release-please-config.json` — release automation policy.
- `scripts/validate_repository.py` — repository-level validation.

Обновлять существующий owning документ вместо создания параллельного
объяснения. README должен ссылаться на подробный runbook, а не дублировать его
полностью.
