# Feature: Category Management

## Priority: High
## Task Reference: Task 2 from Desktop-Web.md
## Related Issue: #3

## Description

Build category management UI that reads from the TUI category folder structure. Users can view, add, rename, and delete categories through the desktop/web application. A settings page allows configuring the category folder path.

## Acceptance Criteria

- [ ] Category list view showing all categories with name, count, description
- [ ] Add new category (respecting max 10 limit)
- [ ] Delete category (with confirmation if entries exist)
- [ ] Rename category
- [ ] Settings page to configure category folder path
- [ ] Default category folder matches CLI default path
- [ ] Desktop app reads categories via Tauri IPC (Rust filesystem access)
- [ ] Web app reads categories via API or fallback to browser storage
- [ ] Shared `capture-core` package with TypeScript category logic

## Data Model

Derived from `capture_tui/models/category.py`:

```typescript
interface Category {
  name: string;
  display_name: string;
  count: number;
  created_at: string;      // ISO date
  last_entry: string | null; // ISO date
  description: string;
}
```

## UI Components Needed

### Category List Page
- Grid/list of category cards showing name, count, last entry date
- "Add Category" button (disabled when count >= 10)
- Each card has edit/rename and delete actions

### Add/Edit Category Dialog
- Name field (alphanumeric, hyphens, underscores)
- Display name field
- Description textarea
- Validation: max 10 categories, unique names

### Settings Page
- Category folder path input
- Browse button (desktop: native file picker via Tauri)
- Default path: matches CLI default
- Validation: path must exist and be a directory

## Implementation Steps

### Step 1: Create shared `capture-core` package
```bash
mkdir -p packages/capture-core/src
```

Implement TypeScript equivalents of:
- `models/category.ts` — Category interface and types
- `category-manager.ts` — CRUD logic, max 10 constraint
- `types.ts` — Shared type definitions

### Step 2: Add Tauri commands (Desktop)
In `apps/desktop/src-tauri/src/lib.rs`:
- `list_categories(path)` — Read folder structure
- `create_category(path, name)` — Create folder + index entry
- `delete_category(path, name)` — Remove folder + index entry
- `rename_category(path, old_name, new_name)` — Rename folder
- `get_default_category_path()` — Get OS-specific default path

### Step 3: Build UI components
- Category list page (`app/categories/page.tsx`)
- Category card component
- Add/Edit dialog
- Delete confirmation dialog
- Settings page with folder config

### Step 4: Wire up data flow
- Desktop: React → Tauri IPC → Rust filesystem
- Web: React → API endpoint → filesystem (or localStorage fallback)

## Dependencies

- Feature 001 (monorepo setup) must be complete
- Tauri IPC setup for desktop file system access
- shadcn/ui components: Card, Dialog, Input, Button, AlertDialog, Settings layout

## Constraints

- Maximum 10 categories (from TUI design)
- Category names: alphanumeric + hyphens + underscores only
- Cannot delete category with entries unless force=true
