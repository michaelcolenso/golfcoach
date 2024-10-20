<script>
    import { onMount } from 'svelte';
    import { resultsStore } from '$lib/stores/resultsStore';
    import { goto } from '$app/navigation';
  
    let results;
    let isLoading = true;
    let error = null;
  
    onMount(() => {
      const unsubscribe = resultsStore.subscribe(value => {
        if (value) {
          results = value;
          isLoading = false;
          console.log('Results:', results);
        } else {
          goto('/');
        }
      });
  
      return unsubscribe;
    });
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Golf Swing Analysis Results</h1>
  
    {#if isLoading}
        <p>Loading results...</p>
    {:else if error}
        <p class="text-red-500">Error: {error}</p>
    {:else if results}
        <div class="mb-8">
            <h2 class="text-xl font-semibold mb-4">Swing Analysis</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {#each results.selected_frames as frame, index}
                    <div class="border p-4 rounded-lg flex flex-col md:flex-row items-center">
                        <img src={`data:image/jpeg;base64,${frame}`} alt="Swing frame {index + 1}" class="w-full md:w-1/2 mb-4 md:mb-0 md:mr-4" />
                        <div>
                            <h3 class="text-lg font-medium mb-2">Frame {index + 1}</h3>
                            <p>{results.feedback.swing_analysis?.[`image_${index + 1}`] || 'No feedback available for this frame.'}</p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        {#if results.feedback?.recommendations && results.feedback.recommendations.length > 0}
            <div class="mb-8">
                <h2 class="text-xl font-semibold mb-4">Recommendations</h2>
                <ul class="list-disc pl-5">
                    {#each results.feedback.recommendations as rec}
                        <li class="mb-2">{rec}</li>
                    {/each}
                </ul>
            </div>
        {/if}

        {#if results.feedback?.overall_feedback}
            <div class="mb-8">
                <h2 class="text-xl font-semibold mb-4">Overall Feedback</h2>
                <p>{results.feedback.overall_feedback}</p>
            </div>
        {/if}
    {:else}
        <p>No results available. Please upload a video first.</p>
    {/if}
</div>