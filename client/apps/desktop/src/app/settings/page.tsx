"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@innate/ui/components/ui/card";
import { Input } from "@innate/ui/components/ui/input";
import { Label } from "@innate/ui/components/ui/label";
import { Button } from "@innate/ui/components/ui/button";

async function invoke<T>(command: string, args?: Record<string, unknown>): Promise<T | null> {
  if ("__TAURI_INTERNALS__" in window) {
    const { invoke: tauriInvoke } = await import("@tauri-apps/api/core");
    return tauriInvoke<T>(command, args);
  }
  return null;
}

export default function Settings() {
  const [categoryPath, setCategoryPath] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      const path = await invoke<string>("get_default_category_path");
      if (path) setCategoryPath(path);
    }
    load();
  }, []);

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Category Folder</CardTitle>
          <CardDescription>
            Configure the folder where your categories are stored.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="categoryPath">Category Folder Path</Label>
            <div className="flex gap-2">
              <Input
                id="categoryPath"
                value={categoryPath}
                onChange={(e) => setCategoryPath(e.target.value)}
                placeholder="~/.innate/categories"
              />
              <Button onClick={handleSave}>
                {saved ? "Saved!" : "Save"}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Default: ~/.innate/categories (matches CLI default path)
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
