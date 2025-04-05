<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  export let checked = false;
  export let disabled = false;
  export let label = "";
  export let size = "md";
  export let color = "primary";
  export let labelPosition = "right"; // right, left
  export let id = "";
  export let name = "";
  export let required = false;
  export let ariaLabel = "";
  export let ariaLabelledBy = "";
  export let labelClass = "";
  
  let switchElement;
  let switchTrack;
  let focused = false;
  
  const dispatch = createEventDispatcher();
  
  // Generate unique ID for a11y if not provided
  $: uniqueId = id || `switch-${Math.random().toString(36).substring(2, 11)}`;
  
  // Size variants for the switch with Skeleton spacing tokens
  const sizeClasses = {
    sm: {
      track: "w-7 h-4",
      thumb: "w-3 h-3",
      thumbOn: "translate-x-3",
      thumbOff: "translate-x-0.5",
      label: "text-sm"
    },
    md: {
      track: "w-10 h-5",
      thumb: "w-4 h-4",
      thumbOn: "translate-x-5.5",
      thumbOff: "translate-x-0.5",
      label: "text-base"
    },
    lg: {
      track: "w-12 h-6",
      thumb: "w-5 h-5",
      thumbOn: "translate-x-7",
      thumbOff: "translate-x-0.5",
      label: "text-lg"
    }
  };
  
  // Colors for switch variants with Skeleton color tokens
  const colorClasses = {
    primary: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-primary-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-primary-500/50"
    },
    secondary: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-secondary-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-secondary-500/50"
    },
    tertiary: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-tertiary-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-tertiary-500/50"
    },
    success: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-success-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-success-500/50"
    },
    warning: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-warning-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-warning-500/50"
    },
    error: {
      trackOff: "bg-surface-300/30",
      trackOn: "bg-error-500",
      thumbOff: "bg-surface-100",
      thumbOn: "bg-surface-50",
      focus: "ring-error-500/50"
    }
  };
  
  // Handle toggle
  function toggle(event) {
    if (!disabled) {
      checked = !checked;
      dispatch('change', { checked });
      event.preventDefault();
    }
  }
  
  // Handle keyboard events
  function handleKeydown(event) {
    if (disabled) return;
    
    if (event.key === ' ' || event.key === 'Enter') {
      checked = !checked;
      dispatch('change', { checked });
      event.preventDefault();
    }
  }
  
  // Focus/blur event handlers
  function handleFocus() {
    focused = true;
    dispatch('focus');
  }
  
  function handleBlur() {
    focused = false;
    dispatch('blur');
  }
</script>

<div class="switch-container {labelPosition === 'left' ? 'switch-reverse' : ''} {disabled ? 'switch-disabled' : ''}">
  <div class="switch-wrapper">
    <!-- Hidden checkbox for form submission -->
    <input 
      type="checkbox"
      id={uniqueId}
      bind:checked
      {disabled}
      {name}
      {required}
      class="switch-input"
      aria-checked={checked}
      aria-disabled={disabled}
      aria-label={ariaLabel || label || null}
      aria-labelledby={ariaLabelledBy || null}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:keydown={handleKeydown}
      {...$$restProps}
    />
    
    <!-- Switch track -->
    <div
      bind:this={switchTrack} 
      class="switch-track {sizeClasses[size]?.track || sizeClasses.md.track} 
             {checked 
                ? colorClasses[color]?.trackOn || colorClasses.primary.trackOn 
                : colorClasses[color]?.trackOff || colorClasses.primary.trackOff}
             {focused ? `switch-focused ${colorClasses[color]?.focus || colorClasses.primary.focus}` : ''}"
      role="presentation"
      on:click={toggle}
    >
      <!-- Switch thumb -->
      <span 
        class="switch-thumb {sizeClasses[size]?.thumb || sizeClasses.md.thumb}
               {checked 
                  ? colorClasses[color]?.thumbOn || colorClasses.primary.thumbOn 
                  : colorClasses[color]?.thumbOff || colorClasses.primary.thumbOff}
               {checked 
                  ? sizeClasses[size]?.thumbOn || sizeClasses.md.thumbOn 
                  : sizeClasses[size]?.thumbOff || sizeClasses.md.thumbOff}"
      ></span>
    </div>
  </div>
  
  <!-- Label -->
  {#if label}
    <label 
      for={uniqueId}
      class="switch-label {sizeClasses[size]?.label || sizeClasses.md.label} {labelClass}"
    >
      {label}
      {#if required}
        <span class="required-indicator">*</span>
      {/if}
    </label>
  {/if}
</div>

<style>
  /* Skeleton-style Switch Component */
  .switch-container {
    display: flex;
    align-items: center;
    margin-bottom: var(--space-3, 0.75rem);
  }
  
  .switch-reverse {
    flex-direction: row-reverse;
    justify-content: flex-end;
  }
  
  .switch-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
  }
  
  /* Hide the default checkbox input */
  .switch-input {
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
  
  /* Switch track and thumb styling */
  .switch-track {
    position: relative;
    display: inline-flex;
    align-items: center;
    border-radius: 9999px;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
  }
  
  .switch-thumb {
    position: absolute;
    border-radius: 50%;
    transform: translateY(-50%);
    top: 50%;
    transition: all 0.2s ease-in-out;
    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06));
  }
  
  /* Focus state */
  .switch-focused {
    ring: 2px;
    ring-offset: 2px;
  }
  
  /* Label styling */
  .switch-label {
    font-weight: 500;
    margin-left: var(--space-3, 0.75rem);
    color: var(--color-surface-900, #0f172a);
    cursor: pointer;
  }
  
  .switch-reverse .switch-label {
    margin-left: 0;
    margin-right: var(--space-3, 0.75rem);
  }
  
  /* Disabled state */
  .switch-disabled {
    opacity: 0.6;
    pointer-events: none;
  }
  
  .switch-disabled .switch-track {
    cursor: not-allowed;
  }
  
  .switch-disabled .switch-label {
    cursor: not-allowed;
  }
  
  /* Required indicator */
  .required-indicator {
    color: var(--color-error-500, #ef4444);
    margin-left: var(--space-1, 0.25rem);
  }
  
  /* Ensure the track has some padding for thumb positioning */
  .w-7 {
    width: 1.75rem;
  }
  
  .h-4 {
    height: 1rem;
  }
  
  .w-10 {
    width: 2.5rem;
  }
  
  .h-5 {
    height: 1.25rem;
  }
  
  .w-12 {
    width: 3rem;
  }
  
  .h-6 {
    height: 1.5rem;
  }
  
  .w-3 {
    width: 0.75rem;
  }
  
  .h-3 {
    height: 0.75rem;
  }
  
  .w-4 {
    width: 1rem;
  }
  
  .h-4 {
    height: 1rem;
  }
  
  .w-5 {
    width: 1.25rem;
  }
  
  .h-5 {
    height: 1.25rem;
  }
  
  /* Translation classes */
  .translate-x-0\.5 {
    transform: translate(0.125rem, -50%);
  }
  
  .translate-x-3 {
    transform: translate(0.75rem, -50%);
  }
  
  .translate-x-5\.5 {
    transform: translate(1.375rem, -50%);
  }
  
  .translate-x-7 {
    transform: translate(1.75rem, -50%);
  }
  
  /* Typography */
  .text-sm {
    font-size: var(--text-sm, 0.875rem);
  }
  
  .text-base {
    font-size: var(--text-base, 1rem);
  }
  
  .text-lg {
    font-size: var(--text-lg, 1.125rem);
  }
</style>