<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  // Core button props
  export let variant = "filled";
  export let color = "primary";
  export let size = "md";
  export let type = "button";
  export let disabled = false;
  export let loading = false;
  export let fullWidth = false;
  export let pill = false;
  export let ripple = true;
  export let shimmer = false;
  export let icon = null;
  export let iconPosition = "left";
  export let square = false;
  export let ariaLabel = "";
  export let tabIndex = 0;

  // Internal state variables
  let buttonElement;
  let rippleElements = [];
  let buttonPressed = false;
  let rippleTimeout;
  let isHovered = false;
  let isFocused = false;
  
  const dispatch = createEventDispatcher();
  
  // Size classes with consistent spacing
  const sizeClasses = {
    xs: "btn-xs",
    sm: "btn-sm",
    md: "btn-md",
    lg: "btn-lg",
    xl: "btn-xl"
  };
  
  // Variant/color combinations using Skeleton tokens
  const variantColorClasses = {
    filled: {
      primary: "btn-filled-primary",
      secondary: "btn-filled-secondary", 
      tertiary: "btn-filled-tertiary",
      success: "btn-filled-success",
      warning: "btn-filled-warning",
      error: "btn-filled-error",
      surface: "btn-filled-surface"
    },
    outline: {
      primary: "btn-outline-primary",
      secondary: "btn-outline-secondary",
      tertiary: "btn-outline-tertiary",
      success: "btn-outline-success",
      warning: "btn-outline-warning",
      error: "btn-outline-error",
      surface: "btn-outline-surface"
    },
    ghost: {
      primary: "btn-ghost-primary",
      secondary: "btn-ghost-secondary",
      tertiary: "btn-ghost-tertiary",
      success: "btn-ghost-success",
      warning: "btn-ghost-warning",
      error: "btn-ghost-error",
      surface: "btn-ghost-surface"
    },
    link: {
      primary: "btn-link-primary",
      secondary: "btn-link-secondary",
      tertiary: "btn-link-tertiary",
      success: "btn-link-success",
      warning: "btn-link-warning",
      error: "btn-link-error",
      surface: "btn-link-surface"
    },
    soft: {
      primary: "btn-soft-primary",
      secondary: "btn-soft-secondary",
      tertiary: "btn-soft-tertiary",
      success: "btn-soft-success",
      warning: "btn-soft-warning",
      error: "btn-soft-error",
      surface: "btn-soft-surface"
    }
  };
  
  // Ripple effect handler
  function handleRipple(event) {
    if (!ripple || disabled || loading) return;
    
    const rect = buttonElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const circle = document.createElement("span");
    const diameter = Math.max(rect.width, rect.height) * 2;
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${x - radius}px`;
    circle.style.top = `${y - radius}px`;
    circle.classList.add("btn-ripple");
    
    // Remove old ripples
    if (rippleElements.length > 0) {
      rippleElements.forEach(el => {
        if (el && el.parentNode === buttonElement) {
          buttonElement.removeChild(el);
        }
      });
    }
    
    buttonElement.appendChild(circle);
    rippleElements = [...rippleElements, circle];
    
    // Clean up ripple after animation
    clearTimeout(rippleTimeout);
    rippleTimeout = setTimeout(() => {
      if (circle && circle.parentNode === buttonElement) {
        buttonElement.removeChild(circle);
        rippleElements = rippleElements.filter(el => el !== circle);
      }
    }, 600);
  }
  
  // Handle button press visual effects
  function handlePress() {
    buttonPressed = true;
  }
  
  function handleRelease() {
    buttonPressed = false;
  }
  
  // Handle hover state
  function handleMouseEnter() {
    isHovered = true;
  }
  
  function handleMouseLeave() {
    isHovered = false;
    handleRelease();
  }
  
  // Handle focus events for accessibility
  function handleFocus() {
    isFocused = true;
    dispatch('focus');
  }
  
  function handleBlur() {
    isFocused = false;
    dispatch('blur');
  }
  
  // Handle click with debounce for performance
  function handleClick(event) {
    if (!loading && !disabled) {
      handleRipple(event);
      dispatch('click', event);
    }
  }
  
  // Clean up on unmount
  onMount(() => {
    return () => {
      clearTimeout(rippleTimeout);
    };
  });

  // Compute class string with Skeleton naming conventions
  $: buttonClasses = [
    "btn",
    sizeClasses[size] || sizeClasses.md,
    variantColorClasses[variant]?.[color] || variantColorClasses.filled.primary,
    pill ? "btn-pill" : "btn-rounded",
    square ? "btn-square" : "",
    fullWidth ? "btn-full" : "",
    disabled ? "btn-disabled" : "",
    loading ? "btn-loading" : "",
    shimmer && !disabled && !loading ? "btn-shimmer" : "",
    buttonPressed ? "btn-pressed" : "",
    $$restProps.class || ""
  ].filter(Boolean).join(" ");
</script>

<button
  bind:this={buttonElement}
  {type}
  disabled={disabled || loading}
  class={buttonClasses}
  aria-label={ariaLabel || null}
  aria-disabled={disabled || loading}
  aria-busy={loading}
  tabindex={disabled ? -1 : tabIndex}
  on:click={handleClick}
  on:mousedown={handlePress}
  on:mouseup={handleRelease}
  on:mouseenter={handleMouseEnter}
  on:mouseleave={handleMouseLeave}
  on:focus={handleFocus}
  on:blur={handleBlur}
  on:keydown={e => e.key === 'Enter' || e.key === ' ' ? handleClick(e) : null}
  {...$$restProps}
>
  {#if loading}
    <div class="btn-loading-indicator" aria-hidden="true">
      <svg class="btn-spinner" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle class="btn-spinner-track" cx="12" cy="12" r="10" />
        <circle class="btn-spinner-head" cx="12" cy="12" r="10" />
      </svg>
    </div>
  {/if}
  
  <span class="btn-content {loading ? 'btn-content-loading' : ''}">
    {#if icon && iconPosition === "left"}
      <span class="btn-icon btn-icon-left" aria-hidden="true">{@html icon}</span>
    {/if}
    
    <slot></slot>
    
    {#if icon && iconPosition === "right"}
      <span class="btn-icon btn-icon-right" aria-hidden="true">{@html icon}</span>
    {/if}
  </span>
</button>

<style>
  /* Base Button Styles */
  .btn {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    user-select: none;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    overflow: hidden;
  }
  
  /* Content container */
  .btn-content {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 1;
    gap: var(--space-2, 0.5rem);
  }
  
  .btn-content-loading {
    opacity: 0;
  }
  
  /* Icon positioning */
  .btn-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  
  .btn-icon-left {
    margin-right: var(--space-1, 0.25rem);
  }
  
  .btn-icon-right {
    margin-left: var(--space-1, 0.25rem);
  }
  
  /* Size Variants */
  .btn-xs {
    height: var(--size-8, 2rem);
    min-width: var(--size-8, 2rem);
    padding: 0 var(--space-2, 0.5rem);
    font-size: var(--text-xs, 0.75rem);
    gap: var(--space-1, 0.25rem);
  }
  
  .btn-sm {
    height: var(--size-9, 2.25rem);
    min-width: var(--size-9, 2.25rem);
    padding: 0 var(--space-3, 0.75rem);
    font-size: var(--text-sm, 0.875rem);
    gap: var(--space-1-5, 0.375rem);
  }
  
  .btn-md {
    height: var(--size-10, 2.5rem);
    min-width: var(--size-10, 2.5rem);
    padding: 0 var(--space-4, 1rem);
    font-size: var(--text-base, 1rem);
    gap: var(--space-2, 0.5rem);
  }
  
  .btn-lg {
    height: var(--size-11, 2.75rem);
    min-width: var(--size-11, 2.75rem);
    padding: 0 var(--space-5, 1.25rem);
    font-size: var(--text-lg, 1.125rem);
    gap: var(--space-2-5, 0.625rem);
  }
  
  .btn-xl {
    height: var(--size-12, 3rem);
    min-width: var(--size-12, 3rem);
    padding: 0 var(--space-6, 1.5rem);
    font-size: var(--text-xl, 1.25rem);
    gap: var(--space-3, 0.75rem);
  }
  
  /* Shape Variants */
  .btn-rounded {
    border-radius: var(--rounded-md, 0.375rem);
  }
  
  .btn-pill {
    border-radius: 9999px;
  }
  
  .btn-square {
    aspect-ratio: 1/1;
    padding: 0;
  }
  
  /* Width Variant */
  .btn-full {
    width: 100%;
  }
  
  /* Pressed State */
  .btn-pressed {
    transform: translateY(1px);
  }
  
  /* Filled Variant Colors */
  .btn-filled-primary {
    background-color: var(--color-primary-500, #3b82f6);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-primary:hover:not(.btn-disabled) {
    background-color: var(--color-primary-600, #2563eb);
  }
  
  .btn-filled-primary:active:not(.btn-disabled) {
    background-color: var(--color-primary-700, #1d4ed8);
  }
  
  .btn-filled-secondary {
    background-color: var(--color-secondary-500, #64748b);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-secondary:hover:not(.btn-disabled) {
    background-color: var(--color-secondary-600, #475569);
  }
  
  .btn-filled-secondary:active:not(.btn-disabled) {
    background-color: var(--color-secondary-700, #334155);
  }
  
  .btn-filled-tertiary {
    background-color: var(--color-tertiary-500, #8b5cf6);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-tertiary:hover:not(.btn-disabled) {
    background-color: var(--color-tertiary-600, #7c3aed);
  }
  
  .btn-filled-tertiary:active:not(.btn-disabled) {
    background-color: var(--color-tertiary-700, #6d28d9);
  }
  
  .btn-filled-success {
    background-color: var(--color-success-500, #10b981);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-success:hover:not(.btn-disabled) {
    background-color: var(--color-success-600, #059669);
  }
  
  .btn-filled-success:active:not(.btn-disabled) {
    background-color: var(--color-success-700, #047857);
  }
  
  .btn-filled-warning {
    background-color: var(--color-warning-500, #f59e0b);
    color: var(--color-surface-900, #0f172a);
    border: none;
  }
  
  .btn-filled-warning:hover:not(.btn-disabled) {
    background-color: var(--color-warning-600, #d97706);
  }
  
  .btn-filled-warning:active:not(.btn-disabled) {
    background-color: var(--color-warning-700, #b45309);
  }
  
  .btn-filled-error {
    background-color: var(--color-error-500, #ef4444);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-error:hover:not(.btn-disabled) {
    background-color: var(--color-error-600, #dc2626);
  }
  
  .btn-filled-error:active:not(.btn-disabled) {
    background-color: var(--color-error-700, #b91c1c);
  }
  
  .btn-filled-surface {
    background-color: var(--color-surface-500, #6b7280);
    color: var(--color-surface-50, #f8fafc);
    border: none;
  }
  
  .btn-filled-surface:hover:not(.btn-disabled) {
    background-color: var(--color-surface-600, #4b5563);
  }
  
  .btn-filled-surface:active:not(.btn-disabled) {
    background-color: var(--color-surface-700, #374151);
  }
  
  /* Outline Variant Colors */
  .btn-outline-primary {
    background-color: transparent;
    color: var(--color-primary-500, #3b82f6);
    border: 1px solid var(--color-primary-500, #3b82f6);
  }
  
  .btn-outline-primary:hover:not(.btn-disabled) {
    background-color: var(--color-primary-100, #dbeafe);
    color: var(--color-primary-700, #1d4ed8);
  }
  
  .btn-outline-primary:active:not(.btn-disabled) {
    background-color: var(--color-primary-200, #bfdbfe);
    color: var(--color-primary-700, #1d4ed8);
  }
  
  /* Additional outline variants follow the same pattern... */
  
  /* Ghost Variant Colors */
  .btn-ghost-primary {
    background-color: transparent;
    color: var(--color-primary-500, #3b82f6);
    border: none;
  }
  
  .btn-ghost-primary:hover:not(.btn-disabled) {
    background-color: var(--color-primary-100, #dbeafe);
  }
  
  .btn-ghost-primary:active:not(.btn-disabled) {
    background-color: var(--color-primary-200, #bfdbfe);
  }
  
  /* Additional ghost variants follow the same pattern... */
  
  /* Link Variant Colors */
  .btn-link-primary {
    background-color: transparent;
    color: var(--color-primary-500, #3b82f6);
    border: none;
    padding: 0;
    height: auto;
    min-height: 0;
    text-decoration: underline;
  }
  
  .btn-link-primary:hover:not(.btn-disabled) {
    color: var(--color-primary-700, #1d4ed8);
    text-decoration: underline;
  }
  
  /* Additional link variants follow the same pattern... */
  
  /* Soft Variant Colors */
  .btn-soft-primary {
    background-color: var(--color-primary-100, #dbeafe);
    color: var(--color-primary-700, #1d4ed8);
    border: none;
  }
  
  .btn-soft-primary:hover:not(.btn-disabled) {
    background-color: var(--color-primary-200, #bfdbfe);
  }
  
  .btn-soft-primary:active:not(.btn-disabled) {
    background-color: var(--color-primary-300, #93c5fd);
  }
  
  /* Additional soft variants follow the same pattern... */
  
  /* Disabled State */
  .btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  /* Loading State */
  .btn-loading {
    cursor: wait;
  }
  
  .btn-loading-indicator {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
  }
  
  .btn-spinner {
    animation: spin 1s linear infinite;
    width: 1.25em;
    height: 1.25em;
  }
  
  .btn-spinner-track {
    fill: none;
    stroke: currentColor;
    stroke-opacity: 0.3;
    stroke-width: 2;
  }
  
  .btn-spinner-head {
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-dasharray: 20;
    stroke-dashoffset: 60;
  }
  
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  /* Ripple Effect */
  .btn-ripple {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.35);
    pointer-events: none;
    transform: scale(0);
    animation: ripple 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 0;
  }
  
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  /* Shimmer Effect */
  .btn-shimmer {
    position: relative;
    overflow: hidden;
  }
  
  .btn-shimmer::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(to right, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%);
    animation: shimmer 2s infinite linear;
    z-index: 0;
  }
  
  @keyframes shimmer {
    from {
      left: -100%;
    }
    to {
      left: 100%;
    }
  }
  
  /* Focus State */
  .btn:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
</style>