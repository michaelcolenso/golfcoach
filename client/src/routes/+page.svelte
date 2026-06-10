<script>
  import { goto } from "$app/navigation";
  import { fade, fly } from "svelte/transition";
  import VideoUploader from "$lib/components/VideoUploader.svelte";
  import VideoPlayer from "$lib/components/VideoPlayer.svelte";
  import AnalysisProgress from "$lib/components/AnalysisProgress.svelte";
  import { analysis } from "$lib/state/analysis.svelte.js";

  let videoFile = $state(null);
  let videoUrl = $state("");
  let currentTime = $state(0);
  let duration = $state(0);
  let clipDuration = $state(3);
  let isLoading = $state(false);
  let errorMessage = $state("");

  function handleFileSelected(file) {
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    videoFile = file;
    videoUrl = URL.createObjectURL(file);
    currentTime = 0;
    errorMessage = "";
  }

  function reset() {
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    videoFile = null;
    videoUrl = "";
    errorMessage = "";
  }

  async function handleAnalyze() {
    isLoading = true;
    errorMessage = "";

    try {
      const formData = new FormData();
      formData.append("video", videoFile);
      formData.append("start_time", currentTime.toString());
      formData.append("duration", clipDuration.toString());

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? `Analysis failed (${response.status})`);
      }

      analysis.set(await response.json());
      goto("/results");
    } catch (error) {
      errorMessage = error.message || "Failed to analyze the video. Please try again.";
    } finally {
      isLoading = false;
    }
  }
</script>

{#if isLoading}
  <div class="flex flex-col items-center gap-6 pt-12" in:fade>
    <h2 class="font-display text-3xl text-zinc-100">Analyzing your swing<span class="text-emerald-400">…</span></h2>
    <AnalysisProgress />
  </div>
{:else if !videoUrl}
  <section class="mx-auto max-w-2xl pt-8 text-center" in:fade>
    <h1 class="font-display text-5xl leading-tight text-zinc-50 sm:text-6xl">
      Your swing, reviewed by an <em class="text-emerald-400">AI coach</em>
    </h1>
    <p class="mx-auto mt-5 max-w-lg text-lg text-zinc-400">
      Upload a video of your golf swing and get frame-by-frame feedback —
      swing phases, strengths, fixes and drills — in under a minute.
    </p>

    <div class="mt-10">
      <VideoUploader onselect={handleFileSelected} />
    </div>

    <ol class="mt-12 grid gap-6 text-left sm:grid-cols-3">
      {#each [["Upload", "Record your swing from face-on or down-the-line and upload the clip."], ["Mark the swing", "Scrub to the moment your swing starts so we analyze the right part."], ["Get coached", "AI breaks down every phase and tells you exactly what to work on."]] as [title, text], i}
        <li class="rounded-xl border border-pine-700 bg-pine-900/60 p-5">
          <span class="text-sm font-bold text-emerald-400">0{i + 1}</span>
          <h3 class="mt-1 font-semibold text-zinc-100">{title}</h3>
          <p class="mt-1.5 text-sm leading-relaxed text-zinc-400">{text}</p>
        </li>
      {/each}
    </ol>
  </section>
{:else}
  <section class="mx-auto max-w-3xl" in:fly={{ y: 16, duration: 400 }}>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-zinc-100">Mark your swing</h2>
        <p class="mt-1 text-sm text-zinc-400">
          Scrub to where your swing begins — the highlighted window is what gets analyzed.
        </p>
      </div>
      <button
        type="button"
        class="rounded-lg border border-pine-600 px-3 py-1.5 text-sm text-zinc-400 transition hover:border-zinc-500 hover:text-zinc-200"
        onclick={reset}
      >
        ↺ Different video
      </button>
    </div>

    <VideoPlayer {videoUrl} bind:currentTime bind:duration {clipDuration} />

    <div class="mt-6 flex flex-wrap items-center justify-between gap-4">
      <label class="flex items-center gap-3 text-sm text-zinc-400">
        Clip length
        <select
          bind:value={clipDuration}
          class="rounded-lg border border-pine-600 bg-pine-900 px-3 py-2 text-zinc-100 focus:border-emerald-500 focus:outline-none"
        >
          <option value={2}>2 seconds</option>
          <option value={3}>3 seconds</option>
          <option value={5}>5 seconds</option>
        </select>
      </label>

      <button
        type="button"
        class="rounded-xl bg-emerald-500 px-8 py-3 font-semibold text-pine-950 shadow-lg shadow-emerald-500/25 transition hover:bg-emerald-400 active:scale-[0.98]"
        onclick={handleAnalyze}
      >
        Analyze my swing →
      </button>
    </div>

    {#if errorMessage}
      <p class="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300" role="alert">
        {errorMessage}
      </p>
    {/if}
  </section>
{/if}
