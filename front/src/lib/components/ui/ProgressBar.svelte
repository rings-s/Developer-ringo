<script>
  import { createEventDispatcher, onMount, tick } from 'svelte';
  
  // Component props
  export let value = 0; // Current progress value (0-100)
  export let max = 100; // Maximum value
  export let variant = "primary"; // primary, secondary, tertiary, etc.
  export let size = "md"; // xs, sm, md, lg, xl
  export let label = ""; // Text label
  export let showValue = false; // Show percentage value
  export let striped = false; // Add striped pattern
  export let animated = false; // Animate the stripes
  export let indeterminate = false; // Indeterminate progress state
  export let rounded = true; // Rounded corners
  export let height = null; // Custom height
  export let backgroundColor = null; // Custom background color
  export let labelPosition = "top"; // top, inside, bottom
  export let valuePosition = "right"; // right, inside, hidden
  export let valueFormat = "percent"; // percent, value, valueslash, custom
  export let customFormat = null; // Custom format function
  export let ariaLabel = ""; // Custom aria label for accessibility
  
  let progressElement;
  let progressResizeObserver;
  let progressBarWidth = 0;
  const dispatch = createEventDispatcher();

  // Ensure value is within bounds
  $: normalizedValue = Math.min(Math.max(0, value), max);
  
  // Calculate percentage
  $: percentage = (normalizedValue / max) * 100;
  
  // Size classes map height with Skeleton-like design tokens
  const sizeClasses = {
    xs: "progress-xs",
    sm: "progress-sm",
    md: "progress-md",
    lg: "progress-lg",
    xl: "progress-xl"
  };
  
  // Variant classes with Skeleton-like naming
  const variantClasses = {
    primary: "progress-primary",
    secondary: "progress-secondary",
    tertiary: "progress-tertiary",
    success: "progress-success",
    warning: "progress-warning",
    error: "progress-error",
  };
  
  // Background color classes with Skeleton-like naming
  const backgroundClasses = {
    primary: "bg-primary-track",
    secondary: "bg-secondary-track",
    tertiary: "bg-tertiary-track",
    success: "bg-success-track",
    warning: "bg-warning-track",
    error: "bg-error-track",
    surface: "bg-surface-track",
    transparent: "bg-transparent",
  };
  
  // Format the value display based on selected format
  function formatValue() {
    if (customFormat && typeof customFormat === 'function') {
      return customFormat(normalizedValue, max, percentage);
    }
    
    switch (valueFormat) {
      case "percent":
        return `${Math.round(percentage)}%`;
      case "value":
        return `${normalizedValue}`;
      case "valueslash":
        return `${normalizedValue}/${max}`;
      default:
        return `${Math.round(percentage)}%`;
    }
  }
  
  // Apply custom height if provided
  $: customHeight = height ? `height: ${height}px;` : '';
  
  // Apply custom background color if provided
  $: customBgColor = backgroundColor ? `background-color: ${backgroundColor};` : '';
  
  // Determine if progress bar should have space for inner text
  $: innerTextBar = labelPosition === 'inside' || valuePosition === 'inside';
  
  // Create a ResizeObserver to update width for animations
  function setupResizeObserver() {
    if (typeof ResizeObserver === 'undefined' || !progressElement) return;
    
    progressResizeObserver = new ResizeObserver(entries => {
      if (entries && entries[0]) {
        progressBarWidth = entries[0].contentRect.width;
      }
    });
    
    progressResizeObserver.observe(progressElement);
  }
  
  onMount(() => {
    setupResizeObserver();
    dispatch('mount', { element: progressElement });
    
    // Initial animation for a more polished appearance
    if (!indeterminate) {
      const initialBar = progressElement.querySelector('.progress-fill');
      if (initialBar) {
        initialBar.style.width = '0%';
        setTimeout(() => {
          initialBar.style.width = `${percentage}%`;
        }, 50);
      }
    }
    
    return () => {
      if (progressResizeObserver) {
        progressResizeObserver.disconnect();
      }
    };
  });
</script>

<div class="progress-container">
  <!-- Top label -->
  {#if label && labelPosition === 'top'}
    <div class="progress-label-top">
      {label}
    </div>
  {/if}
  
  <!-- Progress bar container -->
  <div 
    bind:this={progressElement}
    role="progressbar" 
    aria-valuenow={indeterminate ? null : normalizedValue} 
    aria-valuemin="0" 
    aria-valuemax={max}
    aria-valuetext={indeterminate ? "Loading..." : formatValue()}
    aria-label={ariaLabel || label || "Progress"}
    class="progress-track {backgroundClasses[variant] || backgroundClasses.surface} {sizeClasses[size] || sizeClasses.md} {rounded ? 'progress-rounded' : ''} {innerTextBar ? 'progress-with-text' : ''}"
    style={`${customHeight} ${customBgColor}`}
  >
    <!-- Inside label (left side) -->
    {#if label && labelPosition === 'inside'}
      <span class="progress-label-inside">
        {label}
      </span>
    {/if}
    
    <!-- Inside value -->
    {#if showValue && valuePosition === 'inside'}
      <span class="progress-value-inside">
        {formatValue()}
      </span>
    {/if}
    
    <!-- Progress fill -->
    <div 
      class="progress-fill {variantClasses[variant] || variantClasses.primary} {rounded ? 'progress-rounded' : ''} {striped ? 'progress-striped' : ''} {animated && striped ? 'progress-animated' : ''} {indeterminate ? 'progress-indeterminate' : ''}"
      style={indeterminate ? '' : `width: ${percentage}%;`}
    ></div>
  </div>
  
  <!-- Bottom label and/or value display -->
  {#if (label && labelPosition === 'bottom') || (showValue && valuePosition === 'right')}
    <div class="progress-info">
      {#if label && labelPosition === 'bottom'}
        <span class="progress-label-bottom">
          {label}
        </span>
      {:else}
        <span></span>
      {/if}
      
      {#if showValue && valuePosition === 'right'}
        <span class="progress-value-right">
          {formatValue()}
        </span>
      {/if}
    </div>
  {/if}
</div>

<style>
/* Skeleton-style Progress Component */
.progress-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: var(--space-4, 1rem);
}

/* Progress track (background) */
.progress-track {
  position: relative;
  width: 100%;
  overflow: hidden;
  background-color: var(--color-surface-300, #d1d5db);
}

/* Progress bar with text */
.progress-with-text {
  display: flex;
  align-items: center;
  padding: 0 var(--space-3, 0.75rem);
  min-height: 1.5rem;
}

/* Progress fill (foreground) */
.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: var(--color-primary-500, #3b82f6);
}

/* Size variants */
.progress-xs {
  height: 0.25rem;
}

.progress-sm {
  height: 0.5rem;
}

.progress-md {
  height: 0.75rem;
}

.progress-lg {
  height: 1rem;
}

.progress-xl {
  height: 1.25rem;
}

/* Rounded corners */
.progress-rounded {
  border-radius: 9999px;
}

/* Labels and values */
.progress-label-top,
.progress-label-bottom {
  font-size: var(--text-sm, 0.875rem);
  font-weight: 500;
  color: var(--color-surface-700, #374151);
  margin-bottom: var(--space-1, 0.25rem);
}

.progress-label-bottom {
  margin-top: var(--space-1, 0.25rem);
  margin-bottom: 0;
}

.progress-label-inside,
.progress-value-inside {
  position: relative;
  z-index: 1;
  font-size: var(--text-xs, 0.75rem);
  font-weight: 600;
  color: var(--color-surface-900, #111827);
  text-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}

.progress-label-inside {
  margin-right: auto;
}

.progress-value-inside {
  margin-left: auto;
}

.progress-value-right {
  font-size: var(--text-sm, 0.875rem);
  font-weight: 600;
  color: var(--color-surface-700, #374151);
  margin-left: var(--space-2, 0.5rem);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-1, 0.25rem);
}

/* Striped background pattern */
.progress-striped {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
}

/* Animation for striped background */
.progress-animated {
  animation: progress-stripes 1s linear infinite;
}

@keyframes progress-stripes {
  from {
    background-position: 1rem 0;
  }
  to {
    background-position: 0 0;
  }
}

/* Indeterminate animation */
.progress-indeterminate {
  width: 30%;
  animation: indeterminate 1.5s ease-in-out infinite;
}

@keyframes indeterminate {
  0% {
    left: -30%;
  }
  100% {
    left: 100%;
  }
}

/* Variant colors - Fill colors */
.progress-primary {
  background-color: var(--color-primary-500, #3b82f6);
}

.progress-secondary {
  background-color: var(--color-secondary-500, #6b7280);
}

.progress-tertiary {
  background-color: var(--color-tertiary-500, #8b5cf6);
}

.progress-success {
  background-color: var(--color-success-500, #10b981);
}

.progress-warning {
  background-color: var(--color-warning-500, #f59e0b);
}

.progress-error {
  background-color: var(--color-error-500, #ef4444);
}

/* Track colors */
.bg-primary-track {
  background-color: var(--color-primary-100, #dbeafe);
}

.bg-secondary-track {
  background-color: var(--color-secondary-100, #f3f4f6);
}

.bg-tertiary-track {
  background-color: var(--color-tertiary-100, #ede9fe);
}

.bg-success-track {
  background-color: var(--color-success-100, #d1fae5);
}

.bg-warning-track {
  background-color: var(--color-warning-100, #fef3c7);
}

.bg-error-track {
  background-color: var(--color-error-100, #fee2e2);
}

.bg-surface-track {
  background-color: var(--color-surface-200, #e5e7eb);
}
</style>