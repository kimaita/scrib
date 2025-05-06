import { writable } from "svelte/store";

export const videos = writable([]);

/**
 * Updates video details client-side
 *
 * @param {string} videoId
 * @param {Partial<Video>} updates
 */
export function updateVideoInStore(videoId, updates) {
  videos.update((currentVideos) =>
    currentVideos.map((video) =>
      video.id === videoId ? { ...video, ...updates } : video
    )
  );
}

/**
 * Sets the initial list of videos
 *
 * @param {Video[]} initialVideos
 */
export function setInitialVideos(initialVideos) {
  videos.set(initialVideos);
}
