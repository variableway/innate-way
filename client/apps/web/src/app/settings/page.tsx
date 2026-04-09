import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@innate/ui/components/ui/card";

export default function Settings() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Web Mode</CardTitle>
          <CardDescription>
            Running in web browser mode. Categories are stored in browser localStorage.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            For full filesystem access, use the desktop application.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
