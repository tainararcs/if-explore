# Project Guidelines

## 1. Purpose and current state

This document defines a simple organization for the Vue 3 + TypeScript frontend.
It uses a familiar separation between features, models, services, components, and
views without turning every feature into a layered architecture.

The current configuration uses Vue 3 with the Composition API, TypeScript, Vite,
and Vue Router. Styling uses Tailwind CSS v4 on top of the project tokens (see
§7). `vue-i18n` is configured in `src/lib/i18n.ts` (Composition API, pt-BR
only). Pinia and test tools are not currently configured in `package.json`.
Documentation must reflect the
actual configuration; do not create files or folders merely to complete the
example below.

`AGENTS.md` contains the agent's operational instructions. This document is the
source for technical organization and responsibility conventions.

## 2. Language conventions

- Write both instruction documents in English.
- Use English for all code identifiers, variable names, function names, class
  names, and file names.
- Write TSDoc and explanatory code comments in Brazilian Portuguese (`pt-BR`).
- Do not add comments for trivial callbacks or self-explanatory code.

## 3. Naming conventions

Apply these conventions consistently. Do not mix naming styles within the same
category.

### Files

- Class files use `PascalCase` matching the exported class name, such as
  `BaseService.ts`, `UserService.ts`, and `HttpClient.ts`.
- Single-File Component files use `PascalCase`, such as `UsersView.vue` and
  `UserTable.vue`.
- Composable files use `camelCase` with the `use` prefix, such as `useUsers.ts`.
- Utility modules and files without classes use `kebab-case`, such as
  `format-date.ts`.

### Identifiers

- Classes, types, and interfaces use `PascalCase`.
- Variables and functions use `camelCase`.
- Component names use multi-word `PascalCase`, such as `UserTable` instead of
  `Table`, to avoid conflicts with HTML elements. The root `App.vue` is the only
  exception.
- Use `PascalCase` for components in templates, such as `<UserTable />`.
- Props are declared in `camelCase`; emitted events are declared in `camelCase`.

## 4. Directory structure

Use feature-oriented organization for code specific to a domain:

```text
src/
├── features/
│   ├── users/
│   │   ├── models/
│   │   ├── services/
│   │   ├── components/
│   │   ├── composables/
│   │   └── views/
│   └── auth/
│       ├── models/
│       ├── services/
│       ├── components/
│       └── views/
├── components/       # Shared components
├── services/         # Shared services and infrastructure
├── models/           # Shared types and contracts
├── composables/      # Shared composables
├── lib/              # Shared utilities and configuration
├── router/           # Application routes
├── App.vue
└── main.ts
```

This is a reference. Create only the directories needed for a feature. A feature
can start with a few files and add `models/`, `services/`, `components/`,
`composables/`, or `views/` when there is a real need. Do not create a complete
set of empty directories.

### Directory responsibilities

| Directory | Responsibility |
|---|---|
| `features/<feature>/` | Code belonging to a domain or feature, such as `users`, `auth`, or `orders` |
| `features/<feature>/models/` | Types, interfaces, and contracts specific to the feature |
| `features/<feature>/services/` | Endpoints and operations specific to the feature |
| `features/<feature>/components/` | Components specific to the feature |
| `features/<feature>/composables/` | Composables specific to the feature |
| `features/<feature>/views/` | Screens and interface composition for the feature |
| `components/` | Components reusable across features |
| `services/` | Services and access infrastructure shared across features |
| `models/` | Types and contracts genuinely shared across the application |
| `composables/` | Composables shared across features |
| `lib/` | Shared technical utilities and configuration |
| `router/` | Vue Router instance and route definitions |

Feature-specific code should remain inside its owning feature. Move something to
a global directory only when it has real reuse or a clearly cross-cutting
responsibility. Do not keep equivalent copies in both locations.

`App.vue` and `main.ts` remain at the root of `src/`.

### Routing

Routes are defined in `src/router/index.ts` with Vue Router.

- Route components are feature views, such as
  `features/home/views/HomeView.vue`.
- Load route views lazily with dynamic imports, such as
  `() => import('../features/home/views/HomeView.vue')`.
- Use route `redirect` for redirections and `/:pathMatch(.*)*` for the
  not-found route, keeping it as the last route.
- Split routes into per-feature modules only when the route list grows enough to
  justify it.

## 5. Models

Models define data types, interfaces, and contracts. Whenever possible, they
should be independent of Vue and should not contain rendering or interface
effects.

- Keep feature-specific models inside their owning feature.
- Use `src/models/` only for genuinely shared contracts.
- Prefer explicit types for exported contracts.
- Use `unknown` for external data that has not been validated.
- Validate external data at the appropriate boundary before treating it as a
  trusted model.
- Avoid duplicating types when an existing contract can be safely reused or
  derived.

Do not create DTOs, mappers, or transformation layers by default. Introduce them
only when there is a concrete format difference, validation need, or maintenance
benefit.

## 6. Services and data access

Services centralize access to APIs and endpoints. A feature service may
encapsulate related operations such as `getAll`, `getById`, `create`, `update`,
and `delete` only when those endpoints actually exist.

- Keep request and response contracts explicit.
- Place feature-specific services in `features/<feature>/services/`.
- Place shared HTTP configuration or access in `src/services/` when multiple
  features genuinely use the same infrastructure.
- Do not mix API calls directly into presentation components.
- Views may coordinate the screen and its local state, but should not
  unnecessarily accumulate API access, business rules, and transformations.
- Handle loading, success, empty, and error states explicitly when the operation
  requires them.
- Normalize errors only when shared behavior justifies it.
- Consider cancellation, caching, or retries when a feature needs them; do not
  impose them mechanically on every request.

Services may be classes when a class helps encapsulate related operations.
Functions or simple modules are preferable when they are sufficient. Services
must not depend on Vue reactivity; expose reactive state through composables
when a component needs it. Do not create repositories, use cases, or other
layers by obligation.

## 7. Components and views

Write components and views as Single-File Components using the Composition API
with `<script setup lang="ts">`. Do not use the Options API.

### Components

Components represent observable interface and interaction.

- Feature-specific components belong in `features/<feature>/components/`.
- Shared components belong in `src/components/`.
- A shared component must not depend on feature-specific rules.
- Keep components cohesive, with explicit props and clear responsibilities.
- Declare props with type-based `defineProps<Props>()` and events with
  type-based `defineEmits<Emits>()`.
- Never mutate props. Use `defineModel()` for two-way binding with `v-model`.
- Prefer composition through slots over components with many conditional props.
- Always provide a stable `:key` with `v-for`, and do not combine `v-if` and
  `v-for` on the same element.
- Extract a component when this improves reuse, consistency, readability, or
  testability.
- Do not use file size as the sole reason to extract a component.
- Do not create wrappers, factories, or components for trivial markup without a
  concrete benefit.
- Evaluate consumers when changing a shared component.

Styling uses Tailwind CSS v4 (`tailwindcss` and `@tailwindcss/vite`), imported
in `src/index.css` with only its theme and utilities; the preflight reset is not
used, and the project base styles stay in `src/index.css`.

- Design tokens live in the `@theme static` block of `src/index.css`. Tailwind
  defaults for colors, fonts, text sizes, radii, shadows, easing, and
  breakpoints are removed, so only project values exist (`bg-surface`,
  `text-text-muted`, `font-display`, `text-small`, `rounded-pill`, `md:`).
- Prefer utilities for layout, spacing, color, and typography in templates. Do
  not use arbitrary values such as `p-[13px]` when a token exists.
- Keep `<style scoped>` for what utilities express poorly: pseudo-elements,
  keyframes, scroll snapping, scroll-driven effects, and complex selectors or
  states. Omit the `<style>` block when the component has no styles.
- Do not style the same property of an element with both a utility and scoped
  CSS: unlayered scoped styles always win over Tailwind's layered utilities.
- Dark mode comes from the semantic tokens (`light-dark()`); `dark:` variants
  are not needed.
- `hover:` variants only apply on devices that support hover
  (`@media (hover: hover)`), so touch screens do not keep a hover state after a
  tap. Never rely on hover alone to reveal content or actions.
- Migration is gradual: existing components keep their scoped CSS until they
  are changed for another reason.

### Views

Views are the screens and interface composition for a feature. They may
coordinate components, receive data, and keep screen-local state, but should
delegate responsibilities when logic is no longer simple or specific to
composition.

Avoid unnecessarily concentrating all of the following in one view:

- endpoint access;
- business rules;
- data transformations;
- shared state management;
- rendering of the entire interface.

There is no need to create a view for every component or small markup variation.

## 8. Composables and state

- Feature-specific composables belong inside their owning feature.
- Composables reused by multiple features belong in `src/composables/`.
- Create a composable when it encapsulates reactive state, watchers, lifecycle
  hooks, `provide`/`inject`, subscriptions, external synchronization, or other
  cohesive Vue behavior.
- Use ordinary TypeScript functions for calculations, validation, business rules,
  and transformations that do not need Vue reactivity.
- Do not create composables merely to wrap a pure function or hide simple code.
- Prefer `ref` for reactive state; use `reactive` only when grouping related
  state in one object adds clarity.
- Keep state close to the components that use it.
- Share state through props and events with the nearest common ancestor that
  needs it.
- Use `provide`/`inject` or a state library only when state is genuinely shared
  and props are insufficient. Pinia is not configured; do not add it without a
  concrete requirement.
- Calculate derived values with `computed`; do not duplicate them and
  synchronize them with watchers without an external need.
- Use `watch` and `watchEffect` to synchronize with external systems, not for
  ordinary calculations.
- Clean up subscriptions, timers, and other external resources at the appropriate
  lifecycle boundary, such as `onUnmounted` or `onWatcherCleanup`.

## 9. Modules and dependencies

- Keep each module focused on a clear responsibility.
- Avoid circular dependencies and unnecessary coupling between features.
- A feature should not import another feature's internal details without a
  genuinely necessary interface or contract.
- Shared infrastructure should not depend on feature-specific domain rules.
- Export only what other modules need.
- Prefer explicit imports over broad barrels that hide dependencies.
- Do not introduce interfaces, dependency injection, inheritance, or patterns
  solely to satisfy SOLID.
- Do not introduce additional layers without a concrete benefit to clarity,
  testability, or maintenance.

## 10. TypeScript, accessibility, and internationalization

### TypeScript

- Do not use `any`, `@ts-ignore`, or unsafe assertions to bypass errors.
- Preserve strict settings and existing checks.
- Define explicit contracts for exported APIs, component props, and emitted
  events.
- Use inference for straightforward local variables.
- Use discriminated unions for mutually exclusive states when this improves
  safety.
- Type-check `.vue` files with `vue-tsc` through the project scripts.

### Accessibility

- Use semantic HTML and accessible names for controls.
- Preserve keyboard navigation and visible focus.
- Use ARIA only when native semantics are insufficient.
- Do not rely only on color to communicate state.

### Internationalization

Use the i18n solution configured in the repository: `vue-i18n` in Composition API
mode, configured in `src/lib/i18n.ts`, with messages in `src/locales/pt-BR.ts`.
Use `useI18n()` in components and `i18n.global` outside them.

When i18n is configured:

- keep interface text in translation resources;
- organize resources by language and use descriptive keys;
- use interpolation for dynamic values;
- use `Intl` APIs for dates, numbers, and currencies when appropriate.

Do not add languages, libraries, or a complete translation structure without a
concrete requirement.

## 11. Performance and dependencies

- Vue tracks reactive dependencies automatically; do not add manual
  optimizations such as `v-memo`, `v-once`, `shallowRef`, or `markRaw`
  indiscriminately.
- Consider those optimizations, `defineAsyncComponent`, lazy loading, and code
  splitting when there is a clear benefit, a measurable requirement, or an
  observed bottleneck.
- Measure or reproduce the problem before adding non-trivial optimizations.
- Evaluate bundle impact, maintenance, and complexity before adding a dependency
  or abstraction.
- Do not optimize prematurely at the expense of readability.

## 12. Documentation and testing

### Code documentation

Use TSDoc in Brazilian Portuguese (`pt-BR`) for exported functions, composables,
public contracts, domain types, and non-obvious logic. Include `@param`,
`@returns`, and `@throws` when relevant.

Document each component with a short comment in Brazilian Portuguese at the top
of the `.vue` file. Use TSDoc on props and emitted events when their meaning is
not obvious.

Explanatory code comments must also be written in Brazilian Portuguese. Do not
add comments for trivial inline callbacks, mechanical wrappers, or code whose
behavior is already clear. Documentation should be concise, accurate, and
proportional to complexity.

### Testing

Use the testing tools configured in the repository. There is currently no
`test` script and no Vitest, Vue Test Utils, Playwright, or Cypress declared in
`package.json`.

When testing tools are configured:

- test pure functions and business rules without mounting components;
- test components through observable behavior and interactions;
- test composables through their behavior and relevant effects;
- test services and integrations at data-access boundaries;
- prefer deterministic tests and avoid implementation-detail assertions;
- add regression coverage for bug fixes when appropriate.

## 13. Checks and dependencies

Use the scripts in `package.json`. The currently available scripts are:

- `npm run dev`
- `npm run build`
- `npm run lint`
- `npm run typecheck`
- `npm run preview`

Before completing a change, run applicable checks and report their results. Do
not install dependencies or change configuration merely to run a check the
project does not currently provide.

New dependencies require a technical justification and consideration of
compatibility, maintenance, security, and bundle size. Avoid unrelated upgrades.
