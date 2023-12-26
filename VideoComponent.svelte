<script>
	import { onMount } from 'svelte';
	import { uploadVideo } from '@/app/actions';
  
	let videoFile;
	let videoUrl = '';
	let startTime = 0;
	let videoDuration = 0;
	let videoPlayer;
  
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
	  // Implement the logic to upload the video
	  // This might involve calling the 'uploadVideo' function
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
  