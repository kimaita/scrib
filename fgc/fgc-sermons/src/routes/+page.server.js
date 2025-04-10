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

    const sermons = await videosRes.json();
    const series = await playlistsRes.json();
    // sermons.data.map((sermon)=>{
    //     sermon.
    // });
    return {
      recentSermons: sermons.data,
      playlists: series.data,
    };
  } catch {
    return {
      status: 500,
      error: "Failed to load data",
    };
  }
}
