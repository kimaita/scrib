<script>
  import SpotifyBadgeDark from "$lib/icons/spotify-badge-dark.svg";
  import YouTubeBadgeDark from "$lib/icons/yt_logo_rgb_dark.png";
  import YouTubeBadgeLight from "$lib/icons/yt_logo_rgb_light.png";
  import DownloadOutline from "flowbite-svelte-icons/DownloadOutline.svelte";

  let { data } = $props();
  import Sermon from "$lib/Sermon.svelte";
  import YtImage from "$lib/YTImage.svelte";

  let recentSermons = data.recentSermons ?? [];
  let playlists = data.playlists ?? [];
</script>

<section>
  <h2 class="my-6 text-2xl">Recent Sermons</h2>
  <ul class="grid grid-cols-1 gap-8 md:gap-12 px-2 sm:grid-cols-2 md:px-4 mt-2">
    {#each recentSermons.slice(0, 6) as sermon}
      <Sermon {sermon} />
    {/each}
  </ul>
</section>

<section>
  <h2 class="mt-10 mb-6 font-funnel text-4xl">Series</h2>
  <div
    class="grid grid-cols-2 gap-8 px-2 sm:px-4 md:grid-cols-3 lg:grid-cols-4"
  >
    {#each playlists as playlist}
      <div>
        <a href={`/series/${playlist.id}`}>
          <img
            src={`https://i.ytimg.com/vi/${playlist.videos[0]?.id}/mqdefault.jpg`}
            alt={playlist.title}
            class="rounded-lg shadow-md dark:shadow-gray-800 mb-2"
          />
        </a>
        <!-- figClass="relative transition-all duration-300 hover:shadow-lg hover:shadow-gray-700"
              captionClass="absolute bottom-2 end-2 me-1 text-sm text-base-content"
              caption={`${playlist.videoCount} Items`} -->
        <h4
          class="capitalize text-lg text-base-content px-2 font-bold truncate"
        >
          {playlist.title.toLowerCase()}
        </h4>
        <p class="text-base-content/60 px-2 font-semibold text-xs md:text-sm">
          {new Date(playlist.publishDate).getFullYear()}
        </p>
      </div>
    {/each}
  </div>
</section>
<!-- <div class="divider mb-6 sm:text-lg">Load More</div> -->

<section class="text-center mt-12">
  <span
    class="text-base-content/70 sm:text-md mt-8 text-sm font-semibold uppercase"
  >
    Our Channels
  </span>
  <div class="my-6 flex justify-center gap-8 sm:gap-12">
    <a href="https://open.spotify.com/show/6WpkLb4bUZv1jOgltGsYh3">
      <img
        src={SpotifyBadgeDark}
        alt="Link to Spotify podcast"
        class="w-36 sm:w-48"
      />
    </a>
    <a href="https://www.youtube.com/@FOUNTAINGATECHURCH">
      <YtImage
        lightSrc={YouTubeBadgeLight}
        darkSrc={YouTubeBadgeLight}
        alt="Link to Youtube channel"
        classes="w-36 sm:w-48"
      />
    </a>
  </div>
</section>

<!-- TODO: Add a Calendar for date searching -->
