import { API_BASE_URL } from "$env/static/private";
import { PROCESSING_API_URL } from "$env/static/private";
import { fail } from "@sveltejs/kit";

export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();

    const update_data = {
      video_id: data.get("video_id"),
      start: data.get("start_time"),
      end: data.get("end_time"),
      title: data.get("title"),
      speaker: data.get("speaker"),
      description: data.get("description"),
    };
    const resp = await fetch(`${API_BASE_URL}/videos/${update_data.video_id}`, {
      method: "PATCH",
      body: JSON.stringify(update_data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (resp.status === 200) {
      console.log("Record updated successfully");
    }
    const processing = await fetch(`${PROCESSING_API_URL}/episode`, {
      method: "POST",
      body: JSON.stringify({
        id: update_data.video_id,
        start: update_data.start,
        end: update_data.end,
        metadata: {
          title: update_data.title,
          artist: update_data.speaker,
        },
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (processing.status === 200) {
      console.log("Processing started successfully");
      const message = await processing.json();
      return message;
    } else {
      console.log("Processing failed");
      return fail(500, {
        error: "The server encountered an error while processing your request.",
      });
    }
  },
};
