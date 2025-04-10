import { error } from "@sveltejs/kit";
import { PUBLIC_API_BASE_URL } from "$env/static/public";

export async function load({ params, fetch }) {
  try {
    const res = await fetch(`${PUBLIC_API_BASE_URL}/playlists/${params.id}`);
    if (!res.ok) throw new Error("Playlist not found");

    const series = await res.json();
    series.videos.forEach((sermon) => {
      sermon.downloadlink = `${PUBLIC_API_BASE_URL}/videos/${sermon.id}/download`;
    });

    return {
      playlist: series,
    };
  } catch {
    error(404, "Playlist not found");
  }
}
