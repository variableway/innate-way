export function StatusBar() {
  return (
    <div className="flex items-center justify-between border-t bg-muted/50 px-4 py-1.5 text-xs text-muted-foreground">
      <div className="flex items-center gap-3">
        <span>🌐 web</span>
      </div>
      <div>v0.1.0</div>
    </div>
  );
}
