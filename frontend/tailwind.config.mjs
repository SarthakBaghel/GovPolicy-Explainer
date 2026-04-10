/** @type {import('tailwindcss').Config} */
const config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
    "./hooks/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#f7f7f8",
        foreground: "#111827",
        card: "#ffffff",
        border: "#e5e7eb",
        muted: "#6b7280",
        primary: {
          DEFAULT: "#111827",
          foreground: "#ffffff",
          soft: "#f3f4f6",
        },
        success: "#166534",
        danger: "#b91c1c",
        warning: "#92400e",
      },
      borderRadius: {
        lg: "0.625rem",
        xl: "0.875rem",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0, 0, 0, 0.06)",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Helvetica Neue", "Arial", "Noto Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
