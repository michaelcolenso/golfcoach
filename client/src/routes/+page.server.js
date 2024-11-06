import { error } from '@sveltejs/kit';
/** @type {import('./$types').PageServerLoad} */

export async function handleUpload() {
    if (!videoFile) {
      alert('Please select a file to upload.');
      return;
    }
  
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('start_time', currentTime.toString());
  
    try {
      isLoading.set(true);
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const result = await response.json();
        const frameFeedback = result.feedback || {};
        const selectedFrames = result.selected_frames || [];
        const frameCount = result.frame_count || 0;
  
  
        goto('/feedback', {
  
          state: {
            frameFeedback,
            selectedFrames,
            frameCount,
          },
        });
      } else {
        throw new Error(`Upload failed: ${response.status}`);
      }
    } catch (error) {
      errorMessage.set(error.message);
    } finally {
      isLoading.set(false);
    }
  }  

