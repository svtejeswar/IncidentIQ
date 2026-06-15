import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: {
          DEFAULT: "var(--surface)",
          2: "var(--surface-2)",
        },
        border: {
          DEFAULT: "var(--border)",
          2: "var(--border-2)",
        },
        foreground: {
          DEFAULT: "var(--foreground)",
          2: "var(--foreground-2)",
          3: "var(--foreground-3)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          dim: "var(--primary-dim)",
          fg: "var(--primary-fg)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          dim: "var(--destructive-dim)",
        },
        success: {
          DEFAULT: "var(--success)",
          dim: "var(--success-dim)",
        },
        warning: {
          DEFAULT: "var(--warning)",
          dim: "var(--warning-dim)",
        },
        orange: {
          DEFAULT: "var(--orange)",
          dim: "var(--orange-dim)",
        },
      },
      keyframes: {
        "bounce-dot": {
          "0%, 80%, 100%": { transform: "translateY(0)" },
          "40%": { transform: "translateY(-6px)" },
        },
      },
      animation: {
        "bounce-dot": "bounce-dot 1.4s infinite ease-in-out",
      },
    },
  },
  plugins: [],
};

export default config;
