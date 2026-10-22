# Project Guidelines

## 1. Purpose and current state

This document defines a simple organization for the React + TypeScript frontend.
It uses a familiar separation between features, models, services, components, and
views without turning every feature into a layered architecture.

The current configuration uses React 19, TypeScript, and Vite. Existing styling
is CSS. `i18next` and `react-i18next` are dependencies, but the i18n
configuration must be verified before use. React Router, Tailwind CSS, and test
tools are not currently configured in `package.json`. Documentation must reflect
the actual configuration; do not create files or folders merely to complete the
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
- React component files use `PascalCase` matching the component name, such as
  `UsersView.tsx` and `UserTable.tsx`.
- Hook files use `camelCase` with the `use` prefix, such as `useUsers.ts`.
- Utility modules and files without classes use `kebab-case`, such as
  `format-date.ts`.

### Identifiers

- Classes, types, and interfaces use `PascalCase`.
- Variables and functions use `camelCase`.

## 4. Directory structure

Use feature-oriented organization for code specific to a domain:

```text
src/
├── features/
│   ├── users/
│   │   ├── models/
│   │   ├── services/
│   │   ├── components/
│   │   └── views/
│   └── auth/
│       ├── models/
│       ├── services/
│       ├── components/
│       └── views/
├── components/       # Shared components
├── services/         # Shared services and infrastructure
├── models/           # Shared types and contracts
├── hooks/            # Shared hooks
├── lib/              # Shared utilities and configuration
├── App.tsx
└── main.tsx
```

This is a reference. Create only the directories needed for a feature. A feature
can start with a few files and add `models/`, `services/`, `components/`, or
`views/` when there is a real need. Do not create a complete set of empty
directories.

### Directory responsibilities

| Directory | Responsibility |
|---|---|
| `features/<feature>/` | Code belonging to a domain or feature, such as `users`, `auth`, or `orders` |
| `features/<feature>/models/` | Types, interfaces, and contracts specific to the feature |
| `features/<feature>/services/` | Endpoints and operations specific to the feature |
| `features/<feature>/components/` | Components specific to the feature |
| `features/<feature>/views/` | Screens and interface composition for the feature |
| `components/` | Components reusable across features |
| `services/` | Services and access infrastructure shared across features |
| `models/` | Types and contracts genuinely shared across the application |
| `hooks/` | Hooks shared across features |
| `lib/` | Shared technical utilities and configuration |

Feature-specific code should remain inside its owning feature. Move something to
a global directory only when it has real reuse or a clearly cross-cutting
responsibility. Do not keep equivalent copies in both locations.

`App.tsx` and `main.tsx` remain at the root of `src/`, as in the current project.
If routing is introduced, its location must follow the configuration adopted by
the project; do not assume React Router without a corresponding dependency and
configuration.

## 5. Models

Models define data types, interfaces, and contracts. Whenever possible, they
should be independent of React and should not contain rendering or interface
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
Functions or simple modules are preferable when they are sufficient. Do not
create repositories, use cases, or other layers by obligation.

## 7. Components and views

### Components

Components represent observable interface and interaction.

- Feature-specific components belong in `features/<feature>/components/`.
- Shared components belong in `src/components/`.
- A shared component must not depend on feature-specific rules.
- Keep components cohesive, with explicit props and clear responsibilities.
- Prefer composition over components with many conditional options.
- Extract a component when this improves reuse, consistency, readability, or
  testability.
- Do not use file size as the sole reason to extract a component.
- Do not create wrappers, factories, or components for trivial markup without a
  concrete benefit.
- Evaluate consumers when changing a shared component.

Use the styling solution configured in the repository. Do not assume Tailwind or
another library without checking dependencies and configuration.

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

## 8. Hooks and state

- Feature-specific hooks belong inside their owning feature.
- Hooks reused by multiple features belong in `src/hooks/`.
- Create a custom hook when it encapsulates state, effects, context,
  subscriptions, external synchronization, or other cohesive React behavior.
- Use ordinary TypeScript functions for calculations, validation, business rules,
  and transformations that do not need React.
- Do not create hooks merely to wrap a pure function or hide simple code.
- Keep state close to the components that use it.
- Lift state only to the nearest common ancestor that needs to share it.
- Use context or a state library only when state is genuinely shared and local
  state is insufficient.
- Calculate derived values from props and state; do not duplicate them and
  synchronize them with effects without an external need.
- Use effects to synchronize with external systems, not for ordinary calculations.
- Clean up subscriptions, timers, and other external resources at the appropriate
  lifecycle boundary.

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
- Define explicit contracts for exported APIs and component props.
- Use inference for straightforward local variables.
- Use discriminated unions for mutually exclusive states when this improves
  safety.

### Accessibility

- Use semantic HTML and accessible names for controls.
- Preserve keyboard navigation and visible focus.
- Use ARIA only when native semantics are insufficient.
- Do not rely only on color to communicate state.

### Internationalization

Use the i18n solution configured in the repository. The `i18next` and
`react-i18next` dependencies are currently available, but do not assume an
active configuration: verify the existing files before using translation hooks
or resources.

When i18n is configured:

- keep interface text in translation resources;
- organize resources by language and use descriptive keys;
- use interpolation for dynamic values;
- use `Intl` APIs for dates, numbers, and currencies when appropriate.

Do not add languages, libraries, or a complete translation structure without a
concrete requirement.

## 11. Performance and dependencies

- Do not use `useMemo`, `useCallback`, or `React.memo` indiscriminately.
- Consider memoization, lazy loading, and code splitting when there is a clear
  benefit, a measurable requirement, or an observed bottleneck.
- Measure or reproduce the problem before adding non-trivial optimizations.
- The React Compiler is not currently configured; do not assume its benefits or
  add configuration without an explicit project decision.
- Evaluate bundle impact, maintenance, and complexity before adding a dependency
  or abstraction.
- Do not optimize prematurely at the expense of readability.

## 12. Documentation and testing

### Code documentation

Use TSDoc in Brazilian Portuguese (`pt-BR`) for exported components, exported
hooks, exported functions, public contracts, domain types, and non-obvious
logic. Include `@param`, `@returns`, and `@throws` when relevant.

Explanatory code comments must also be written in Brazilian Portuguese. Do not
add comments for trivial inline callbacks, mechanical wrappers, or code whose
behavior is already clear. Documentation should be concise, accurate, and
proportional to complexity.

### Testing

Use the testing tools configured in the repository. There is currently no
`test` script and no Vitest, Jest, React Testing Library, Playwright, or Cypress
declared in `package.json`.

When testing tools are configured:

- test pure functions and business rules without rendering React;
- test components through observable behavior and interactions;
- test hooks through their behavior and relevant effects;
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
