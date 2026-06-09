<script>
  import { onMount } from "svelte";

  // The analysis is a single request, so progress through the stages is
  // simulated on a timer that roughly tracks real processing time.
  const stages = [
    { label: "Uploading your video", after: 0 },
    { label: "Extracting swing frames", after: 3000 },
    { label: "Detecting key positions", after: 6000 },
    { label: "Your AI coach is reviewing the swing", after: 9000 },
  ];

  let elapsed = $state(0);
  const active = $derived(stages.filter((s) => elapsed >= s.after).length - 1);

  onMount(() => {
    const start = Date.now();
    const timer = setInterval(() => (elapsed = Date.now() - start), 250);
    return () => clearInterval(timer);
  });
</script>

<div class="mx-auto w-full max-w-md rounded-2xl border border-pine-700 bg-pine-900/80 p-8">
  <div class="mb-6 flex justify-center">
    <div class="size-12 animate-spin rounded-full border-4 border-pine-600 border-t-emerald-400"></div>
  </div>
  <ul class="space-y-4">
    {#each stages as stage, i}
      <li class="flex items-center gap-3 text-sm transition-colors duration-500
        {i < active ? 'text-emerald-400' : i === active ? 'text-zinc-100' : 'text-zinc-600'}">
        {#if i < active}
          <svg class="size-5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd" />
          </svg>
        {:else if i === active}
          <span class="relative flex size-5 shrink-0 items-center justify-center">
            <span class="absolute size-3 animate-ping rounded-full bg-emerald-400/60"></span>
            <span class="size-2 rounded-full bg-emerald-400"></span>
          </span>
        {:else}
          <span class="flex size-5 shrink-0 items-center justify-center">
            <span class="size-2 rounded-full bg-zinc-700"></span>
          </span>
        {/if}
        {stage.label}
      </li>
    {/each}
  </ul>
</div>
