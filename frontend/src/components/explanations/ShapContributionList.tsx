import React from "react"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import type { FeatureContributionItem } from "@/types/explanation"
import { formatShapValue } from "@/lib/utils"

interface ShapContributionListProps {
  title: string
  subtitle: string
  items: FeatureContributionItem[]
  type: "positive" | "negative"
  className?: string
}

export const ShapContributionList: React.FC<ShapContributionListProps> = ({
  title,
  subtitle,
  items,
  type,
  className = "",
}) => {
  const isPos = type === "positive"

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between border-b border-border/40 pb-2">
        <div>
          <h4
            className={`text-xs font-semibold uppercase tracking-wider font-mono ${
              isPos ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {title}
          </h4>
          <p className="text-[11px] text-muted-foreground">{subtitle}</p>
        </div>
        <span className="text-[11px] font-mono text-muted-foreground/70">
          {items.length} factors
        </span>
      </div>

      <div className="space-y-2">
        {items.length === 0 ? (
          <p className="text-xs text-muted-foreground italic py-3 text-center">
            No dominant {type} factors detected.
          </p>
        ) : (
          items.map((item, idx) => (
            <div
              key={`${item.feature}-${idx}`}
              className="flex items-center justify-between p-2.5 rounded-xl bg-surface-2/60 border border-border/50 text-xs hover:bg-surface-3/70 transition-colors shadow-xs"
            >
              <div className="space-y-0.5 max-w-[70%]">
                <span className="font-medium text-foreground block truncate" title={item.label}>
                  {item.label}
                </span>
                <span className="text-[10px] text-muted-foreground font-mono">
                  Input value: {item.value}
                </span>
              </div>

              <div className="flex items-center gap-1.5 shrink-0">
                <span
                  className={`font-mono font-semibold px-2 py-0.5 rounded-md text-xs ${
                    isPos
                      ? "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                      : "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                  }`}
                  title="SHAP attribution in log-odds model score space"
                >
                  {formatShapValue(item.shap_value)}
                </span>
                {isPos ? (
                  <ArrowUpRight className="w-3.5 h-3.5 text-rose-400" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
