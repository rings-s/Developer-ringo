<script>
  import { createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  export let variant = "primary";
  export let title = "";
  export let dismissible = false;
  export let icon = true;
  export let rounded = "md";
  export let bordered = true;
  export let elevated = false;
  export let banner = false;
  export let timeout = 0; // Auto-dismiss in ms (0 means no auto-dismiss)
  export let compact = false;
  export let id = "";
  export let role = "alert";
  export let ariaLive = "assertive";
  
  let visible = true;
  let timeoutId;
  const dispatch = createEventDispatcher();
  
  // Generate a unique ID for accessibility
  $: uniqueId = id || `alert-${Math.random().toString(36).substring(2, 11)}`;
  
  // Set auto-dismiss timeout if specified
  import { onMount, onDestroy } from 'svelte';
  
  onMount(() => {
    if (timeout > 0) {
      timeoutId = setTimeout(() => {
        dismiss();
      }, timeout);
    }
  });
  
  onDestroy(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  });
  
  // Variant-specific classes with Skeleton-like tokens
  const variantClasses = {
    primary: "alert-primary",
    secondary: "alert-secondary",
    tertiary: "alert-tertiary",
    success: "alert-success",
    warning: "alert-warning",
    error: "alert-error",
    info: "alert-info",
  };
  
  // Rounded corner classes
  const roundedClasses = {
    none: "rounded-none",
    sm: "rounded-sm",
    md: "rounded-md",
    lg: "rounded-lg",
    xl: "rounded-xl",
    full: "rounded-full",
  };
  
  function dismiss() {
    visible = false;
    dispatch('dismiss');
  }
  
  // Handle keydown events for accessibility
  function handleKeydown(event) {
    if (dismissible && event.key === 'Escape') {
      dismiss();
    }
  }
</script>

{#if visible}
  <div 
    id={uniqueId}
    {role}
    aria-live={ariaLive}
    class="alert {variantClasses[variant] || variantClasses.primary} {rounded ? roundedClasses[rounded] || roundedClasses.md : ''} {elevated ? 'alert-elevated' : ''} {bordered ? 'alert-bordered' : ''} {banner ? 'alert-banner' : ''} {compact ? 'alert-compact' : ''}"
    in:fly={{ y: 20, duration: 300 }}
    out:fade={{ duration: 200 }}
    on:keydown={handleKeydown}
    tabindex={dismissible ? "0" : null}
    {...$$restProps}
  >
    <div class="alert-content">
      {#if icon}
        <div class="alert-icon" aria-hidden="true">
          {#if variant === 'primary' || variant === 'info'}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-svg">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 16v-4"></path>
              <path d="M12 8h.01"></path>
            </svg>
          {:else if variant === 'success'}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-svg">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          {:else if variant === 'warning'}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-svg">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          {:else if variant === 'error'}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-svg">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-svg">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          {/if}
        </div>
      {/if}
      
      <div class="alert-message">
        {#if title}
          <h3 class="alert-title">{title}</h3>
        {/if}
        <div class={`alert-text ${title ? 'has-title' : ''}`}>
          <slot />
        </div>
      </div>
      
      {#if dismissible}
        <button 
          type="button"
          class="alert-close"
          on:click={dismiss}
          aria-label="Dismiss"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Skeleton-style Alert Component */
  .alert {
    position: relative;
    width: 100%;
    margin-bottom: var(--space-4, 1rem);
    padding: 0;
    overflow: hidden;
  }
  
  .alert-content {
    display: flex;
    align-items: flex-start;
    width: 100%;
    padding: var(--space-4, 1rem);
  }
  
  /* Icon styling */
  .alert-icon {
    flex-shrink: 0;
    margin-right: var(--space-3, 0.75rem);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .alert-svg {
    width: 1.5rem;
    height: 1.5rem;
    stroke-width: 2;
  }
  
  /* Message container */
  .alert-message {
    flex: 1;
    min-width: 0;
  }
  
  /* Title styling */
  .alert-title {
    margin: 0 0 var(--space-1, 0.25rem) 0;
    font-size: var(--text-lg, 1.125rem);
    font-weight: 600;
    line-height: 1.4;
  }
  
  /* Text styling */
  .alert-text {
    margin: 0;
    font-size: var(--text-sm, 0.875rem);
    line-height: 1.5;
  }
  
  .alert-text.has-title {
    font-size: var(--text-sm, 0.875rem);
  }
  
  /* Close button */
  .alert-close {
    flex-shrink: 0;
    margin-left: var(--space-3, 0.75rem);
    background: transparent;
    border: 0;
    padding: var(--space-1, 0.25rem);
    cursor: pointer;
    color: inherit;
    opacity: 0.7;
    transition: opacity 0.2s ease-in-out;
    line-height: 0;
    border-radius: var(--rounded-md, 0.375rem);
  }
  
  .alert-close:hover {
    opacity: 1;
  }
  
  .alert-close:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 1px;
  }
  
  /* Compact style */
  .alert-compact .alert-content {
    padding: var(--space-2, 0.5rem) var(--space-3, 0.75rem);
  }
  
  .alert-compact .alert-svg {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .alert-compact .alert-title {
    font-size: var(--text-base, 1rem);
  }
  
  .alert-compact .alert-text {
    font-size: var(--text-xs, 0.75rem);
  }
  
  /* Banner style */
  .alert-banner {
    border-radius: 0;
    margin-left: calc(-1 * var(--space-4, 1rem));
    margin-right: calc(-1 * var(--space-4, 1rem));
    border-left: 0;
    border-right: 0;
  }
  
  /* Elevated style */
  .alert-elevated {
    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06));
  }
  
  /* Bordered style */
  .alert-bordered {
    border-left-width: 4px;
    border-left-style: solid;
  }
  
  /* Rounded corners */
  .rounded-md {
    border-radius: var(--rounded-md, 0.375rem);
  }
  
  .rounded-none {
    border-radius: 0;
  }
  
  .rounded-sm {
    border-radius: var(--rounded-sm, 0.125rem);
  }
  
  .rounded-lg {
    border-radius: var(--rounded-lg, 0.5rem);
  }
  
  .rounded-xl {
    border-radius: var(--rounded-xl, 0.75rem);
  }
  
  .rounded-full {
    border-radius: var(--rounded-full, 9999px);
  }
  
  /* Variant Styles */
  .alert-primary {
    background-color: var(--color-primary-100, #dbeafe);
    color: var(--color-primary-800, #1e40af);
    border-color: var(--color-primary-500, #3b82f6);
  }
  
  .alert-secondary {
    background-color: var(--color-secondary-100, #f1f5f9);
    color: var(--color-secondary-800, #1e293b);
    border-color: var(--color-secondary-500, #64748b);
  }
  
  .alert-tertiary {
    background-color: var(--color-tertiary-100, #ede9fe);
    color: var(--color-tertiary-800, #5b21b6);
    border-color: var(--color-tertiary-500, #8b5cf6);
  }
  
  .alert-success {
    background-color: var(--color-success-100, #dcfce7);
    color: var(--color-success-800, #166534);
    border-color: var(--color-success-500, #10b981);
  }
  
  .alert-warning {
    background-color: var(--color-warning-100, #fef3c7);
    color: var(--color-warning-800, #92400e);
    border-color: var(--color-warning-500, #f59e0b);
  }
  
  .alert-error {
    background-color: var(--color-error-100, #fee2e2);
    color: var(--color-error-800, #991b1b);
    border-color: var(--color-error-500, #ef4444);
  }
  
  .alert-info {
    background-color: var(--color-primary-100, #dbeafe);
    color: var(--color-primary-800, #1e40af);
    border-color: var(--color-primary-500, #3b82f6);
  }
</style>