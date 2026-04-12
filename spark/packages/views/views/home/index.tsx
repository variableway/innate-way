import { Button } from "@spark/ui/components/button";

export function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <h1 className="text-4xl font-bold tracking-tight">Spark</h1>
      <p className="text-lg text-muted-foreground max-w-md text-center">
        Personal AI Assistant — Ideas, Tasks, Agents, all in one workspace.
      </p>
      <div className="flex gap-3">
        <Button>Get Started</Button>
        <Button variant="outline">Learn More</Button>
      </div>
    </div>
  );
}
