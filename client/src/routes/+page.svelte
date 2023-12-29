<script>
  import { onMount } from 'svelte';
  import VideoUploader from '$lib/VideoUploader.svelte';
  import VideoPlayer from '$lib/VideoPlayer.svelte';
  import VideoSlider from '../lib/VideoSlider.svelte';

  
  let startTime = 0;
  let videoDuration = 0;
  let videoFile;
  let videoUrl = '';
  let frameFeedback = null;
  let overallFeedback = null;
  let selectedFrames = [];
  let frameCount = 0;
  let errorMessage = '';

  onMount(() => {
    // This function will be executed when the component is mounted
  });

  function handleFileSelected(event) {
    videoFile = event.detail.file;
    videoUrl = URL.createObjectURL(videoFile);
  }

  async function handleUpload() {
    // Check if a file is selected
    if (!videoFile) {
      alert('Please select a file to upload.');
      return;
    }

    // Create FormData and append the file
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('start_time', startTime.toString()); // Convert startTime to a string

    try {
      // Send the request to the Flask backend
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log(result);
        frameFeedback = result.feedback[0];
        overallFeedback = result.feedback[1];
        selectedFrames = result.selected_frames;
        frameCount = result.frame_count;
      } else {
        throw new Error(`Upload failed: ${response.status}`);
      }
    } catch (error) {
      errorMessage = error.message;
    }
  }

  function setDuration(duration) {
    videoDuration = duration;
  }
  
  function handleSliderChange(event) {
    startTime = parseFloat(event.target.value);
  }
</script>

<div class="container mx-auto p-8 space-y-8">
  <VideoUploader on:fileselected={handleFileSelected} on:upload={handleUpload} />
  
<VideoPlayer {videoUrl} on:durationchange={event => setDuration(event.detail.duration)} />
  
  {#if videoDuration > 0}
    <div>
     <VideoSlider {videoDuration} bind:startTime />
    </div>
  {/if}
  
  {#if errorMessage}
    <p class="error">{errorMessage}</p>
  {/if}
  
  {#if overallFeedback}
    <div class="feedback">
      <h3>Overall Feedback</h3>
      <p>{overallFeedback}</p>
    </div>
  {/if}
  
  {#if selectedFrames.length > 0}
    <div class="frames">
      <h3>Selected Frames ({frameCount})</h3>
      {#each selectedFrames as frame, index (frame)}
        <div class="frame">
          <img src={`data:image/jpeg;base64,${frame}`} alt={`Frame ${index + 1}`} />
          {#if frameFeedback[`image_${index + 1}`]}
            <p class="caption">{frameFeedback[`image_${index + 1}`]}</p>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
