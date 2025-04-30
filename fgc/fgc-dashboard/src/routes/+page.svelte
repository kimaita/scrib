<script>
  import { goto } from "$app/navigation";

  let { data } = $props();
  let videos = data.sermons;
</script>

<!-- <section>
  <h3>Recent videos</h3>
</section>
<input type="search" name="" id="" /> -->

<section class="container mx-auto px-4 py-8">
  <h3 class="text-2xl sm:text-4xl text-center font-extrabold mt-8 mb-12">
    Youtube Videos
  </h3>

  <div class="overflow-x-auto">
    <table class="table">
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
