import { API_BASE_URL } from "$env/static/private";
// import { error } from "@sveltejs/kit";

export async function load({ fetch }) {
  try {
    const [videosRes, playlistsRes] = await Promise.all([
      fetch(`${API_BASE_URL}/videos?pageSize=2`),
      fetch(`${API_BASE_URL}/playlists?pageSize=6`),
    ]);

    if (!videosRes.ok || !playlistsRes.ok)
      throw new Error("Failed to fetch data");

    const sermon_resp = await videosRes.json();

    const sermons = sermon_resp.data.map((sermon) => {
      return {
        ...sermon,
        downloadlink: `${API_BASE_URL}/videos/${sermon.id}/download`,
      };
    });

    const series = await playlistsRes.json();

    return {
      recentSermons: sermons,
      playlists: series.data,
    };
  } catch {
    return {
      status: 500,
      error: "Failed to load data",
    };
  }
}
