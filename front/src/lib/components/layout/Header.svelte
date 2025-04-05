<script>
  import { onMount, tick } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  // Use the navigation links from the comment
  const navLinks = [
    { href: '/about', label: 'About' },
    { href: '/services', label: 'Services' },
    { href: '/projects', label: 'Projects' },
    { href: '/blog', label: 'Blog' },
    { href: '/contact', label: 'Contact' }
  ];
  
  // Mobile navigation state
  let isOpen = false;
  
  // Toggle mobile menu
  function toggleNav() {
    isOpen = !isOpen;
  }
  
  // Close mobile menu
  function closeNav() {
    isOpen = false;
  }
  
  // Current page for active state
  let currentPath = '';
  
  // On mount, get the current path
  onMount(() => {
    currentPath = window.location.pathname;
    
    // Update currentPath when the route changes
    const handleRouteChange = () => {
      currentPath = window.location.pathname;
    };
    
    window.addEventListener('popstate', handleRouteChange);
    
    // Add click event listener to close menu when clicking outside
    const handleClickOutside = (event) => {
      const navElement = document.getElementById('mobile-menu');
      const navToggle = document.getElementById('nav-toggle');
      
      if (isOpen && navElement && !navElement.contains(event.target) && !navToggle.contains(event.target)) {
        closeNav();
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
      document.removeEventListener('click', handleClickOutside);
    };
  });
  
  // Check if a link is active
  function isActive(href) {
    if (href === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(href);
  }
  
  // Handle link clicks in mobile menu
  async function handleLinkClick() {
    await tick();
    closeNav();
  }
</script>

<header class="border-b border-surface-300-600-token">
  <div class="container-xl mx-auto px-4">
    <nav class="py-3">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <a href="/" class="flex-none" on:click|preventDefault={handleLinkClick}>
          <span class="font-bold text-2xl text-primary-500">Logo</span>
        </a>
        
        <!-- Desktop Navigation -->
        <div class="hidden lg:flex items-center gap-8">
          <ul class="flex gap-6">
            {#each navLinks as link}
              <li>
                <a 
                  href={link.href} 
                  class="nav-link py-2 px-1 font-medium border-b-2 border-transparent transition-colors duration-200 
                         {isActive(link.href) ? 'text-primary-500 border-primary-500' : 'text-surface-900 dark:text-surface-50 hover:text-primary-500 hover:border-primary-300'}"
                >
                  {link.label}
                </a>
              </li>
            {/each}
          </ul>
          
          <!-- CTA Buttons -->
          <div class="flex items-center gap-4">
            <a href="/signin" class="btn btn-sm variant-ghost">Sign In</a>
            <a href="/signup" class="btn btn-sm variant-filled">Sign Up</a>
          </div>
        </div>
        
        <!-- Mobile Menu Button -->
        <button 
          id="nav-toggle"
          type="button" 
          class="lg:hidden btn-icon variant-ghost p-2"
          aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isOpen}
          aria-controls="mobile-menu"
          on:click={toggleNav}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d={isOpen 
                ? "M6 18L18 6M6 6l12 12" 
                : "M4 6h16M4 12h16M4 18h16"} 
            />
          </svg>
        </button>
      </div>
    </nav>
  </div>
  
  <!-- Mobile Navigation Menu -->
  {#if isOpen}
    <div 
      id="mobile-menu"
      class="lg:hidden border-t border-surface-300-600-token"
      transition:fly={{ duration: 200, y: -10 }}
    >
      <div class="container-xl mx-auto px-4 py-4">
        <ul class="flex flex-col gap-2 mb-6">
          {#each navLinks as link}
            <li>
              <a 
                href={link.href} 
                class="block py-2.5 px-3 rounded-token font-medium transition-colors
                       {isActive(link.href) 
                         ? 'bg-primary-500/10 text-primary-500 font-semibold' 
                         : 'text-surface-900 dark:text-surface-50 hover:bg-primary-500/5 hover:text-primary-500'}"
                on:click|preventDefault={handleLinkClick}
              >
                {link.label}
              </a>
            </li>
          {/each}
        </ul>
        
        <!-- Mobile CTA Buttons -->
        <div class="flex flex-col gap-3 pt-3 border-t border-surface-300-600-token">
          <a href="/signin" class="btn variant-ghost w-full" on:click|preventDefault={handleLinkClick}>Sign In</a>
          <a href="/signup" class="btn variant-filled-primary w-full" on:click|preventDefault={handleLinkClick}>Sign Up</a>
        </div>
      </div>
    </div>
  {/if}
</header>

<style>
  /* Skeleton-style header component */
  
  /* Container with max width */
  .container-xl {
    max-width: 1280px;
  }
  
  /* Nav link styles */
  .nav-link {
    position: relative;
    display: inline-block;
  }
  
  /* Button styles */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    font-weight: 500;
    border-radius: var(--rounded-token, 0.4rem);
    transition: all 0.2s ease-in-out;
  }
  
  .btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
  }
  
  .btn-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--rounded-token, 0.4rem);
  }
  
  /* Variant styles */
  .variant-ghost {
    background-color: transparent;
    color: var(--color-surface-900);
    border: 1px solid var(--color-surface-300);
  }
  
  .variant-ghost:hover {
    background-color: rgba(var(--color-surface-500-rgb), 0.1);
  }
  
  .variant-filled {
    background-color: var(--color-primary-500);
    color: white;
    border: 1px solid var(--color-primary-500);
  }
  
  .variant-filled:hover {
    background-color: var(--color-primary-600);
  }
  
  .variant-filled-primary {
    background-color: var(--color-primary-500);
    color: white;
    border: 1px solid var(--color-primary-500);
  }
  
  .variant-filled-primary:hover {
    background-color: var(--color-primary-600);
  }
  
  /* Colors */
  .text-primary-500 {
    color: var(--color-primary-500);
  }
  
  .text-surface-900 {
    color: var(--color-surface-900);
  }
  
  .dark .text-surface-50 {
    color: var(--color-surface-50);
  }
  
  .border-surface-300-600-token {
    border-color: var(--color-surface-300);
  }
  
  .dark .border-surface-300-600-token {
    border-color: var(--color-surface-600);
  }
  
  .border-primary-500 {
    border-color: var(--color-primary-500);
  }
  
  .border-primary-300 {
    border-color: var(--color-primary-300);
  }
  
  .border-transparent {
    border-color: transparent;
  }
  
  .bg-primary-500\/10 {
    background-color: rgba(var(--color-primary-500-rgb), 0.1);
  }
  
  .bg-primary-500\/5 {
    background-color: rgba(var(--color-primary-500-rgb), 0.05);
  }
  
  /* Border utilities */
  .border-b {
    border-bottom-width: 1px;
    border-bottom-style: solid;
  }
  
  .border-t {
    border-top-width: 1px;
    border-top-style: solid;
  }
  
  .border-b-2 {
    border-bottom-width: 2px;
    border-bottom-style: solid;
  }
  
  /* Rounded utilities */
  .rounded-token {
    border-radius: var(--rounded-token, 0.4rem);
  }
  
  /* Layout utilities */
  .flex {
    display: flex;
  }
  
  .hidden {
    display: none;
  }
  
  .flex-none {
    flex: none;
  }
  
  .flex-col {
    flex-direction: column;
  }
  
  .items-center {
    align-items: center;
  }
  
  .justify-between {
    justify-content: space-between;
  }
  
  .w-full {
    width: 100%;
  }
  
  .h-6, .w-6 {
    height: 1.5rem;
    width: 1.5rem;
  }
  
  /* Spacing utilities */
  .gap-2 {
    gap: 0.5rem;
  }
  
  .gap-3 {
    gap: 0.75rem;
  }
  
  .gap-4 {
    gap: 1rem;
  }
  
  .gap-6 {
    gap: 1.5rem;
  }
  
  .gap-8 {
    gap: 2rem;
  }
  
  .px-1 {
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }
  
  .px-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .py-2\.5 {
    padding-top: 0.625rem;
    padding-bottom: 0.625rem;
  }
  
  .py-3 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .pt-3 {
    padding-top: 0.75rem;
  }
  
  .p-2 {
    padding: 0.5rem;
  }
  
  .mb-6 {
    margin-bottom: 1.5rem;
  }
  
  .mx-auto {
    margin-left: auto;
    margin-right: auto;
  }
  
  /* Typography */
  .text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }
  
  .font-bold {
    font-weight: 700;
  }
  
  .font-medium {
    font-weight: 500;
  }
  
  .font-semibold {
    font-weight: 600;
  }
  
  /* Transitions */
  .transition-colors {
    transition-property: color, background-color, border-color;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .duration-200 {
    transition-duration: 200ms;
  }
  
  /* Media queries */
  @media (min-width: 1024px) {
    .lg\:flex {
      display: flex;
    }
    
    .lg\:hidden {
      display: none;
    }
  }
</style>