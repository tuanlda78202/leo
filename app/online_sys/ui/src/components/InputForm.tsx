import { Send, StopCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";

// Updated InputFormProps
interface InputFormProps {
  onSubmit: (inputValue: string, effort: string, model: string) => void;
  onCancel: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [internalInputValue, setInternalInputValue] = useState("");

  // Use default values instead of user selection
  const effort = "medium";
  const model = "gemini-2.5-flash-preview-04-17";

  const handleInternalSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!internalInputValue.trim()) return;
    onSubmit(internalInputValue, effort, model);
    setInternalInputValue("");
  };

  const handleInternalKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleInternalSubmit();
    }
  };

  const isSubmitDisabled = !internalInputValue.trim() || isLoading;

  return (
    <div className="p-3">
      <form onSubmit={handleInternalSubmit} className="flex flex-col gap-2">
        <div className="flex flex-row items-center justify-between rounded-3xl break-words min-h-7 bg-muted border border-border px-4 pt-3">
          <Textarea
            value={internalInputValue}
            onChange={(e) => setInternalInputValue(e.target.value)}
            onKeyDown={handleInternalKeyDown}
            placeholder="Ask Leo anything..."
            className="w-full text-foreground placeholder-muted-foreground resize-none border-0 focus:outline-none focus:ring-0 outline-none focus-visible:ring-0 shadow-none md:text-base min-h-[56px] max-h-[200px] bg-transparent !bg-transparent dark:!bg-transparent"
            rows={1}
          />
          <div className="-mt-3">
            {isLoading ? (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="text-red-500 hover:text-red-400 hover:bg-red-500/10 p-2 cursor-pointer rounded-full transition-all duration-200"
                onClick={onCancel}
              >
                <StopCircle className="h-5 w-5" />
              </Button>
            ) : (
              <Button
                type="submit"
                variant="ghost"
                className={`${isSubmitDisabled
                  ? "text-muted-foreground"
                  : "text-blue-500 hover:text-blue-400 hover:bg-blue-500/10"
                  } p-2 cursor-pointer rounded-full transition-all duration-200 text-base`}
                disabled={isSubmitDisabled}
              >
                <Send className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>
      </form>

      {/* Add disclaimer like ChatGPT */}
      <div className="text-center text-xs text-muted-foreground mt-2">
        Leo can make mistakes. Check important info.
      </div>
    </div>
  );
};
