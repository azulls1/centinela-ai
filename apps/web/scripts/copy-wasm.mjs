/**
 * Copy ONNX Runtime WASM binaries to public/ so Vite dev server serves them
 * with the correct application/wasm MIME type.
 * Runs automatically after npm install via postinstall script.
 */
import { copyFileSync, existsSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')
const publicDir = join(root, 'public')
const ortDist = join(root, 'node_modules', 'onnxruntime-web', 'dist')

const files = [
  'ort-wasm-simd-threaded.jsep.wasm',
  'ort-wasm-simd-threaded.wasm',
]

if (!existsSync(publicDir)) mkdirSync(publicDir, { recursive: true })

for (const file of files) {
  const src = join(ortDist, file)
  const dest = join(publicDir, file)
  if (existsSync(src)) {
    copyFileSync(src, dest)
    console.log(`[copy-wasm] ${file} -> public/`)
  }
}
