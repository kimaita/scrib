import { PUBLIC_API_BASE_URL } from "$env/static/public";
import { error } from "@sveltejs/kit";

export async function load({ fetch }) {
  const apiBaseUrl = PUBLIC_API_BASE_URL;
  try {
    const [videosRes, playlistsRes] = await Promise.all([
      fetch(`${apiBaseUrl}/videos?pageSize=2`),
      fetch(`${apiBaseUrl}/playlists?pageSize=6`),
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
  } catch (e) {
    console.log(e);
    error(404);
    return {
      status: 500,
      error: "Failed to load data",
    };
  }
}
