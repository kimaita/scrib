<script>
  import { page } from "$app/state";
  let { data, form } = $props();

  let vid = data.sermons.find((v) => v.id === page.params.id) || {};
  $inspect(vid);
</script>

<div class="px-4 sm:px-8 grid gap-4 items-center md:grid-cols-2 grid-cols-1">
  <iframe
    class="w-full h-64 sm:h-96 rounded-lg"
    src={`https://www.youtube.com/embed/${vid.id}`}
    title={vid.title}
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
  ></iframe>

  <form class="mx-auto max-w-lg" method="POST">
    <input type="hidden" name="video_id" value={vid.id} />
    <div class="flex flex-col items-center">
      <div class="grid w-full gap-3 sm:grid-cols-2">
        <fieldset class="fieldset col-span-2">
          <legend class="fieldset-legend sm:text-sm">Title</legend>
          <input
            class="input w-full"
            type="text"
            id="text-title"
            name="title"
            value={vid.title}
            required
          />
        </fieldset>

        <fieldset class="fieldset w-full">
          <legend class="fieldset-legend sm:text-sm">Start time:</legend>
          <input
            class="input"
            type="text"
            id="text-start"
            name="start_time"
            placeholder="HH:MM:SS"
            required
          />
        </fieldset>

        <fieldset class="fieldset w-full">
          <legend class="fieldset-legend sm:text-sm">End time:</legend>
          <input
            class="input"
            type="text"
            id="text-end"
            name="end_time"
            placeholder="HH:MM:SS"
            required
          />
        </fieldset>
        <fieldset class="fieldset w-full">
          <legend class="fieldset-legend sm:text-sm">Speaker</legend>
          <input
            class="input"
            type="text"
            id="text-speaker"
            name="speaker"
            value={vid.speaker}
          />
        </fieldset>
        <fieldset class="fieldset w-full">
          <legend class="fieldset-legend sm:text-sm">Series</legend>
          <input
            class="input"
            type="text"
            id="text-series"
            name="series"
            value={vid.playlist}
          />
        </fieldset>
        <fieldset class="fieldset col-span-2">
          <legend class="fieldset-legend sm:text-sm">Description</legend>
          <textarea class="textarea h-24 w-full" placeholder="Bio"></textarea>
          <div class="fieldset-label">
            Leave blank for an AI generated description
          </div>
        </fieldset>
      </div>

      <button type="submit" class="btn btn-accent btn-block mt-6">Submit</button
      >
    </div>
  </form>
</div>

{#if form?.error}
  <div class="toast">
    <div class="alert alert-error">
      <span>{form.error}</span>
    </div>
  </div>
{:else if form?.message}
  <div class="toast">
    <div class="alert alert-info">
      <span>{form.message}</span>
    </div>
  </div>
{/if}
