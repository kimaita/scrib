<script>
  import "../app.css";
  let { children } = $props();
</script>

<div class="pb-8">
  <nav class="navbar bg-base-100 shadow-sm">
    <div class="flex-none">
      <img src="/fgcn-logo.png" class="h-8 sm:h-10" alt="FGCN Logo" />
    </div>
    <div class="flex-1 ms-3">
      <a class="text-2xl font-bold sm:text-3xl" href="/">FGCN</a>
    </div>
    <div class="flex-none me-3">
      <!-- <input type="text" placeholder="Search" class="input w-auto" /> -->
    </div>
  </nav>
  <div class="mx-auto max-w-4xl px-4 lg:max-w-6xl">
    {@render children()}
  </div>
</div>
