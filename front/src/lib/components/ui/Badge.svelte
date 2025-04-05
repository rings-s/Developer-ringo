<script>
  export let variant = "primary";
  export let size = "md";
  export let pill = true;
  export let outline = false;
  export let dot = false;
  export let pulse = false;
  export let removable = false;
  export let icon = null;
  export let ariaLabel = "";
  export let id = "";
  
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  
  // Generate a unique ID for accessibility
  $: uniqueId = id || `badge-${Math.random().toString(36).substring(2, 11)}`;
  
  // Variant-specific classes with Skeleton styling
  const variantClasses = {
    primary: outline 
      ? "badge-outline-primary" 
      : "badge-filled-primary",
    secondary: outline 
      ? "badge-outline-secondary" 
      : "badge-filled-secondary",
    tertiary: outline 
      ? "badge-outline-tertiary" 
      : "badge-filled-tertiary",
    success: outline 
      ? "badge-outline-success" 
      : "badge-filled-success",
    warning: outline 
      ? "badge-outline-warning" 
      : "badge-filled-warning",
    error: outline 
      ? "badge-outline-error" 
      : "badge-filled-error",
    surface: outline 
      ? "badge-outline-surface" 
      : "badge-filled-surface",
  };
  
  // Size classes with consistent Skeleton-like spacing
  const sizeClasses = {
    xs: "badge-xs",
    sm: "badge-sm",
    md: "badge-md",
    lg: "badge-lg",
  };
  
  function handleRemove(event) {
    event.stopPropagation();
    dispatch('remove');
  }
</script>

<span 
  id={uniqueId}
  class="badge {variantClasses[variant] || variantClasses.primary} {sizeClasses[size] || sizeClasses.md} {pill ? 'badge-pill' : 'badge-square'} {$$restProps.class || ''}"
  role={removable ? "button" : null}
  aria-label={ariaLabel || null}
  {...$$restProps}
>
  {#if dot}
    <span class="badge-dot {pulse ? 'badge-dot-pulse' : ''}"></span>
  {/if}
  
  {#if icon}
    <span class="badge-icon">{@html icon}</span>
  {/if}
  
  <span class="badge-content">
    <slot />
  </span>
  
  {#if removable}
    <button 
      type="button" 
      class="badge-remove"
      on:click={handleRemove}
      aria-label="Remove"
    >
      <svg class="badge-remove-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  {/if}
</span>

<style>
  /* Skeleton-style Badge Component */
  .badge {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    transition: all 0.2s ease-in-out;
  }
  
  /* Size variants */
  .badge-xs {
    padding: var(--space-0-5, 0.125rem) var(--space-1, 0.25rem);
    font-size: var(--text-2xs, 0.625rem);
    min-height: 1.25rem;
  }
  
  .badge-sm {
    padding: var(--space-1, 0.25rem) var(--space-2, 0.5rem);
    font-size: var(--text-xs, 0.75rem);
    min-height: 1.5rem;
  }
  
  .badge-md {
    padding: var(--space-1-5, 0.375rem) var(--space-3, 0.75rem);
    font-size: var(--text-sm, 0.875rem);
    min-height: 1.75rem;
  }
  
  .badge-lg {
    padding: var(--space-2, 0.5rem) var(--space-4, 1rem);
    font-size: var(--text-base, 1rem);
    min-height: 2rem;
  }
  
  /* Shape variants */
  .badge-pill {
    border-radius: 9999px;
  }
  
  .badge-square {
    border-radius: var(--rounded-base, 0.25rem);
  }
  
  /* Content layout */
  .badge-content {
    display: inline-block;
    vertical-align: middle;
  }
  
  .badge-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: var(--space-1-5, 0.375rem);
  }
  
  /* Removable badge */
  .badge-remove {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    margin-left: var(--space-1-5, 0.375rem);
    margin-right: var(--space-0-5, 0.125rem);
    background: transparent;
    border: none;
    cursor: pointer;
    color: inherit;
    opacity: 0.7;
    transition: opacity 0.2s ease-in-out;
  }
  
  .badge-remove:hover {
    opacity: 1;
  }
  
  .badge-remove-icon {
    width: 0.875em;
    height: 0.875em;
  }
  
  /* Status dot */
  .badge-dot {
    position: absolute;
    top: calc(-1 * var(--space-1, 0.25rem));
    right: calc(-1 * var(--space-1, 0.25rem));
    width: var(--space-2, 0.5rem);
    height: var(--space-2, 0.5rem);
    border-radius: 50%;
    background-color: var(--color-error-500, #f56565);
  }
  
  .badge-dot-pulse {
    animation: badge-pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  @keyframes badge-pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
  
  /* Filled variant colors */
  .badge-filled-primary {
    background-color: var(--color-primary-500, #3b82f6);
    color: var(--color-surface-50, #f8fafc);
  }
  
  .badge-filled-secondary {
    background-color: var(--color-secondary-500, #6b7280);
    color: var(--color-surface-50, #f8fafc);
  }
  
  .badge-filled-tertiary {
    background-color: var(--color-tertiary-500, #8b5cf6);
    color: var(--color-surface-50, #f8fafc);
  }
  
  .badge-filled-success {
    background-color: var(--color-success-500, #10b981);
    color: var(--color-surface-50, #f8fafc);
  }
  
  .badge-filled-warning {
    background-color: var(--color-warning-500, #f59e0b);
    color: var(--color-surface-900, #0f172a);
  }
  
  .badge-filled-error {
    background-color: var(--color-error-500, #ef4444);
    color: var(--color-surface-50, #f8fafc);
  }
  
  .badge-filled-surface {
    background-color: var(--color-surface-500, #64748b);
    color: var(--color-surface-50, #f8fafc);
  }
  
  /* Outline variant colors */
  .badge-outline-primary {
    background-color: transparent;
    color: var(--color-primary-500, #3b82f6);
    border: 1px solid var(--color-primary-500, #3b82f6);
  }
  
  .badge-outline-secondary {
    background-color: transparent;
    color: var(--color-secondary-500, #6b7280);
    border: 1px solid var(--color-secondary-500, #6b7280);
  }
  
  .badge-outline-tertiary {
    background-color: transparent;
    color: var(--color-tertiary-500, #8b5cf6);
    border: 1px solid var(--color-tertiary-500, #8b5cf6);
  }
  
  .badge-outline-success {
    background-color: transparent;
    color: var(--color-success-500, #10b981);
    border: 1px solid var(--color-success-500, #10b981);
  }
  
  .badge-outline-warning {
    background-color: transparent;
    color: var(--color-warning-500, #f59e0b);
    border: 1px solid var(--color-warning-500, #f59e0b);
  }
  
  .badge-outline-error {
    background-color: transparent;
    color: var(--color-error-500, #ef4444);
    border: 1px solid var(--color-error-500, #ef4444);
  }
  
  .badge-outline-surface {
    background-color: transparent;
    color: var(--color-surface-500, #64748b);
    border: 1px solid var(--color-surface-500, #64748b);
  }
  
  /* Hover states */
  .badge[role="button"]:hover {
    opacity: 0.9;
    cursor: pointer;
  }
</style>