<script>
  import "../app.css";

  let { children } = $props();
</script>

<div class="flex min-h-screen flex-col">
  <header class="border-b border-pine-800/80">
    <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
      <a href="/" class="flex items-center gap-2.5">
        <span class="flex size-9 items-center justify-center rounded-xl bg-emerald-500/15 text-lg">⛳</span>
        <span class="text-lg font-bold tracking-tight text-zinc-100">
          Golf<span class="text-emerald-400">Coach</span>
        </span>
      </a>
      <span class="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
        AI Swing Analysis
      </span>
    </div>
  </header>

  <main class="mx-auto w-full max-w-5xl flex-1 px-4 py-10 sm:px-6">
    {@render children()}
  </main>

  <footer class="border-t border-pine-800/80 py-6 text-center text-xs text-zinc-600">
    GolfCoach · AI-powered swing analysis
  </footer>
</div>
