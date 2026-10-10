/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        // Spatial surface layers
        surface: {
          0: "hsl(var(--surface-0))",
          1: "hsl(var(--surface-1))",
          2: "hsl(var(--surface-2))",
          3: "hsl(var(--surface-3))",
        },
        // Clinical risk tokens
        risk: {
          low: "hsl(var(--risk-low))",
          moderate: "hsl(var(--risk-mod))",
          high: "hsl(var(--risk-high))",
          critical: "hsl(var(--risk-critical))",
        },
        // Spatial accent colors
        spatial: {
          coral: "hsl(var(--spatial-coral))",
          jade: "hsl(var(--spatial-jade))",
          amber: "hsl(var(--spatial-amber))",
          slate: "hsl(var(--spatial-slate))",
          porcelain: "hsl(var(--spatial-porcelain))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "calc(var(--radius) + 4px)",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
      },
      animation: {
        "pulse-subtle": "spatial-pulse-subtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spatial-glow": "spatial-glow 2s ease-in-out infinite",
        "fade-up": "spatial-fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
        "fade-in": "spatial-fade-in 0.4s ease-out both",
        "scale-in": "spatial-scale-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) both",
        "slide-in": "spatial-slide-in-right 0.4s cubic-bezier(0.16, 1, 0.3, 1) both",
      },
      boxShadow: {
        "spatial-sm": "0 2px 8px -2px hsl(var(--surface-0) / 0.4)",
        "spatial": "0 4px 16px -4px hsl(var(--surface-0) / 0.5)",
        "spatial-lg": "0 8px 32px -8px hsl(var(--surface-0) / 0.6)",
        "spatial-glow": "0 0 20px -4px hsl(var(--primary) / 0.15)",
      },
      backdropBlur: {
        "spatial": "16px",
        "spatial-strong": "24px",
      },
    },
  },
  plugins: [],
}
