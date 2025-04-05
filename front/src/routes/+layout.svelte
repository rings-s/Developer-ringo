<script>
	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import '../app.css';
  
	let { children } = $props();
  </script>
  
  <div class="min-h-screen flex flex-col">
	<Header />
	<main class="flex-1">
	  {@render children()}
	</main>
	<Footer />
  </div>