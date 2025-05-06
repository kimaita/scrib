<script>
  import { page } from "$app/state";
  import { enhance } from "$app/forms";
  import { videos } from "$lib/stores/videoStore.js";

  let { data, form } = $props();
  let vid = data.sermons.find((v) => v.id === page.params.id) || {};
  let isSubmitting = $state(false);
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

  <form
    class="mx-auto max-w-lg"
    method="POST"
    use:enhance={() => {
      isSubmitting = true;
      // This runs *before* the form submits
      return async ({ result, update }) => {
        // This runs *after* the action completes on the server
        isSubmitting = false;

        // result contains the data returned from the form action
        // update() function handles default navigation/updates based on result
        // If the action returns a redirect, enhance handles it automatically.
        // If the action returns { status: 'success' }, form store is updated.
        // No need for manual navigation here if action redirects.
        await update();
      };
    }}
  >
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
            disabled={isSubmitting}
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
            value={vid.startAt}
            required
            disabled={isSubmitting}
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
            value={vid.endAt}
            required
            disabled={isSubmitting}
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
            disabled={isSubmitting}
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
            disabled={isSubmitting}
          />
        </fieldset>
        <fieldset class="fieldset col-span-2">
          <legend class="fieldset-legend sm:text-sm">Description</legend>
          <textarea
            class="textarea h-24 w-full"
            placeholder="Bio"
            disabled={isSubmitting}
          ></textarea>
          <div class="fieldset-label">
            Leave blank for an AI generated description
          </div>
        </fieldset>
      </div>

      <button
        type="submit"
        class="btn btn-accent btn-block mt-6"
        disabled={isSubmitting}
        >{isSubmitting ? "Submitting..." : "Submit"}</button
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
