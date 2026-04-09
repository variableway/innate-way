"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@innate/ui/components/ui/card";
import { Button } from "@innate/ui/components/ui/button";
import { Input } from "@innate/ui/components/ui/input";
import { Label } from "@innate/ui/components/ui/label";
import { Textarea } from "@innate/ui/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@innate/ui/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@innate/ui/components/ui/alert-dialog";
import { FolderOpen, Plus, Trash2, Pencil } from "lucide-react";

interface Category {
  name: string;
  display_name: string;
  count: number;
  description: string;
}

async function invoke<T>(command: string, args?: Record<string, unknown>): Promise<T | null> {
  if ("__TAURI_INTERNALS__" in window) {
    const { invoke: tauriInvoke } = await import("@tauri-apps/api/core");
    return tauriInvoke<T>(command, args);
  }
  return null;
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryPath, setCategoryPath] = useState<string>("");
  const [addOpen, setAddOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDisplayName, setNewDisplayName] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategories();
  }, []);

  async function loadCategories() {
    setLoading(true);
    setError(null);
    try {
      const path = await invoke<string>("get_default_category_path");
      if (path) {
        setCategoryPath(path);
        const cats = await invoke<Category[]>("list_categories", { rootDir: path });
        setCategories(cats || []);
      }
    } catch {
      setError("Failed to load categories");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd() {
    if (!newName.trim()) return;
    try {
      await invoke("create_category", {
        rootDir: categoryPath,
        name: newName.trim(),
        displayName: newDisplayName.trim() || null,
        description: newDescription.trim() || null,
      });
      setAddOpen(false);
      setNewName("");
      setNewDisplayName("");
      setNewDescription("");
      loadCategories();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleDelete(name: string) {
    try {
      await invoke("delete_category", { rootDir: categoryPath, name });
      loadCategories();
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Categories</h1>
          <p className="text-sm text-muted-foreground">
            {categories.length}/10 categories
          </p>
        </div>
        <Dialog open={addOpen} onOpenChange={setAddOpen}>
          <DialogTrigger asChild>
            <Button disabled={categories.length >= 10}>
              <Plus className="mr-2 h-4 w-4" />
              Add Category
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Category</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="my-category"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value.replace(/[^a-zA-Z0-9\-_]/g, ""))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="displayName">Display Name</Label>
                <Input
                  id="displayName"
                  placeholder="My Category"
                  value={newDisplayName}
                  onChange={(e) => setNewDisplayName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="What is this category for?"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button onClick={handleAdd} disabled={!newName.trim()} className="w-full">
                Create
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {error && !addOpen && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : categories.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No categories yet</p>
            <p className="text-sm text-muted-foreground">
              Create your first category to start organizing.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat) => (
            <Card key={cat.name}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-base font-medium">
                  {cat.display_name}
                </CardTitle>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete &quot;{cat.display_name}&quot;?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete the category folder and all its contents.
                        {cat.count > 0 && ` This category contains ${cat.count} entries.`}
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDelete(cat.name)}>
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardHeader>
              <CardContent>
                {cat.description && (
                  <p className="text-sm text-muted-foreground mb-2">{cat.description}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  {cat.count} entries
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
