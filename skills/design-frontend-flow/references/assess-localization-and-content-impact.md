# Assess Localization and Content Impact

Treat copy as part of behavior whenever it explains status, constraints, consequences, or recovery.

## Inventory user-facing content

Identify applicable:

- headings and instructions;
- field labels, hints, and validation;
- primary and secondary actions;
- empty, loading, pending, success, and error messages;
- confirmations and destructive-action warnings;
- accessibility names and status announcements;
- legal, billing, verification, privacy, or support language;
- notifications or companion-channel messages.

## Apply configured localization policy

Resolve:

- supported locales and source language;
- whether all locales change in one task;
- message-key and placeholder parity requirements;
- content that is user-entered, technical, externally served, or otherwise exempt;
- semantic or native-language review requirements;
- layout and responsive checks for content expansion.

Do not assume a locale set or translation workflow. Use project configuration and current catalogs.

## Preserve product truth

Translations and rewritten copy must preserve:

- actor and role;
- action intent;
- validation constraint;
- lifecycle consequence;
- permission and tenant boundary;
- recovery action;
- actual channel, timing, and support promise.

Do not let a translation add an approval, payment, delivery, refund, service-level, or support promise absent from the source contract.

## Escalate sensitive content

Require the configured semantic or specialist review for legal, billing, verification, privacy, consent, and support copy. Separate design of the surrounding UI flow from authorship of a legal document or policy text.

## Return an impact summary

State:

- affected content categories and locales;
- semantic constraints;
- layout or accessibility risks;
- required checks or reviews;
- `none` with a reason only when no user-facing content changes.
