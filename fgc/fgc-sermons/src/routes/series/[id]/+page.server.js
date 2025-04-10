import { error } from "@sveltejs/kit";
import { API_BASE_URL } from "$env/static/private";

export async function load({ params, fetch }) {
  try {
    const res = await fetch(`${API_BASE_URL}/playlists/${params.id}`);
    if (!res.ok) throw new Error("Playlist not found");

    const series = await res.json();
    series.videos.forEach((sermon) => {
      sermon.downloadlink = `${API_BASE_URL}/videos/${sermon.id}/download`;
    });

    return {
      playlist: series,
    };
  } catch {
    error(404, "Playlist not found");
  }
}
