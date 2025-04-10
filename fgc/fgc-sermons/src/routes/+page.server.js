import { PUBLIC_API_BASE_URL } from "$env/static/public";
// import { error } from "@sveltejs/kit";

export async function load({ fetch }) {
  try {
    const [videosRes, playlistsRes] = await Promise.all([
      fetch(`${PUBLIC_API_BASE_URL}/videos?pageSize=2`),
      fetch(`${PUBLIC_API_BASE_URL}/playlists?pageSize=6`),
    ]);

    if (!videosRes.ok || !playlistsRes.ok)
      throw new Error("Failed to fetch data");

    const sermon_resp = await videosRes.json();

    const sermons = sermon_resp.data.map((sermon) => {
      return {
        ...sermon,
        downloadlink: `${PUBLIC_API_BASE_URL}/videos/${sermon.id}/download`,
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
