import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(__dirname, "..");
const vendorDir = path.join(frontendDir, "public", "js", "vendor");
const ortDistDir = path.join(frontendDir, "node_modules", "onnxruntime-web", "dist");

fs.mkdirSync(vendorDir, { recursive: true });

await build({
  stdin: {
    contents: `
      import ninada from "ninada";
      import * as ort from "onnxruntime-web";

      if (ort?.env?.wasm) {
        ort.env.wasm.wasmPaths = "/js/vendor/";
      }

      if (typeof globalThis !== "undefined") {
        globalThis.ninada = ninada;
        globalThis.ort = ort;
      }
      if (typeof window !== "undefined") {
        window.__ninada = ninada;
        window.__ort = ort;
      }

      export { ninada, ort };
      export default ninada;
    `,
    resolveDir: frontendDir,
    loader: "js",
  },
  bundle: true,
  format: "esm",
  platform: "browser",
  outfile: path.join(vendorDir, "ninada.bundle.mjs"),
});

if (fs.existsSync(ortDistDir)) {
  for (const entry of fs.readdirSync(ortDistDir)) {
    if (entry.startsWith("ort-wasm-simd-threaded") && (entry.endsWith(".mjs") || entry.endsWith(".wasm"))) {
      fs.copyFileSync(path.join(ortDistDir, entry), path.join(vendorDir, entry));
    }
  }
}

console.log("Staged ninada.bundle.mjs and ort-wasm-simd-threaded runtime files in", vendorDir);