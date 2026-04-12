import { Button } from "@innate/ui/components/button";

function App() {
  return (
    <div className="flex flex-col h-screen">
      {/* Toolbar */}
      <div
        className="flex items-center h-12 px-4 border-b bg-background"
        data-tauri-drag-region
      >
        <span className="text-lg font-bold">Innate</span>
        <div className="flex-1" data-tauri-drag-region />
        <span className="text-xs text-muted-foreground">v0.0.1</span>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-12 border-r bg-muted/30 flex flex-col items-center py-4 gap-4">
          <NavButton icon="💡" label="Ideas" />
          <NavButton icon="📋" label="Tasks" />
          <NavButton icon="🤖" label="Agents" />
          <NavButton icon="🔧" label="Skills" />
          <div className="flex-1" />
          <NavButton icon="⚙️" label="Settings" />
        </div>

        {/* Content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold">Innate</h1>
            <p className="text-muted-foreground">
              Personal AI Assistant Desktop
            </p>
            <Button>Get Started</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function NavButton({ icon, label }: { icon: string; label: string }) {
  return (
    <button
      className="w-8 h-8 rounded-md hover:bg-accent flex items-center justify-center text-sm transition-colors"
      title={label}
    >
      {icon}
    </button>
  );
}

export default App;
