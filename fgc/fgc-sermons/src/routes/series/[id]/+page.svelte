<script>
  import Sermon from "$lib/Sermon.svelte";
  import { formatDateString } from "$lib/format.js";
  import Youtube from "$lib/icons/youtube.svg";
  let { data } = $props();
  const series = data.playlist;
  series.thumbnail = `https://i.ytimg.com/vi/${series.videos[0].id}/mqdefault.jpg`;
  series.finish = series.videos[0].publishDate;
  series.start = series.videos[series.videos.length - 1].publishDate;
  //   const speakers = new Set(Array.from(series.videos, (v) => v?.speaker));
  //   console.log(speakers);
</script>

<div class="">
  <div class="mt-4 flex flex-col sm:flex-row sm:space-x-3">
    <div class="stack stack-top sm:stack-start flex-none">
      <img
        src={series.thumbnail}
        class="rounded-lg shadow-lg sm:shadow-xl"
        alt={series.title}
      />
      <img
        src={`https://i.ytimg.com/vi/${series.videos[1].id}/mqdefault.jpg`}
        class="rounded-lg"
        alt=""
      />
      <img
        src={`https://i.ytimg.com/vi/${series.videos[series.videos.length - 1].id}/mqdefault.jpg`}
        class="rounded-lg"
        alt=""
      />
    </div>
    <div class="flex-col content-center mt-6 px-2">
      <h1 class="uppercase text-xl font-semibold sm:text-2xl">
        {series.title}
      </h1>
      <p class="mt-1 text-sm text-base-content/60">
        {series.videos.length} Sermons •
        {formatDateString(series.start)} - {formatDateString(series.finish)}
      </p>

      <a
        class="flex gap-2 items-center mt-2"
        href={`https://www.youtube.com/playlist?list=${series.id}`}
      >
        <svg
          fill="#FF0000"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          class="size-[2em]"
        >
          <path
            d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"
          />
        </svg>
        <p class="text-sm font-light text-base-content/50">View on YouTube</p>
      </a>

      <!-- <button class="btn btn-sm sm:btn btn-soft mt-3 sm:mt-5">
			Download
			<DownloadOutline />
		</button> -->
    </div>
  </div>

  <div class="divider divider-start mt-10 sm:mt-14 mb-6 text-2xl font-semibold">
    Sermons
  </div>

  <ul class="grid grid-cols-1 gap-4 px-2 md:grid-cols-2 md:px-4">
    {#each series.videos as sermon}
      <Sermon {sermon} />
    {/each}
  </ul>
</div>
