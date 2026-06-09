import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // SPA mode: the FastAPI backend serves client/build with index.html fallback.
    adapter: adapter({
      fallback: "index.html",
    }),
  },
  preprocess: vitePreprocess(),
};

export default config;
