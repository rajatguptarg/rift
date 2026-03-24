const plugin = require("tailwindcss/plugin");

module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#131313",
        surface: "#131313",
        "surface-container-lowest": "#0E0E0E",
        "surface-container-low": "#1B1B1B",
        "surface-container": "#1F1F1F",
        "surface-container-high": "#2A2A2A",
        "surface-container-highest": "#353535",
        "secondary-fixed": "#1A1A2E",
        "secondary-fixed-hover": "#1F1F3D",
        "primary-container": "#FF5543",
        primary: "#FFB4A9",
        "primary-fixed": "#FFDAD5",
        tertiary: "#45D8ED",
        "tertiary-container": "#00A0B1",
        "on-tertiary-container": "#001F24",
        "secondary-container": "#3A3A5C",
        secondary: "#C8C5F4",
        "error-container": "#93000A",
        "on-error-container": "#FFDAD6",
        "on-surface": "#E2E2E2",
        "on-background": "#E2E2E2",
        "on-surface-variant": "#E4BEB8",
        "on-primary-container": "#5C0001",
        "outline-variant": "#5B403C",
        error: "#FFB4AB",
      },
      fontFamily: {
        headline: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "sans-serif"],
        label: ["Inter", "sans-serif"],
        mono: ['"Fira Code"', "monospace"],
      },
      borderRadius: {
        DEFAULT: "1rem",
        lg: "2rem",
        xl: "3rem",
        full: "9999px",
        none: "0px",
      },
      fontSize: {
        "7xl": ["4.5rem", { lineHeight: "1" }],
      },
    },
  },
  plugins: [
    plugin(({ addUtilities }) => {
      addUtilities({
        ".kinetic-gradient": {
          background: "radial-gradient(ellipse at center, #FF5543 0%, #FFB4A9 100%)",
        },
        ".crosshatch-bg": {
          backgroundImage:
            "radial-gradient(circle, rgba(91,64,60,0.10) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        },
        ".scrollbar-thin": {
          scrollbarWidth: "thin",
          scrollbarColor: "#353535 #131313",
        },
      });
    }),
  ],
};
