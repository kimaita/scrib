<script>
  import DownloadOutline from "flowbite-svelte-icons/DownloadOutline.svelte";
  import { error } from "@sveltejs/kit";

  let s = $props();
  const sermon = s.sermon;
</script>

<li>
  <div class="flex items-center space-x-3 rtl:space-x-reverse">
    <img
      class="size-16 md:size-18 rounded"
      src={`https://i.ytimg.com/vi/${sermon.id}/default.jpg`}
      alt={sermon.title}
    />

    <div class="max-w-3/4 flex-1">
      <h5
        class="text-md leading-none sm:text-lg font-semibold text-base-content/95 capitalize"
      >
        {sermon.title.toLowerCase()}
      </h5>
      <p class="text-base-content/60 truncate text-xs sm:text-sm">
        {#if sermon.speaker}
          {`${sermon.speaker} • `}
        {/if}
        {new Date(sermon.publishDate).toDateString()}
      </p>
    </div>
    {#if sermon?.state?.toLowerCase() === "ready"}
      <div class="">
        <a href={sermon.downloadlink}>
          <DownloadOutline class="size-6 hover:shadow" />
        </a>
        <!-- <ShareNodesOutline class="size-6" /> -->
      </div>
    {/if}
  </div>
</li>
