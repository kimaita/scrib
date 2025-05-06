import { API_BASE_URL } from "$env/static/private";

async function checkStatusesAndNotify(videoIdsToCheck) {
  const videosRes = await Promise.all(
    videoIdsToCheck.map((id) => {
      fetch(`${API_BASE_URL}/videos/${id}`);
    })
  );

  console.log(videosRes);

  if (!videosRes.ok) {
    const err = await videosRes;
    console.error("Error fetching videos:", err);
  }

  const sermon_resp = videosRes;
  return sermon_resp;
}

/** @type {import('./$types').RequestHandler} */
export async function GET({ request }) {
  const url = new URL(request.url);
  const idsParam = url.searchParams.get("ids");
  const initialVideoIds = idsParam ? idsParam.split(",") : [];
  let videos;
  if (initialVideoIds.length > 0) {
    videos = await checkStatusesAndNotify(initialVideoIds);
  }
  return new Response(videos);
}
