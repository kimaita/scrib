<script>
  import { goto } from "$app/navigation";

  let { data } = $props();
  let videos = data.sermons;
</script>

<section class="container mx-auto px-4 py-8">
  <div class="flex align-baseline mt-6 mb-8">
    <h3 class="text-2xl sm:text-4xl font-extrabold flex-1">Youtube Videos</h3>
    <button class="btn btn-soft btn-info">Refresh</button>
  </div>

  <label class="input">
    <svg
      class="h-[1em] opacity-50"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
    >
      <g
        stroke-linejoin="round"
        stroke-linecap="round"
        stroke-width="2.5"
        fill="none"
        stroke="currentColor"
      >
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.3-4.3"></path>
      </g>
    </svg>
    <input type="search" required placeholder="Search" />
  </label>

  <div class="overflow-x-auto">
    <table class="table table-xs">
      <!-- head -->
      <thead>
        <tr>
          <th>Title</th>
          <th>Date</th>
          <th>Speaker</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {#each videos as vid (vid.id)}
          <tr onclick={() => goto(`/episode/${vid.id}`)}>
            <td>
              <!-- <div class="flex items-center gap-3">
                <div class="avatar">
                  <div class="mask mask-squircle h-12 w-12">
                    <img
                      src="https://img.daisyui.com/images/profile/demo/2@94.webp"
                      alt="Avatar Tailwind CSS Component"
                    />
                  </div>
                </div>
                <div>-->
              <div class="font-bold">{vid.title}</div>
              <!-- </div>
              </div> -->
            </td>
            <td>
              {vid.publishDate}
            </td>
            <td>{vid.speaker}</td>
            <td>
              <span
                class={[
                  "badge",
                  "badge-sm",
                  vid.state.toLocaleLowerCase() === "ready" && "badge-success",
                  vid.state.toLocaleLowerCase() === "unstarted" &&
                    "badge-neutral",
                  vid.state.toLocaleLowerCase() === "processing" &&
                    "badge-info",
                  vid.state.toLocaleLowerCase() === "failed" && "badge-error",
                ]}
              >
                {vid.state}
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
      <!-- foot -->
      <!-- <tfoot>
        <tr>
          <th></th>
          <th>Name</th>
          <th>Job</th>
          <th>Favorite Color</th>
          <th></th>
        </tr>
      </tfoot> -->
    </table>
  </div>
</section>

<style>
  /* Theme-aware transitions */
  tr {
    transition: background-color 0.2s ease;
  }
</style>
