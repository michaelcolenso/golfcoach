<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import VideoUploader from '$lib/VideoUploader.svelte';
  import VideoPlayer from '$lib/VideoPlayer.svelte';
  import UploadButton from '$lib/UploadButton.svelte';
  import { fly } from 'svelte/transition';
  import { writable } from 'svelte/store';
  import { resultsStore } from '$lib/stores/resultsStore';



  let startTime;
  let maxDuration = '';
  let currentTime = 0;
  let videoFile;
  let videoUrl = '';
  let isLoading = writable(false);
  let errorMessage = writable('');

  
  onMount(() => {
    // This function will be executed when the component is mounted
  });

  function handleFileSelected(event) {
    videoFile = event.detail.file;
    videoUrl = URL.createObjectURL(videoFile);
  }

  function setDuration(duration) {
    maxDuration = duration;
  }

  function handleTimeChange(event) {
    currentTime = event.detail; 
  }

  async function handleUpload() {
    isLoading.set(true);
    errorMessage.set('');

    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('start_time', currentTime.toString());
      formData.append('duration', '3'); // You might want to make this configurable

      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      
      // Store the results
      resultsStore.set(result);
      
      // Navigate to the results page
      goto('/results');
    } catch (error) {
      console.error('Error uploading video:', error);
      errorMessage.set('Failed to upload video. Please try again.');
    } finally {
      isLoading.set(false);
    }
  }
</script>

<div class="hero bg-base-200">
  <div class="hero-content text-center">
    <div class="">
      <h1 class="text-5xl font-bold">Golfcoach</h1>
      {#if !videoUrl}
      <VideoUploader on:fileselected={handleFileSelected} on:upload={handleUpload} />
    {/if}
    {#if $isLoading}
      <div class="flex justify-center loading">
        Loading...
      </div>
    {:else if videoUrl}
      <div class="flex justify-center">
        <div class="">
          <div class="videoplayer" in:fly={{x: 0, y: 0, duration: 1000}} out:fly={{x: -200, y: 0, duration: 500}}>
            <h3 class="text-lg font-semibold">Video</h3>
            <p class="text-xs">{currentTime} / {maxDuration}</p>
            <VideoPlayer {videoUrl} bind:currentTime bind:maxDuration />
          </div>
        </div>
      </div>
      <UploadButton videoFile={videoFile} on:upload={handleUpload} />
    {/if}
    {#if $errorMessage}
      <p class="text-red-500">{$errorMessage}</p>
    {/if}
      <button class="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>

<style>
  .container {
    padding: 1rem;
  }
  .loading {
    font-size: 1.5rem;
  }
</style>