import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Info } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const tools = [
  {
    id: 'search',
    name: 'Web Search',
    description: 'Search the web for real-time information',
    icon: '🔍',
  },
  {
    id: 'document-search',
    name: 'Document Search',
    description: 'Search through internal documents and knowledge base',
    icon: '📄',
  },
  {
    id: 'economic-data',
    name: 'Economic Data',
    description: 'Fetch economic data from FRED',
    icon: '📊',
  },
  {
    id: 'market-analysis',
    name: 'Market Analysis',
    description: 'Analyze market conditions for a location',
    icon: '📈',
  },
  {
    id: 'property-analysis',
    name: 'Property Analysis',
    description: 'Analyze a specific property',
    icon: '🏢',
  },
  {
    id: 'value-proposition',
    name: 'Value Proposition',
    description: 'Generate value propositions for properties',
    icon: '💡',
  },
];

interface ToolSelectorProps {
  selectedTools: string[];
  onToolsChange: (tools: string[]) => void;
}

export default function ToolSelector({ selectedTools, onToolsChange }: ToolSelectorProps) {
  const handleToolToggle = (toolId: string) => {
    const newSelectedTools = selectedTools.includes(toolId)
      ? selectedTools.filter(id => id !== toolId)
      : [...selectedTools, toolId];
    onToolsChange(newSelectedTools);
  };

  return (
    <div className="space-y-3 md:space-y-4">
      {tools.map((tool) => (
        <div
          key={tool.id}
          className={cn(
            "flex items-start space-x-2 md:space-x-3 p-3 md:p-4 rounded-lg transition-colors",
            "hover:bg-secondary/80",
            selectedTools.includes(tool.id) && "bg-secondary/50"
          )}
        >
          <Checkbox
            id={tool.id}
            checked={selectedTools.includes(tool.id)}
            onCheckedChange={() => handleToolToggle(tool.id)}
            className="mt-1"
          />
          <div className="flex-1 space-y-0.5 md:space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-base md:text-lg">{tool.icon}</span>
              <Label
                htmlFor={tool.id}
                className="text-xs md:text-sm font-medium leading-none cursor-pointer"
              >
                {tool.name}
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info className="h-3 w-3 md:h-4 md:w-4 text-muted-foreground hover:text-foreground transition-colors" />
                  </TooltipTrigger>
                  <TooltipContent side="left">
                    <p className="text-xs md:text-sm">{tool.description}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <p className="text-xs md:text-sm text-muted-foreground">
              {tool.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
} 