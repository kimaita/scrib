<script>
	import { page } from '$app/state';
</script>

<h1 class="text-error">{page.status}: {page.error.message}</h1>
