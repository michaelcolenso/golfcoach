<script>
  import { goto } from "$app/navigation";
  import { fade } from "svelte/transition";
  import { analysis } from "$lib/state/analysis.svelte.js";
  import { phaseInfo } from "$lib/phases.js";

  const result = $derived(analysis.result);
  const feedback = $derived(result?.feedback);

  // Per-frame analysis keyed by frame index, falling back to positional order.
  const frameCards = $derived(
    (result?.selected_frames ?? []).map((image, i) => ({
      image,
      analysis: feedback?.frames?.find((f) => f.frame_index === i) ?? feedback?.frames?.[i],
    }))
  );

  $effect(() => {
    if (!analysis.result) goto("/");
  });

  function startOver() {
    analysis.clear();
    goto("/");
  }
</script>

{#if result && feedback}
  <div in:fade={{ duration: 300 }}>
    <div class="mb-10 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="font-display text-4xl text-zinc-50">Swing Analysis</h1>
        <p class="mt-2 max-w-2xl leading-relaxed text-zinc-400">{feedback.overall_feedback}</p>
      </div>
      <button
        type="button"
        class="rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-pine-950 shadow-lg shadow-emerald-500/25 transition hover:bg-emerald-400"
        onclick={startOver}
      >
        Analyze another swing
      </button>
    </div>

    <div class="mb-10 grid gap-6 lg:grid-cols-2">
      {#if feedback.strengths?.length}
        <section class="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-6">
          <h2 class="mb-4 text-lg font-semibold text-emerald-300">What you're doing well</h2>
          <ul class="space-y-3">
            {#each feedback.strengths as strength}
              <li class="flex gap-3 text-sm leading-relaxed text-zinc-300">
                <svg class="mt-0.5 size-5 shrink-0 text-emerald-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd" />
                </svg>
                {strength}
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      {#if feedback.recommendations?.length}
        <section class="rounded-2xl border border-amber-500/25 bg-amber-500/5 p-6">
          <h2 class="mb-4 text-lg font-semibold text-amber-300">What to work on</h2>
          <ol class="space-y-3">
            {#each feedback.recommendations as rec, i}
              <li class="flex gap-3 text-sm leading-relaxed text-zinc-300">
                <span class="flex size-5 shrink-0 items-center justify-center rounded-full bg-amber-500/20 text-xs font-bold text-amber-300">{i + 1}</span>
                {rec}
              </li>
            {/each}
          </ol>
        </section>
      {/if}
    </div>

    <section class="mb-10">
      <h2 class="mb-5 text-xl font-bold text-zinc-100">Frame-by-frame breakdown</h2>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {#each frameCards as { image, analysis: frame }, i}
          <article class="overflow-hidden rounded-2xl border border-pine-700 bg-pine-900/70 transition hover:border-pine-600">
            <div class="relative">
              <img
                src={`data:image/jpeg;base64,${image}`}
                alt="Swing frame {i + 1}{frame ? ` — ${phaseInfo(frame.phase).label}` : ''}"
                loading="lazy"
                class="aspect-video w-full bg-black object-contain"
              />
              <span class="absolute left-3 top-3 rounded-md bg-black/60 px-2 py-0.5 font-mono text-xs text-zinc-300">#{i + 1}</span>
              {#if frame}
                <span class="absolute right-3 top-3 rounded-full border px-2.5 py-0.5 text-xs font-medium backdrop-blur {phaseInfo(frame.phase).classes}">
                  {phaseInfo(frame.phase).label}
                </span>
              {/if}
            </div>
            <div class="space-y-3 p-4">
              <p class="text-sm leading-relaxed text-zinc-300">
                {frame?.observation ?? "No feedback available for this frame."}
              </p>
              {#if frame?.tip}
                <p class="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 text-sm leading-relaxed text-emerald-200">
                  <span class="font-semibold">Tip:</span> {frame.tip}
                </p>
              {/if}
            </div>
          </article>
        {/each}
      </div>
    </section>

    {#if feedback.drills?.length}
      <section class="rounded-2xl border border-pine-700 bg-pine-900/70 p-6">
        <h2 class="mb-4 text-lg font-semibold text-zinc-100">🏌️ Practice drills</h2>
        <ul class="grid gap-4 md:grid-cols-3">
          {#each feedback.drills as drill}
            <li class="rounded-xl border border-pine-600 bg-pine-800/60 p-4 text-sm leading-relaxed text-zinc-300">{drill}</li>
          {/each}
        </ul>
      </section>
    {/if}
  </div>
{/if}
