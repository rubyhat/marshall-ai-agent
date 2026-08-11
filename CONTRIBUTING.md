# Участие в разработке

Этот репозиторий хранит единый совместимый набор reusable skills для Codex.
Изменения должны сохранять границы ответственности skills, воспроизводимость
установки и понятную историю совместимости.

## Рабочий процесс

1. Прочитайте
   [`docs/skill-design-manifesto.md`](docs/skill-design-manifesto.md) и
   определите responsibility, entry contract, decision policy, completion и
   handoff изменяемого skill.
2. Создайте отдельную ветку.
3. Измените только owning skill и необходимые repository-level файлы.
4. Обновите `agents/openai.yaml`, если изменились trigger или назначение skill.
5. Запустите:

   ```bash
   python3 scripts/validate_repository.py
   ```

6. Для каждого изменённого skill дополнительно запустите системный validator:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill-name>
   ```

   Если Python сообщает об отсутствующем модуле `yaml`, используйте локальное
   изолированное окружение, не добавляя runtime dependency репозиторию:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install 'PyYAML>=6,<7'
   .venv/bin/python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill-name>
   ```

7. Проверьте representative positive, negative и recovery scenarios; для
   сложного поведения выполните независимый forward-test без передачи агенту
   ожидаемого ответа.
8. Откройте Pull Request и дождитесь обязательной проверки `Validate / Skills`.
9. Используйте squash merge с Conventional Commit title.

Не редактируйте `version.txt`, `.release-please-manifest.json` или release
sections в `CHANGELOG.md` вручную в обычном feature/fix PR. Эти файлы принадлежат
Release Please.

## Conventional Commits

Формат:

```text
<type>(<optional-scope>): <short description>
```

Основные типы:

- `feat` — обратно совместимая новая возможность;
- `fix` — обратно совместимое исправление;
- `docs` — только документация;
- `refactor` — изменение без нового пользовательского поведения;
- `test` — тесты и fixtures;
- `ci` — CI/release infrastructure;
- `chore` — обслуживание репозитория.

В качестве scope обычно используйте имя skill:

```text
feat(configure-project-workflow): support pinned kit revisions
fix(deliver-reviewed-change): stop after a clean review verdict
docs(readme): document release installation
```

Несовместимое изменение обозначайте `!` и подробно объясняйте в footer:

```text
feat(configure-project-workflow)!: require pinned workflow revisions

BREAKING CHANGE: projects using a floating branch must select an exact tag or commit.
```

## Публичный контракт

При выборе SemVer учитывайте как публичный контракт:

- имена, triggers и exclusions skills;
- quick commands и их authority boundaries;
- обязательные поля project configuration;
- handoff между owning workflows;
- создаваемые project artifacts и schema;
- installation/update contract;
- safety, approval и mutation boundaries.

Обычное улучшение формулировки не является breaking change, пока не меняет
поведение, authority или ожидаемый handoff.

Подробный release flow описан в [docs/releasing.md](docs/releasing.md).
