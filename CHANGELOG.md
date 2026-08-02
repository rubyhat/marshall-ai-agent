# Changelog

## [0.4.0](https://github.com/rubyhat/marshall-ai-agent/compare/v0.3.0...v0.4.0) (2026-08-02)


### Новые возможности

* **workflow:** add ADR lifecycle core ([#14](https://github.com/rubyhat/marshall-ai-agent/issues/14)) ([7f298e3](https://github.com/rubyhat/marshall-ai-agent/commit/7f298e3bd6208ccfd44b7be77e1d5bfc5ccf58fd))

### Совместимость и обновление

* Добавлен skill `record-architecture-decision` и read-only/mutation aliases
  `--adr-review` и `--record-adr`. Он управляет necessity, applicability и
  lifecycle одного материального архитектурного решения, а сохраняет готовый
  ADR через bounded handoff в `record-project-context`.
* Для проектов, которые не включают новый ADR-модуль, обязательной миграции
  нет; существующие установки по pinned revision не изменяются автоматически.
* При обновлении до `v0.4.0` с включением ADR-модуля повторно запустите
  `--workflow-setup`: конфигурация должна получить секцию
  `architecture_decisions` с project-relative root/index, lifecycle labels,
  decision authority, preview/confirmation policy и точным exclusive-lock или
  compare-and-swap protocol для общей ADR/index mutation. После настройки
  выполните `--workflow-check`.
* Стабильная установка должна использовать exact tag `v0.4.0`; floating
  `main` не является воспроизводимой revision.

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
