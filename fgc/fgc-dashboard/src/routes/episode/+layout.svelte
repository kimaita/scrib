<script>
  /** @type {import('./$types').LayoutProps} */
  let { data, children } = $props();
</script>

<div class="mb-6 mt-4">
  <a
    href="/"
    class="inline-flex items-center text-blue-600 hover:text-blue-800"
    onclick={() => history.back()}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-8 w-8 mr-1"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        fill-rule="evenodd"
        d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
        clip-rule="evenodd"
      />
    </svg>
    Back to Videos
  </a>
</div>
{@render children()}
