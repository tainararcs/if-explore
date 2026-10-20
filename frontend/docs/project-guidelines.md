# Project Guidelines

## 1. Overview

The project uses Node.js 24.22.0, React, TypeScript, Vite, and Tailwind CSS.

The architecture must remain modular, simple, and maintainable. Prioritize strict typing, component reuse, clear responsibilities, documentation, and testability without introducing unnecessary abstractions.

`AGENTS.md` defines mandatory agent behavior. This document defines the technical conventions used to implement the application.

## 2. Project Structure

Use a feature-oriented modular architecture.

```text
src/
├── app/
│   ├── providers/
│   ├── router/
│   ├── App.tsx
│   └── i18n.ts
├── assets/
├── components/
│   ├── ui/
│   └── layout/
├── features/
│   └── example/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── types/
│       ├── utils/
│       └── index.ts
├── hooks/
├── lib/
├── locales/
│   └── pt-BR/
│       └── translation.json
├── styles/
├── test/
├── types/
└── main.tsx
```

Create directories only when needed. Do not create empty structures or files in anticipation of hypothetical requirements.

### Directory Responsibilities

| Directory | Responsibility |
|---|---|
| `app/` | Application composition, routing, providers, and initialization |
| `assets/` | Static resources |
| `components/ui/` | Generic, reusable UI components |
| `components/layout/` | Shared structural components |
| `features/` | Business functionality organized by feature |
| `hooks/` | Hooks shared across features |
| `lib/` | Shared technical utilities and library configuration |
| `locales/` | Translation resources |
| `styles/` | Global styles and design foundations |
| `test/` | Shared testing utilities |
| `types/` | Types genuinely shared across the application |

Feature-specific components, hooks, types, services, and utilities should remain inside their owning feature.

Feature subdirectories are optional. Introduce them only when they improve organization.

## 3. Modularity and Dependencies

- Keep modules cohesive and focused on a clear responsibility.
- Expose only the functionality that other modules need.
- Avoid circular dependencies and unnecessary cross-feature coupling.
- Keep shared infrastructure independent of business features.
- Avoid broad barrel exports that obscure dependency boundaries.
- Prefer explicit contracts and straightforward dependencies.
- Do not introduce additional architectural layers without a concrete benefit.

Apply SOLID principles pragmatically:

- **SRP:** Give each function, component, and module a clear responsibility.
- **OCP:** Prefer composition and controlled extension when variation is needed.
- **LSP:** Preserve behavioral contracts when using substitutable implementations.
- **ISP:** Keep interfaces and component props focused.
- **DIP:** Reduce coupling to external dependencies when abstraction provides a real benefit.

Do not introduce interfaces, dependency injection, inheritance, or design patterns solely to satisfy SOLID.

## 4. React Componentization

Componentization must improve reuse, consistency, readability, or testability.

### Component Categories

**Shared UI — `src/components/ui/`**

Generic components such as buttons, inputs, cards, dialogs, and badges. They must not depend on business-specific logic.

**Shared layout — `src/components/layout/`**

Structural components such as headers, sidebars, and page containers.

**Feature components — `src/features/<feature>/components/`**

Components that implement domain-specific presentation and behavior.

### Componentization Rules

- Reuse existing components when their contracts fit the requirement.
- Extract repeated UI patterns when doing so improves maintainability or consistency.
- Prefer composition and explicit props over duplicated markup.
- Keep components cohesive and avoid excessive configuration options.
- Do not create components for trivial, isolated markup without a clear benefit.
- Evaluate all consumers when changing a shared component.
- Use TypeScript interfaces or types to define component props.
- Follow the project's Tailwind CSS conventions.

Reuse should not compromise clarity or create artificial abstractions.

## 5. TypeScript and React

Maintain strict TypeScript settings.

- Never use `any`, `@ts-ignore`, or unsafe assertions to bypass type errors.
- Use `unknown` for values whose types are not established.
- Validate external data at appropriate runtime boundaries.
- Define explicit contracts for exported APIs, component props, and custom hooks.
- Use return type annotations where they improve clarity and contract safety.
- Prefer inference for straightforward local variables.
- Use discriminated unions for mutually exclusive states.
- Avoid duplicated types when they can be derived from an existing schema.
- Prefer function components and React hooks.
- Keep state close to its consumers and avoid redundant state.
- Use effects for synchronization with external systems, not ordinary calculations.
- Avoid premature memoization and unnecessary effects.

Do not weaken compiler settings to accommodate an implementation.

## 6. Documentation

All functions, methods, custom hooks, and React components must have TSDoc documentation written in Brazilian Portuguese (`pt-BR`).

Documentation must describe the unit's purpose and include applicable parameter, return, and exception documentation.

Use `@param`, `@returns`, and `@throws` when relevant.

Document named internal functions and callbacks as well. For anonymous callbacks, include concise documentation wherever it can be expressed clearly; prefer named functions when this improves maintainability.

Document meaningful domain types, interfaces, and non-obvious contracts.

### Example

```ts
/**
 * Calculates the final product price after applying a discount.
 *
 * @param price - Original product price.
 * @param discount - Discount percentage between 0 and 100.
 * @returns Final price after applying the discount.
 */
export function calculatePrice(
  price: number,
  discount: number,
): number {
  return price * (1 - discount / 100);
}
```

The example description is in English for illustration only. Actual project documentation must be written in `pt-BR`.

Documentation must remain accurate, concise, and consistent with the implementation.

## 7. Internationalization

Use `i18next` and `react-i18next` for application internationalization unless an equivalent solution is already established.

Initially, implement only Brazilian Portuguese (`pt-BR`).

- Keep all user-facing text in translation resources.
- Do not hardcode interface text in components, hooks, or business logic.
- Initialize and configure i18n centrally in `src/app/i18n.ts`.
- Organize translations under `src/locales/pt-BR/`.
- Use descriptive, consistent translation keys.
- Use interpolation for dynamic values.
- Preserve type safety for translation keys where supported.
- Use JavaScript internationalization APIs, such as `Intl.DateTimeFormat` and `Intl.NumberFormat`, for dates, numbers, and currencies when appropriate.
- Do not add other implemented languages unless explicitly requested.

### Example

`src/locales/pt-BR/translation.json`:

```json
{
  "common": {
    "save": "Salvar",
    "cancel": "Cancelar"
  },
  "welcome": {
    "title": "Bem-vindo, {{name}}"
  }
}
```

Component usage:

```tsx
/**
 * Exibe uma saudação utilizando o sistema de internacionalização.
 *
 * @returns Elemento React com o título traduzido.
 */
export function Welcome(): React.JSX.Element {
  const { t } = useTranslation();

  return <h1>{t("welcome.title", { name: "Usuário" })}</h1>;
}
```

Import `useTranslation` from `react-i18next` and configure the library before using this component.

## 8. Styling and Accessibility

Use Tailwind CSS for component styling.

- Follow the conventions of the installed Tailwind version.
- Prefer existing design tokens and consistent visual scales.
- Avoid dynamically constructed class names that static scanning cannot detect.
- Keep global CSS minimal.
- Avoid introducing competing styling systems without justification.
- Use semantic HTML and accessible names for interactive elements.
- Associate form controls with labels and meaningful validation feedback.
- Preserve keyboard navigation and visible focus indicators.
- Do not rely on color alone to communicate status.
- Use ARIA only when native HTML semantics are insufficient.

## 9. API Integration and Security

- Centralize shared HTTP configuration when needed.
- Define explicit request and response contracts.
- Validate untrusted external data at system boundaries.
- Handle loading, empty, success, and error states appropriately.
- Normalize API errors where shared behavior is needed.
- Avoid swallowing errors or fabricating fallback data.
- Never expose secrets through `VITE_*` environment variables.
- Never commit credentials or private environment files.
- Do not log tokens, credentials, or sensitive information.
- Treat frontend validation as complementary to backend validation and authorization.

Introduce additional validation libraries or API abstractions only when justified by actual requirements.

## 10. Testing and Quality

Use Vitest and React Testing Library when configured.

- Unit tests should cover meaningful pure functions and business rules.
- Component tests should verify observable rendering and user interactions.
- Integration tests should cover relevant interactions between modules.
- Add end-to-end tests when critical workflows justify browser-level verification.
- Add regression tests for bug fixes when practical.
- Prefer deterministic tests that verify behavior rather than implementation details.
- Avoid unnecessary mocking and artificial tests.

Before completing a task, run the applicable type checks, lint, tests, and production build using existing project scripts.

Report failed or unexecuted checks accurately.

## 11. Naming and Code Style

- Components: `PascalCase`.
- Hooks: `camelCase`, prefixed with `use`.
- Functions and variables: `camelCase`.
- Types and interfaces: `PascalCase`.
- Tests: follow the established `*.test.ts` and `*.test.tsx` conventions.
- Use descriptive names that communicate intent.
- Prefer early returns and straightforward control flow.
- Avoid nested ternaries and overly complex expressions.
- Follow ESLint and Prettier when configured.

Keep naming and formatting consistent throughout the project.

## 12. Dependencies and Configuration

- Use Node.js 24.22.0 as the project runtime baseline.
- Declare the Node.js version in `.nvmrc` and `package.json` where supported.
- Use npm and commit `package-lock.json`.
- Prefer existing dependencies and native platform capabilities.
- Evaluate compatibility, maintenance, security, and bundle impact before adding dependencies.
- Avoid unrelated dependency upgrades and unnecessary build configuration changes.
- Use existing `package.json` scripts for verification.

## 13. Completion Criteria

A change is complete when:

- The requested behavior is implemented.
- Type safety and module boundaries are preserved.
- Required TSDoc documentation is present and accurate.
- User-facing text follows the internationalization mechanism.
- Relevant tests and quality checks pass, or limitations are reported.
- No unrelated changes or unjustified suppressions are introduced.
- Documentation is updated when established conventions change.

Keep these guidelines aligned with the actual implementation. Prefer simple, evidence-based architectural decisions over speculative complexity.