<script>
	import { onMount } from 'svelte';
  
	let videoFile;
	let videoUrl = '';
	let startTime = 0;
	let videoDuration = 0;
	let videoPlayer;
    let frameFeedback = null;
    let overallFeedback = null;
    let selectedFrames = [];
    let frameCount = 0;
    let errorMessage = '';
  
	onMount(() => {
	  // This function will be executed when the component is mounted
	});
  
	function onFileChange(event) {
	  const files = event.target.files;
	  if (files.length > 0) {
		videoFile = files[0];
		videoUrl = URL.createObjectURL(videoFile);
		// If you have an onVideoSelect callback, you can call it here
	  }
	}
  
	function onLoadedMetadata() {
	  videoDuration = videoPlayer.duration;
	}
  
	function handleSliderChange(event) {
	  const newStartTime = parseFloat(event.target.value);
	  startTime = newStartTime;
	  videoPlayer.currentTime = newStartTime;
	}
  
    async function handleSubmit(event) {
        event.preventDefault();

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

  </script>
  
  <form on:submit={handleSubmit}>
	<div id="upload-form" class="mb-4">
	  <label for="video-file" class="block text-gray-700 text-sm font-bold mb-2">
		Choose a video
	  </label>
	  <input type="file" id="video-file" name="video" accept="video/*" required 
			 class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
			 on:change={onFileChange} />
	</div>
	<div class="flex items-center justify-between">
	  <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
		Upload Video
	  </button>
	</div>
  </form>
  
  <!-- svelte-ignore a11y-media-has-caption -->
  <video bind:this={videoPlayer} src={videoUrl} on:loadedmetadata={onLoadedMetadata} controls></video>
  
  {#if videoDuration > 0}
	<div>
	  <label for="start-time-slider">Start Time (seconds):</label>
	  <input type="range" id="start-time-slider" min="0" max={videoDuration - 3} step="0.01"
			 bind:value={startTime} on:input={handleSliderChange} 
			 class="w-full h-2 bg-blue-400" />
	  <div>Selected Start Time: {startTime.toFixed(2)}s</div>
	</div>
  {/if}

  {#if errorMessage}
  <p class="error">{errorMessage}</p>
{/if}

{#if overallFeedback}
  <div class="feedback">
    <h3>Overall Feedback</h3>
    <p>{overallFeedback}</p> <!-- Assuming 'message' holds the overall feedback -->
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
