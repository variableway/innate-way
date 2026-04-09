import { Card, CardContent, CardHeader, CardTitle } from "@innate/ui/components/ui/card";
import { Badge } from "@innate/ui/components/ui/badge";

export default function Home() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Welcome to Innate Capture</h1>
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Capture and organize your thoughts with categories.
          </p>
          <div className="flex gap-2">
            <Badge variant="secondary">Next.js</Badge>
            <Badge variant="secondary">shadcn/ui</Badge>
            <Badge variant="secondary">Web</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
