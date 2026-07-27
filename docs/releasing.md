# Версионирование и релизы

## Модель

Репозиторий выпускается как единый workflow kit. Один Git tag представляет
совместимый снимок всех skills, references, scripts и assets. Выбранные skills
можно устанавливать отдельно, но их source revision должна относиться к одному
релизу.

Канонические значения:

- `version.txt` — текущая SemVer-версия репозитория;
- `.release-please-manifest.json` — та же версия для Release Please;
- `release-please-config.json` → `initial-version: 0.1.0` — явная версия
  первой публикации вместо bootstrap default `1.0.0`;
- `CHANGELOG.md` — история пользовательски значимых изменений;
- `v<MAJOR>.<MINOR>.<PATCH>` — immutable release tag.

Внутренние поля `schema_version` версионируют формат конкретного artifact и не
заменяют SemVer репозитория.

## Правила SemVer

До стабилизации installation и update contract используются версии `0.x.y`:

- `PATCH` — исправление без изменения существующего контракта;
- `MINOR` — новая возможность или несовместимое изменение pre-1.0;
- `MAJOR` — несовместимое изменение после объявления `v1.0.0`.

Перед `v1.0.0` нужно forward-test первоначальную настройку и обновление как
минимум на single-repo и multi-repo проектах.

## Однократная настройка GitHub

1. Создайте fine-grained token для exact repository:
   - repository access — только `marshall-ai-agent`;
   - Contents — Read and write;
   - Pull requests — Read and write;
   - Issues — Read and write для release labels;
   - Metadata — Read.
2. Сохраните token как Actions secret `RELEASE_PLEASE_TOKEN`.
3. Разрешите GitHub Actions создавать Pull Requests, если repository settings
   блокируют это действие.
4. Для `main` включите branch protection или ruleset:
   - изменения только через Pull Request;
   - required check `Validate / Skills`;
   - запрет force-push и удаления branch.
5. Используйте squash merge и Conventional Commit PR titles.

Стандартный `GITHUB_TOKEN` намеренно не используется: Pull Request, созданный
с его помощью, обычно не запускает другие workflows. Отдельный ограниченный
token позволяет Release PR пройти ту же обязательную validation.

## Обычный release flow

1. Feature/fix PR проходит `Validate / Skills`.
2. Squash commit попадает в `main` с Conventional Commit message.
3. `Release Please` создаёт или обновляет один Release PR.
4. Проверьте в Release PR:
   - SemVer bump;
   - `version.txt`;
   - `.release-please-manifest.json`;
   - полноту и понятность `CHANGELOG.md`;
   - breaking и migration notes;
   - зелёный `Validate / Skills`.
5. Merge Release PR является явным разрешением выпустить версию.
6. Release Please создаёт tag `vX.Y.Z` и опубликованный GitHub Release.
7. Проверьте, что tag, GitHub Release, `version.txt` и manifest совпадают.

Не создавайте tag или GitHub Release вручную поверх незамерженного Release PR.
Релиз не запускает deployment и не изменяет активные копии в `~/.codex/skills`
или project-local sources.

## Первый релиз

До первого релиза `version.txt` и manifest содержат `0.0.0`. Первый merged
releasable commit должен иметь тип `feat`; Release Please предложит `v0.1.0`.

Перед merge первого Release PR:

1. убедитесь, что все 12 skills перечислены в README;
2. запустите repository validator;
3. запустите системный `quick_validate.py` для каждого skill;
4. проверьте setup и update contract `configure-project-workflow`;
5. проверьте, что release notes явно называют набор экспериментальным pre-1.0.

## Compatibility и migrations

Release notes должны содержать отдельное объяснение, если изменились:

- required configuration fields;
- `schema_version`;
- quick commands;
- skill name или trigger;
- generated file layout;
- authority, safety или approval boundary;
- правила установки и синхронизации.

Для breaking change укажите:

1. кого оно затрагивает;
2. как обнаружить старое состояние;
3. точную последовательность обновления;
4. безопасен ли rollback;
5. какая минимальная совместимая версия требуется.

Стабильная project configuration должна сохранять exact tag, например
`v0.3.1`. Для unreleased testing допустим полный commit SHA. Floating branch
вроде `main` не является воспроизводимой revision.

## Hotfix и rollback

Hotfix проходит обычный PR и создаёт patch release.

Rollback установки означает возврат всех выбранных skills к одному предыдущему
known-good tag. Перед заменой активных копий нужно сравнить их с source и
остановиться при локальных изменениях. Release rollback не удаляет опубликованный
GitHub Release и не переписывает существующий tag.

## Обслуживание Actions

Все внешние Actions закреплены полным commit SHA. При обновлении:

1. найдите новый официальный release tag;
2. проверьте, что SHA принадлежит официальному repository;
3. обновите SHA и комментарий версии в отдельном PR;
4. перечитайте release notes Action;
5. пройдите repository validation до merge.
