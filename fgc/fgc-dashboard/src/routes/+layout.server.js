import { API_BASE_URL } from "$env/static/private";
// import { error } from "@sveltejs/kit";

export async function load({ fetch }) {
  try {
    const videosRes = await fetch(`${API_BASE_URL}/videos?pageSize=25`);
    console.log("videosRes", videosRes);
    if (!videosRes.ok) {
      console.error("Error fetching videos:", videosRes.statusText);
      //   return {};
    }

    const sermon_resp = await videosRes.json();
    console.log("sermon_resp", sermon_resp);

    const sermons = sermon_resp.data.map((sermon) => {
      return {
        ...sermon,
        publishDate: new Date(sermon.publishDate).toDateString(),
      };
    });

    return { sermons };
  } catch (error) {
    console.error("Error fetching videos:", error);
    return {};
  }
}
