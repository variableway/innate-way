# Feature: Setup Monorepo with Desktop & Web Apps

## Priority: High
## Task Reference: Task 1 from Desktop-Web.md
## Related Issue: #3

## Description

Set up a pnpm monorepo structure with both a Tauri desktop application and a Next.js web application, following the `innate-next-mono` pattern.

## Acceptance Criteria

- [ ] `apps/desktop/` — Tauri 2.x + Next.js app with sidebar layout
- [ ] `apps/web/` — Next.js web app sharing same UI components
- [ ] `packages/ui/` — Shared shadcn/ui components with Tailwind CSS
- [ ] `packages/utils/` — Shared utilities (cn(), etc.)
- [ ] `packages/tsconfig/` — Shared TypeScript configs (base, nextjs, react-library)
- [ ] `pnpm-workspace.yaml` configured correctly
- [ ] Root `package.json` with workspace scripts
- [ ] Both apps can run `pnpm dev` successfully
- [ ] Use `tauri-desktop-app` skill templates as starting point

## Implementation Steps

### Step 1: Extend innate-next-mono monorepo
```bash
cd ../innate-next-mono
```

### Step 2: Add desktop app using tauri-desktop-app templates
```bash
# Copy from tauri-desktop-app skill templates
cp -r ../spark-skills/tauri-desktop-app/templates/apps/desktop apps/desktop
```

### Step 3: Create web app (Next.js only, no Tauri)
```bash
# Create web app from desktop template, removing src-tauri
cp -r apps/desktop apps/web
rm -rf apps/web/src-tauri
```

### Step 4: Update shared packages
- Ensure `packages/ui/` has shared components
- Ensure `packages/utils/` has shared utilities
- Ensure `packages/tsconfig/` has shared configs

### Step 5: Configure workspace
- Update `pnpm-workspace.yaml`
- Update root `package.json` scripts
- Configure both apps to use shared packages

### Step 6: Install and verify
```bash
pnpm install
pnpm dev  # Should start web app
pnpm tauri dev  # Should start desktop app
```

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `apps/desktop/` | Create | Tauri + Next.js desktop app |
| `apps/web/` | Create | Next.js web app |
| `packages/ui/` | Update | Add shadcn/ui components |
| `pnpm-workspace.yaml` | Update | Add new apps |
| `package.json` | Update | Add workspace scripts |

## Tech Stack

| Tech | Version | Purpose |
|------|---------|---------|
| Tauri | 2.x | Desktop framework |
| Next.js | 16+ | React framework |
| React | 19 | UI library |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 4 | Styling |
| shadcn/ui | latest | Component library |
| pnpm | workspace | Package manager |
