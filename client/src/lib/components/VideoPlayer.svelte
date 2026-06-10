<script>
  let { videoUrl, currentTime = $bindable(0), duration = $bindable(0), clipDuration = 3 } = $props();

  let video = $state();
  let paused = $state(true);

  const clipEnd = $derived(Math.min(currentTime + clipDuration, duration || Infinity));

  function format(seconds) {
    if (!Number.isFinite(seconds)) return "0:00.0";
    const m = Math.floor(seconds / 60);
    const s = (seconds % 60).toFixed(1).padStart(4, "0");
    return `${m}:${s}`;
  }

  function step(delta) {
    video.pause();
    currentTime = Math.min(Math.max(0, currentTime + delta), duration);
  }
</script>

<div class="overflow-hidden rounded-2xl border border-pine-700 bg-pine-900/80 shadow-2xl shadow-black/40">
  <!-- svelte-ignore a11y_media_has_caption -->
  <video
    bind:this={video}
    bind:currentTime
    bind:duration
    bind:paused
    src={videoUrl}
    playsinline
    class="max-h-[55vh] w-full bg-black object-contain"
  ></video>

  <div class="space-y-3 p-4">
    <!-- Scrubber with the analysis window highlighted -->
    <div class="relative">
      <div
        class="pointer-events-none absolute top-1/2 h-2 -translate-y-1/2 rounded-full bg-emerald-400/30"
        style="left: {duration ? (currentTime / duration) * 100 : 0}%; width: {duration ? ((clipEnd - currentTime) / duration) * 100 : 0}%"
      ></div>
      <input
        type="range"
        min="0"
        max={duration || 0}
        step="0.033"
        bind:value={currentTime}
        oninput={() => video.pause()}
        aria-label="Swing start time"
        class="relative h-2 w-full cursor-pointer appearance-none rounded-full bg-pine-700 accent-emerald-400"
      />
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-1.5">
        <button
          type="button"
          class="rounded-lg border border-pine-600 px-3 py-1.5 text-sm text-zinc-300 transition hover:border-emerald-500/50 hover:text-white"
          onclick={() => (paused ? video.play() : video.pause())}
        >
          {paused ? "▶ Play" : "❚❚ Pause"}
        </button>
        <button
          type="button"
          class="rounded-lg border border-pine-600 px-2.5 py-1.5 text-sm text-zinc-300 transition hover:border-emerald-500/50 hover:text-white"
          onclick={() => step(-1 / 30)}
          aria-label="Back one frame"
        >−1f</button>
        <button
          type="button"
          class="rounded-lg border border-pine-600 px-2.5 py-1.5 text-sm text-zinc-300 transition hover:border-emerald-500/50 hover:text-white"
          onclick={() => step(1 / 30)}
          aria-label="Forward one frame"
        >+1f</button>
      </div>
      <p class="font-mono text-sm text-zinc-400">
        <span class="text-emerald-400">{format(currentTime)}</span>
        <span class="mx-1 text-zinc-600">→ {format(clipEnd)}</span>
        / {format(duration)}
      </p>
    </div>
  </div>
</div>
