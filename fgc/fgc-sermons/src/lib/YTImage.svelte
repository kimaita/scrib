<script>
  export let lightSrc;
  export let darkSrc;
  export let alt = "";
  export let classes = "";
  export let lazy = true;
</script>

<picture>
  <source srcset={darkSrc} media="(prefers-color-scheme: dark)" />
  <source srcset={darkSrc} class="theme-dark" />
  <img
    src={lightSrc}
    {alt}
    class={`${classes} dark:hidden`}
    loading={lazy ? "lazy" : "eager"}
    decoding="async"
  />
  <img
    src={darkSrc}
    {alt}
    class={`${classes} hidden dark:block`}
    loading={lazy ? "lazy" : "eager"}
    decoding="async"
  />
</picture>
