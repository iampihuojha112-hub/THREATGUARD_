import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-start gap-3 rounded-lg border border-danger/30 bg-danger/10 p-5">
      <div className="flex items-center gap-2 text-danger">
        <AlertTriangle className="h-5 w-5" />
        <span className="font-medium">Could not load data</span>
      </div>
      <p className="text-sm text-foreground/80">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
