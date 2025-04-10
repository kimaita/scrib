import { error } from "@sveltejs/kit";
import { PUBLIC_API_BASE_URL } from "$env/static/public";

export async function load({ params, fetch }) {
  try {
    const res = await fetch(`${PUBLIC_API_BASE_URL}/playlists/${params.id}`);
    if (!res.ok) throw new Error("Playlist not found");

    return {
      playlist: await res.json(),
    };
  } catch {
    error(404, "Playlist not found");
  }
}
