import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import boundaries from "eslint-plugin-boundaries";
import tseslint from "typescript-eslint";

const ELEMENTS = [
  { type: "shared",       pattern: "src/engine/shared/**/*",       mode: "file" },
  { type: "bootstrap",    pattern: "src/engine/bootstrap/**/*",    mode: "file" },
  { type: "curation",     pattern: "src/engine/curation/**/*",     mode: "file" },
  { type: "adjudication", pattern: "src/engine/adjudication/**/*", mode: "file" },
  { type: "allocation",   pattern: "src/engine/allocation/**/*",   mode: "file" },
  { type: "reputation",   pattern: "src/engine/reputation/**/*",   mode: "file" },
  { type: "lifecycle",    pattern: "src/engine/lifecycle/**/*",    mode: "file" },
  { type: "inspector",    pattern: "src/inspector/**/*",           mode: "file" },
  { type: "tests",        pattern: "tests/**/*",                   mode: "file" },
];

const ALLOWED = [
  { from: "shared",       allow: [] },
  { from: "bootstrap",    allow: ["shared", "bootstrap"] },
  { from: "curation",     allow: ["shared", "curation"] },
  { from: "adjudication", allow: ["shared", "adjudication"] },
  { from: "allocation",   allow: ["shared", "allocation"] },
  { from: "reputation",   allow: ["shared", "reputation"] },
  {
    from: "lifecycle",
    allow: [
      "shared",
      "lifecycle",
      "curation",
      "adjudication",
      "allocation",
      "reputation",
      "bootstrap",
    ],
  },
  { from: "inspector",    allow: ["shared", "lifecycle", "bootstrap", "inspector"] },
  { from: "tests",        allow: ["shared", "bootstrap", "curation", "adjudication", "allocation", "reputation", "lifecycle", "inspector", "tests"] },
];

export default tseslint.config(
  { ignores: ["dist", "node_modules"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      boundaries,
    },
    settings: {
      "boundaries/elements": ELEMENTS,
      "boundaries/include": ["src/**/*", "tests/**/*"],
      "import/resolver": {
        typescript: {
          alwaysTryTypes: true,
          project: "./tsconfig.json",
        },
        node: true,
      },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "boundaries/element-types": [
        "error",
        {
          default: "disallow",
          rules: ALLOWED.map(({ from, allow }) => ({
            from: [from],
            allow,
          })),
        },
      ],
    },
  },
);
