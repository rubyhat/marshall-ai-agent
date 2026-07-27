# Model Surfaces, States, and Actions

Turn the business flow into the minimum coherent frontend behavior model.

## Inventory surfaces

For each required page, panel, modal, drawer, step, or embedded region, state:

- its single responsibility;
- how the user enters and leaves it;
- whether it owns a route or exists inside another surface;
- which actor or role can access it;
- which upstream and downstream surfaces it connects.

Reuse an established product pattern when it fits. Do not add a screen merely to make the diagram symmetrical.

## Define the state model

Consider only applicable states:

- initial and loading;
- empty;
- ready or populated;
- partial or stale;
- validation failure;
- permission denied or unavailable;
- recoverable error;
- terminal failure;
- pending asynchronous work;
- success or completed;
- disabled, expired, cancelled, or already processed.

Distinguish server truth from temporary client presentation. Explain which state survives refresh, navigation, another device, or a later session.

## Define actions and feedback

For each state, identify:

- visible primary and secondary actions;
- unavailable or forbidden actions;
- validation timing;
- progress and duplicate-submit protection;
- confirmation for destructive or irreversible actions;
- success feedback and next navigation;
- error message, retry, cancel, support, or recovery action;
- preservation or clearing of user input.

Do not use a toast as the only representation of durable state. Do not hide a lifecycle transition behind ambiguous generic copy.

## Cover form and draft behavior

When applicable, resolve:

- server versus client validation;
- field-level and form-level errors;
- unsaved-change warning;
- autosave or explicit save;
- draft ownership and expiration;
- upload progress and retry;
- refresh, back navigation, and session-expiry behavior.

## Present a compact matrix

Use a table when multiple surfaces or states repeat:

| Surface | State | Available actions | Feedback | Recovery or next step |
|---|---|---|---|---|

Keep the matrix behavioral. Leave exact component and file structure to the specification workflow.
