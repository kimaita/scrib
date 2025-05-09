import { API_BASE_URL } from "$env/static/private";
import { PROCESSING_API_URL } from "$env/static/private";
import { ACCESS_TOKEN } from "$env/static/private";
import { fail, redirect } from "@sveltejs/kit";
import { updateVideoInStore } from "$lib/stores/videoStore.js";

async function updateRecord(data, state) {
  const update_data = {
    start: data.get("start_time"),
    end: data.get("end_time"),
    title: data.get("title"),
    speaker: data.get("speaker"),
    ...(state && { state }),
    // playlistId
    ...(data.get("description") && { description: data.get("description") }),
  };
  const resp = await fetch(`${API_BASE_URL}/videos/${data.get("video_id")}`, {
    method: "PATCH",
    body: JSON.stringify(update_data),
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (resp.ok) {
    console.log("Record updated successfully");
  } else {
    console.error("Failed to update DB record");
  }
  return { success: resp.ok, body: await resp.json() };
}

/**
 *
 * @param {*} data
 * @returns
 */
async function submitForProcessing(data) {
  const processing = await fetch(`${PROCESSING_API_URL}`, {
    method: "POST",
    body: JSON.stringify({
      id: data.get("video_id"),
      start: data.get("start_time"),
      end: data.get("end_time"),
      metadata: {
        title: data.get("title"),
        artist: data.get("speaker"),
        album: data.get("series"),
        description: data.get("description"),
      },
    }),
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${ACCESS_TOKEN}`,
    },
  });
  if (processing.ok) {
    console.log("Processing started successfully");
  } else {
    console.log("Processing failed");
  }

  return { success: processing.ok, body: await processing.json() };
}

export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const videoId = data.get("video_id");
    try {
      const submitSuccess = await submitForProcessing(data);
      const updateSuccess = await updateRecord(
        data,
        submitSuccess.success ? "ONGOING" : undefined
      );

      if (!(submitSuccess.success && updateSuccess.success)) {
        return fail(500, {
          error: "An error occured submitting your request.",
          detail: updateSuccess.body || submitSuccess.body,
        });
      }
      try {
        updateVideoInStore(videoId, { status: "ongoing" });
        console.log(
          `Updated video ${videoId} status to 'processing' (server-side)`
        );
      } catch (storeError) {
        console.error("Failed to update store:", storeError);
      }
    } catch (err) {
      console.error(`Error in form action for video ${videoId}:`, err);
      return fail(500, {
        message: "An unexpected error occurred.",
        detail: err,
      });
    }
    redirect(303, "/");
  },
};
