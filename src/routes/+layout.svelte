<script>
  import '../app.css'
	let { children } = $props();
</script>

<div class="layout" data-name="c">
	{@render children()}
</div>
