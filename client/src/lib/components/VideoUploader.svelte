<script>
  let { onselect } = $props();

  let dragging = $state(false);
  let error = $state("");
  let fileInput;

  const MAX_BYTES = 200 * 1024 * 1024;

  function accept(file) {
    error = "";
    if (!file) return;
    if (!file.type.startsWith("video/")) {
      error = "Please choose a video file (MP4, MOV, WebM…).";
      return;
    }
    if (file.size > MAX_BYTES) {
      error = "That video is over the 200MB limit. Try trimming it first.";
      return;
    }
    onselect(file);
  }

  function handleDrop(event) {
    event.preventDefault();
    dragging = false;
    accept(event.dataTransfer?.files?.[0]);
  }
</script>

<div
  role="button"
  tabindex="0"
  aria-label="Upload a video of your golf swing"
  class="group relative flex w-full cursor-pointer flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-8 py-16 transition-all duration-200
    {dragging
      ? 'border-emerald-400 bg-emerald-400/10 scale-[1.01]'
      : 'border-pine-600 bg-pine-900/60 hover:border-emerald-500/60 hover:bg-pine-800/60'}"
  ondragover={(e) => { e.preventDefault(); dragging = true; }}
  ondragleave={() => (dragging = false)}
  ondrop={handleDrop}
  onclick={() => fileInput.click()}
  onkeydown={(e) => (e.key === "Enter" || e.key === " ") && fileInput.click()}
>
  <div class="flex size-16 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-400 transition-transform duration-200 group-hover:scale-110">
    <svg xmlns="http://www.w3.org/2000/svg" class="size-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
    </svg>
  </div>
  <div class="text-center">
    <p class="text-lg font-semibold text-zinc-100">Drop your swing video here</p>
    <p class="mt-1 text-sm text-zinc-400">or <span class="text-emerald-400 underline underline-offset-2">browse files</span> — MP4, MOV or WebM up to 200MB</p>
  </div>
  <input
    bind:this={fileInput}
    type="file"
    accept="video/*"
    class="hidden"
    onchange={(e) => accept(e.currentTarget.files?.[0])}
  />
</div>

{#if error}
  <p class="mt-3 text-sm text-red-400" role="alert">{error}</p>
{/if}
