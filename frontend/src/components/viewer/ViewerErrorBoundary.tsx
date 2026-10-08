import { Component, type ErrorInfo, type ReactNode } from "react"
import { AlertTriangle, RefreshCw } from "lucide-react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ViewerErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("CoroVista 3D Viewer WebGL Error:", error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div
          className="border border-destructive/30 bg-destructive/5 rounded-xl p-6 flex flex-col items-center justify-center text-center min-h-[360px]"
          role="alert"
          aria-live="assertive"
        >
          <div className="w-12 h-12 rounded-xl bg-destructive/10 text-destructive flex items-center justify-center mb-3">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h4 className="text-base font-semibold text-foreground mb-1">
            3D Graphics Rendering Issue
          </h4>
          <p className="text-xs text-muted-foreground max-w-sm mb-4 leading-relaxed">
            The WebGL canvas encountered an error loading the anatomical model ({this.state.error?.message || "Unknown error"}). Your numerical risk predictions and SHAP explanations remain fully accessible.
          </p>
          <button
            type="button"
            onClick={this.handleReset}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-secondary hover:bg-secondary/80 text-foreground transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload 3D Scene</span>
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
