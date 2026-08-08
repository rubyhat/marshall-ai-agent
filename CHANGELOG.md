# Changelog

## [0.6.8](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.7...v0.6.8) (2026-08-08)


### Исправления

* **workflow:** require current reviewed publication schema ([#47](https://github.com/rubyhat/marshall-ai-agent/issues/47)) ([a290c65](https://github.com/rubyhat/marshall-ai-agent/commit/a290c65a1bdbb4a0abf81e1bb6328ea8332e7cbf))

## [0.6.7](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.6...v0.6.7) (2026-08-07)


### Исправления

* **workflow:** bind review evidence to published specs ([#45](https://github.com/rubyhat/marshall-ai-agent/issues/45)) ([69df005](https://github.com/rubyhat/marshall-ai-agent/commit/69df005228a84e61702608ea44d3dd667f327a6d))

## [0.6.6](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.5...v0.6.6) (2026-08-07)


### Исправления

* **workflow:** prioritize reviewed publication evidence ([#43](https://github.com/rubyhat/marshall-ai-agent/issues/43)) ([382e687](https://github.com/rubyhat/marshall-ai-agent/commit/382e687a73c2a86a190a5475fdf11566bd9e57db))

## [0.6.5](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.4...v0.6.5) (2026-08-07)


### Исправления

* **workflow:** make legacy readiness an alternative gate ([#41](https://github.com/rubyhat/marshall-ai-agent/issues/41)) ([742a769](https://github.com/rubyhat/marshall-ai-agent/commit/742a7699ed89969a172324443825544dccbfba41))

## [0.6.4](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.3...v0.6.4) (2026-08-07)


### Исправления

* **workflow:** preserve legacy spec readiness ([#39](https://github.com/rubyhat/marshall-ai-agent/issues/39)) ([550e07c](https://github.com/rubyhat/marshall-ai-agent/commit/550e07c45453cb1c19245062090094f27d80f79b))

## [0.6.3](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.2...v0.6.3) (2026-08-07)


### Исправления

* **workflow:** enforce planning publication schema guards ([b84ab0a](https://github.com/rubyhat/marshall-ai-agent/commit/b84ab0a0ceee0fb16a2bbb800e1eb234c3c2d226))

## [0.6.2](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.1...v0.6.2) (2026-08-07)


### Исправления

* **workflow:** bind spec review to planning worktree ([50d4147](https://github.com/rubyhat/marshall-ai-agent/commit/50d414711a425eb512b1c87f87d623973f876165))

## [0.6.1](https://github.com/rubyhat/marshall-ai-agent/compare/v0.6.0...v0.6.1) (2026-08-07)


### Исправления

* **workflow:** support vendored roadmap contract test ([#33](https://github.com/rubyhat/marshall-ai-agent/issues/33)) ([6592754](https://github.com/rubyhat/marshall-ai-agent/commit/6592754e74115fdedb9af8182f909779eaa277df))

## [0.6.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.5.1...v0.6.0) (2026-08-07)


### Новые возможности

* **workflow:** make roadmap task identity issue-first ([#32](https://github.com/rubyhat/marshall-ai-agent/issues/32)) ([79047f9](https://github.com/rubyhat/marshall-ai-agent/commit/79047f999414d403825b8c0b8e9cd6ee8c3767a7))

### Миграция

* Изменение затрагивает проекты с `--shape-roadmap` и GitHub task tracking,
  которые заранее подбирают свободный custom Task ID либо сохраняют отдельный
  local roadmap/coordination artifact.
* После установки всех выбранных skills из `v0.6.0` запустите
  `--workflow-setup` в режиме reconfigure. Для новых задач настройте
  provider-number-derived identity, формат с `<ISSUE_NUMBER>`, нейтральный
  correlation marker и namespace, уникальный между Issue repositories;
  preallocation custom-номера для новых GitHub Issues отключите.
* `--shape-roadmap` теперь принимает уже сформированный outcome, утверждает один
  semantic tracker manifest и не создаёт локальные roadmap, memory или
  coordination files. Существующие Task IDs остаются legacy anchors и не
  переименовываются.
* Rollback skills на предыдущий tag безопасен до создания задач с новым
  форматом. После появления Issue-number-derived IDs сохраняйте совместимый
  validation/search contract либо оставайтесь на `v0.6.0`; не переписывайте
  созданную историю ради rollback.


### Документация

* **release:** protect Release Please PR body ([#30](https://github.com/rubyhat/marshall-ai-agent/issues/30)) ([2c90288](https://github.com/rubyhat/marshall-ai-agent/commit/2c90288d41e1be4a033cbc7dc463f4b77df3e509))

## [0.5.1](https://github.com/rubyhat/marshall-ai-agent/compare/v0.5.0...v0.5.1) (2026-08-07)


### Исправления

* **workflow:** support cross-repository spec provenance ([#28](https://github.com/rubyhat/marshall-ai-agent/issues/28)) ([2a50159](https://github.com/rubyhat/marshall-ai-agent/commit/2a501599b1c75693293525aaf675ce37f4b59a85))

## [0.5.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.4.3...v0.5.0) (2026-08-07)


### Новые возможности

* **workflow:** publish reviewed task specifications ([a7a3512](https://github.com/rubyhat/marshall-ai-agent/commit/a7a351276b22cf6ddf81c7c9ab8fbba3bd443f1e))

### Миграция

* Проекты с Git-tracked task specifications должны установить все выбранные
  skills из `v0.5.0`, включить `publish-planning-change`, настроить секцию
  `planning_publication` и зарегистрировать `--publish-spec`.
* Planning profile может разрешать только capability
  `planning_artifact_publication`; implementation, ordinary delivery, release,
  deploy и production mutations остаются заблокированными до отдельной
  authority и, для implementation, новой сессии.
* Общий `schema_version` остаётся `2`. До reconfiguration старый проект не
  должен считать локальную или unmerged specification достаточным
  implementation gate.

## [0.4.3](https://github.com/rubyhat/marshall-ai-agent/compare/v0.4.2...v0.4.3) (2026-08-07)


### Исправления

* **workflow:** roll back documentation-only fast path ([525ec77](https://github.com/rubyhat/marshall-ai-agent/commit/525ec77e9d921926498d362af26c2d1735f1aae6))

## [0.4.2](https://github.com/rubyhat/marshall-ai-agent/compare/v0.4.1...v0.4.2) (2026-08-07)


### Исправления

* **workflow:** require fast-path exclusions ([#21](https://github.com/rubyhat/marshall-ai-agent/issues/21)) ([404f1af](https://github.com/rubyhat/marshall-ai-agent/commit/404f1af6c4f416e53588d088e0b9e7678cd4e3bd))

## [0.4.1](https://github.com/rubyhat/marshall-ai-agent/compare/v0.4.0...v0.4.1) (2026-08-07)


### Исправления

* **workflow:** enforce documentation fast-path guards ([#19](https://github.com/rubyhat/marshall-ai-agent/issues/19)) ([bf643a5](https://github.com/rubyhat/marshall-ai-agent/commit/bf643a5da6f4aabcb2fc4c7237ee6cd8710d5aad))

## [0.4.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.3.0...v0.4.0) (2026-08-07)


### Новые возможности

* **workflow:** add documentation-only delivery fast path ([8429db0](https://github.com/rubyhat/marshall-ai-agent/commit/8429db0a00f63e854646eb5cc350fbdd26377e74))

## [0.3.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.2.1...v0.3.0) (2026-08-01)


### Новые возможности

* **workflow:** add topology onboarding and spec continuation ([843f06c](https://github.com/rubyhat/marshall-ai-agent/commit/843f06ce79bab0ca89d6f485feac8eccf6cec471))

## [0.2.1](https://github.com/rubyhat/marshall-ai-agent/compare/v0.2.0...v0.2.1) (2026-07-28)


### Исправления

* **workflow:** enforce planning session boundaries ([91125cd](https://github.com/rubyhat/marshall-ai-agent/commit/91125cd050301cfaaa85608b2ee0d61cb9bc893e))

## [0.2.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.1.0...v0.2.0) (2026-07-28)


### ⚠ BREAKING CHANGES

* **workflow:** project workflow schema v2 requires commands.sequence_guard; setup tracker schema v2 requires modules.enabled_aliases; reconfigure schema v1 projects before enabling the new aliases.

### Новые возможности

* **workflow:** add guarded workflow aliases ([93e6d11](https://github.com/rubyhat/marshall-ai-agent/commit/93e6d1151acaa894ca5f93ba6b2b9a55f171b299))


### Документация

* **readme:** point setup to v0.1.0 ([#6](https://github.com/rubyhat/marshall-ai-agent/issues/6)) ([5faf381](https://github.com/rubyhat/marshall-ai-agent/commit/5faf3811896069e0f067023fe18ad4f2193eb8be))

## 0.1.0 (2026-07-27)


### Новые возможности

* bootstrap reusable Codex workflow kit ([4ce05a0](https://github.com/rubyhat/marshall-ai-agent/commit/4ce05a0ec1b1d1c458277fb2dfdab7d1d08ea258))


### Исправления

* **release:** keep bootstrap changelog heading-free ([#4](https://github.com/rubyhat/marshall-ai-agent/issues/4)) ([d09dceb](https://github.com/rubyhat/marshall-ai-agent/commit/d09dcebff21a1d13c9a9482979559bb2ecdb147c))
* **release:** set initial version to 0.1.0 ([#2](https://github.com/rubyhat/marshall-ai-agent/issues/2)) ([61b6b9f](https://github.com/rubyhat/marshall-ai-agent/commit/61b6b9fc668206aa59a6dc4039613afa038d12be))


### Документация

* **release:** normalize initial changelog header ([#3](https://github.com/rubyhat/marshall-ai-agent/issues/3)) ([7ac68b4](https://github.com/rubyhat/marshall-ai-agent/commit/7ac68b4e2f4b6fce3df143ea21aebe47a95aaa53))

<!-- Managed by Release Please. Bootstrap policy: docs/releasing.md. -->
