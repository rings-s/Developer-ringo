<script>
  export let variant = "primary";
  export let size = "md";
  export let label = "Loading...";
  export let showLabel = false;
  export let type = "border"; // border, grow, dots, pulse
  export let labelPosition = "right"; // right, bottom
  export let speed = "normal"; // slow, normal, fast
  export let ariaLabel = "";
  export let id = "";
  
  // Size classes for the different spinner types with Skeleton tokens
  const sizeClasses = {
    border: {
      xs: "spinner-xs",
      sm: "spinner-sm",
      md: "spinner-md",
      lg: "spinner-lg",
      xl: "spinner-xl"
    },
    grow: {
      xs: "spinner-grow-xs",
      sm: "spinner-grow-sm",
      md: "spinner-grow-md",
      lg: "spinner-grow-lg",
      xl: "spinner-grow-xl"
    },
    dots: {
      xs: "spinner-dots-xs",
      sm: "spinner-dots-sm",
      md: "spinner-dots-md",
      lg: "spinner-dots-lg",
      xl: "spinner-dots-xl"
    },
    pulse: {
      xs: "spinner-pulse-xs",
      sm: "spinner-pulse-sm",
      md: "spinner-pulse-md",
      lg: "spinner-pulse-lg",
      xl: "spinner-pulse-xl"
    }
  };
  
  // Animation speed classes
  const speedClasses = {
    border: {
      slow: "animate-spin-slow",
      normal: "animate-spin",
      fast: "animate-spin-fast"
    },
    grow: {
      slow: "animate-ping-slow",
      normal: "animate-ping",
      fast: "animate-ping-fast"
    },
    dots: {
      slow: "animate-bounce-slow",
      normal: "animate-bounce",
      fast: "animate-bounce-fast"
    },
    pulse: {
      slow: "animate-pulse-slow",
      normal: "animate-pulse",
      fast: "animate-pulse-fast"
    }
  };
  
  // Variant classes with Skeleton color tokens
  const variantClasses = {
    primary: "text-primary-500",
    secondary: "text-secondary-500",
    tertiary: "text-tertiary-500",
    success: "text-success-500",
    warning: "text-warning-500",
    error: "text-error-500",
    surface: "text-surface-500",
  };
  
  // Get the correct classes based on the spinner type
  $: spinnerSizeClass = sizeClasses[type]?.[size] || sizeClasses.border[size];
  $: spinnerSpeedClass = speedClasses[type]?.[speed] || speedClasses.border[speed];
  $: spinnerVariantClass = variantClasses[variant] || variantClasses.primary;
  
  // Generate a unique ID for accessibility if not provided
  $: uniqueId = id || `spinner-${Math.random().toString(36).substring(2, 11)}`;
</script>

<div 
  class="spinner-container {labelPosition === 'bottom' ? 'spinner-vertical' : 'spinner-horizontal'}" 
  role="status"
  aria-label={ariaLabel || label}
  id={uniqueId}
  aria-live="polite"
  {...$$restProps}
>
  {#if type === 'border'}
    <div 
      class="spinner-border {spinnerSizeClass} {spinnerSpeedClass} {spinnerVariantClass}" 
      aria-hidden="true"
    ></div>
  {:else if type === 'grow'}
    <div 
      class="spinner-grow {spinnerSizeClass} {spinnerSpeedClass} {spinnerVariantClass}" 
      aria-hidden="true"
    ></div>
  {:else if type === 'dots'}
    <div class="spinner-dots" aria-hidden="true">
      {#each Array(3) as _, i}
        <div 
          class="spinner-dot {spinnerSizeClass} {spinnerVariantClass} {spinnerSpeedClass}" 
          style="animation-delay: {i * 0.15}s"
        ></div>
      {/each}
    </div>
  {:else if type === 'pulse'}
    <div 
      class="spinner-pulse {spinnerSizeClass} {spinnerSpeedClass} {spinnerVariantClass}" 
      aria-hidden="true"
    ></div>
  {/if}
  
  {#if showLabel}
    <span class="spinner-label {labelPosition === 'right' ? 'spinner-label-right' : 'spinner-label-bottom'}">
      {label}
    </span>
  {/if}
  
  <!-- Allow custom content alongside the spinner -->
  {#if $$slots.default && !showLabel}
    <span class="spinner-label {labelPosition === 'right' ? 'spinner-label-right' : 'spinner-label-bottom'}">
      <slot />
    </span>
  {/if}
  
  <!-- Visually hidden text for screen readers when label is not shown -->
  {#if !showLabel && !$$slots.default}
    <span class="sr-only">{label}</span>
  {/if}
</div>

<style>
  /* Skeleton-style Spinner Component */
  
  /* Container styles */
  .spinner-container {
    display: inline-flex;
    align-items: center;
  }
  
  .spinner-horizontal {
    flex-direction: row;
  }
  
  .spinner-vertical {
    flex-direction: column;
    align-items: center;
  }
  
  /* Label styles */
  .spinner-label {
    font-size: var(--text-sm, 0.875rem);
    color: inherit;
  }
  
  .spinner-label-right {
    margin-left: var(--space-3, 0.75rem);
  }
  
  .spinner-label-bottom {
    margin-top: var(--space-2, 0.5rem);
  }
  
  /* Border Spinner */
  .spinner-border {
    display: inline-block;
    border-radius: 50%;
    border: 2px solid currentColor;
    border-right-color: transparent;
  }
  
  /* Size variants for border spinner */
  .spinner-xs {
    width: var(--size-4, 1rem);
    height: var(--size-4, 1rem);
    border-width: 2px;
  }
  
  .spinner-sm {
    width: var(--size-5, 1.25rem);
    height: var(--size-5, 1.25rem);
    border-width: 2px;
  }
  
  .spinner-md {
    width: var(--size-8, 2rem);
    height: var(--size-8, 2rem);
    border-width: 3px;
  }
  
  .spinner-lg {
    width: var(--size-10, 2.5rem);
    height: var(--size-10, 2.5rem);
    border-width: 3px;
  }
  
  .spinner-xl {
    width: var(--size-12, 3rem);
    height: var(--size-12, 3rem);
    border-width: 4px;
  }
  
  /* Grow Spinner */
  .spinner-grow {
    display: inline-block;
    border-radius: 50%;
    background-color: currentColor;
    opacity: 0;
  }
  
  /* Size variants for grow spinner */
  .spinner-grow-xs {
    width: var(--size-4, 1rem);
    height: var(--size-4, 1rem);
  }
  
  .spinner-grow-sm {
    width: var(--size-5, 1.25rem);
    height: var(--size-5, 1.25rem);
  }
  
  .spinner-grow-md {
    width: var(--size-8, 2rem);
    height: var(--size-8, 2rem);
  }
  
  .spinner-grow-lg {
    width: var(--size-10, 2.5rem);
    height: var(--size-10, 2.5rem);
  }
  
  .spinner-grow-xl {
    width: var(--size-12, 3rem);
    height: var(--size-12, 3rem);
  }
  
  /* Dots Spinner */
  .spinner-dots {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1, 0.25rem);
  }
  
  .spinner-dot {
    display: inline-block;
    border-radius: 50%;
    background-color: currentColor;
  }
  
  /* Size variants for dots */
  .spinner-dots-xs .spinner-dot {
    width: var(--size-1, 0.25rem);
    height: var(--size-1, 0.25rem);
  }
  
  .spinner-dots-sm .spinner-dot {
    width: var(--size-1-5, 0.375rem);
    height: var(--size-1-5, 0.375rem);
  }
  
  .spinner-dots-md .spinner-dot {
    width: var(--size-2, 0.5rem);
    height: var(--size-2, 0.5rem);
  }
  
  .spinner-dots-lg .spinner-dot {
    width: var(--size-2-5, 0.625rem);
    height: var(--size-2-5, 0.625rem);
  }
  
  .spinner-dots-xl .spinner-dot {
    width: var(--size-3, 0.75rem);
    height: var(--size-3, 0.75rem);
  }
  
  /* Pulse Spinner */
  .spinner-pulse {
    display: inline-block;
    border-radius: 50%;
    background-color: currentColor;
  }
  
  /* Size variants for pulse */
  .spinner-pulse-xs {
    width: var(--size-4, 1rem);
    height: var(--size-4, 1rem);
  }
  
  .spinner-pulse-sm {
    width: var(--size-5, 1.25rem);
    height: var(--size-5, 1.25rem);
  }
  
  .spinner-pulse-md {
    width: var(--size-8, 2rem);
    height: var(--size-8, 2rem);
  }
  
  .spinner-pulse-lg {
    width: var(--size-10, 2.5rem);
    height: var(--size-10, 2.5rem);
  }
  
  .spinner-pulse-xl {
    width: var(--size-12, 3rem);
    height: var(--size-12, 3rem);
  }
  
  /* Colors */
  .text-primary-500 {
    color: var(--color-primary-500, #3b82f6);
  }
  
  .text-secondary-500 {
    color: var(--color-secondary-500, #64748b);
  }
  
  .text-tertiary-500 {
    color: var(--color-tertiary-500, #8b5cf6);
  }
  
  .text-success-500 {
    color: var(--color-success-500, #10b981);
  }
  
  .text-warning-500 {
    color: var(--color-warning-500, #f59e0b);
  }
  
  .text-error-500 {
    color: var(--color-error-500, #ef4444);
  }
  
  .text-surface-500 {
    color: var(--color-surface-500, #6b7280);
  }
  
  /* Animations */
  .animate-spin {
    animation: spin 1s linear infinite;
  }
  
  .animate-spin-slow {
    animation: spin 2s linear infinite;
  }
  
  .animate-spin-fast {
    animation: spin 0.5s linear infinite;
  }
  
  .animate-ping {
    animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
  }
  
  .animate-ping-slow {
    animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
  }
  
  .animate-ping-fast {
    animation: ping 0.5s cubic-bezier(0, 0, 0.2, 1) infinite;
  }
  
  .animate-bounce {
    animation: bounce 1s infinite;
  }
  
  .animate-bounce-slow {
    animation: bounce 2s infinite;
  }
  
  .animate-bounce-fast {
    animation: bounce 0.5s infinite;
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  .animate-pulse-slow {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  .animate-pulse-fast {
    animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  @keyframes ping {
    75%, 100% {
      transform: scale(2);
      opacity: 0;
    }
  }
  
  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-25%);
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
  
  /* Screen reader only */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
</style>