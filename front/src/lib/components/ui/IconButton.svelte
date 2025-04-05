<!-- src/lib/components/ui/IconButton.svelte -->
 
<script>
  import { createEventDispatcher } from 'svelte';
  import Button from './Button.svelte';
  
  export let icon = null;
  export let variant = "primary";
  export let size = "md";
  export let type = "button";
  export let disabled = false;
  export let loading = false;
  export let ariaLabel = "";
  export let tooltip = null;
  export let tooltipPosition = "top";
  export let pulse = false;
  export let elevation = "md";
  export let badge = null;
  export let badgeVariant = "danger";
  export let tabIndex = 0;
  
  let showTooltip = false;
  let buttonRef;
  let tooltipTimeout;
  const dispatch = createEventDispatcher();
  
  // Size classes mapped to dimensions
  const sizeMap = {
    xs: "w-7 h-7 text-xs",
    sm: "w-9 h-9 text-sm",
    md: "w-11 h-11",
    lg: "w-14 h-14 text-lg",
    xl: "w-16 h-16 text-xl"
  };
  
  // Badge variant classes
  const badgeVariants = {
    primary: "bg-primary-500 text-background-900",
    secondary: "bg-secondary-500 text-primary-100",
    accent: "bg-accent-500 text-primary-100",
    danger: "bg-danger-500 text-background-900",
    success: "bg-green-500 text-background-900",
    warning: "bg-yellow-500 text-primary-100",
    info: "bg-blue-500 text-background-900"
  };
  
  // Badge position classes based on size
  $: badgePositionClass = size === 'xs' || size === 'sm' 
    ? "-top-1 -right-1" 
    : "-top-1.5 -right-1.5";
  
  $: pulseClass = pulse && !disabled && !loading ? "animate-pulse" : "";
  
  // Tooltip debouncing
  function showTooltipWithDelay() {
    clearTimeout(tooltipTimeout);
    tooltipTimeout = setTimeout(() => {
      showTooltip = true;
    }, 500); // Delay showing tooltip
  }
  
  function hideTooltipWithDelay() {
    clearTimeout(tooltipTimeout);
    tooltipTimeout = setTimeout(() => {
      showTooltip = false;
    }, 100);
  }
  
  // Clean up timeout on unmount
  import { onDestroy } from 'svelte';
  
  onDestroy(() => {
    if (tooltipTimeout) clearTimeout(tooltipTimeout);
  });
</script>

<div 
  class="relative inline-block" 
  on:mouseenter={tooltip ? showTooltipWithDelay : null}
  on:mouseleave={tooltip ? hideTooltipWithDelay : null}
  on:focus={tooltip ? () => showTooltip = true : null}
  on:blur={tooltip ? () => showTooltip = false : null}
  bind:this={buttonRef}
>
  <Button
    {variant}
    rounded={true}
    {disabled}
    {loading}
    {type}
    {elevation}
    {tabIndex}
    ariaLabel={ariaLabel || 'Button'}
    class="{sizeMap[size] || sizeMap.md} p-0 flex items-center justify-center {pulseClass} {$$restProps.class || ''}"
    on:click={event => dispatch('click', event)}
    on:focus
    on:blur
    {...$$restProps}
  >
    <slot>
      {#if icon}
        <span class="flex items-center justify-center">{@html icon}</span>
      {/if}
    </slot>
  </Button>
  
  {#if badge !== null && badge !== undefined}
    <span class={`absolute ${badgePositionClass} flex items-center justify-center ${badgeVariants[badgeVariant] || badgeVariants.danger} text-xs font-bold rounded-full h-5 min-w-5 px-1`}>
      {badge}
    </span>
  {/if}
  
  {#if tooltip && showTooltip}
    <div 
      class="absolute z-50 px-2 py-1 text-xs bg-primary-100 text-background-800 rounded shadow-lg pointer-events-none whitespace-nowrap
      {tooltipPosition === 'top' ? 'bottom-full left-1/2 transform -translate-x-1/2 -translate-y-2 mb-1' :
       tooltipPosition === 'right' ? 'left-full top-1/2 transform -translate-y-1/2 translate-x-2 ml-1' :
       tooltipPosition === 'bottom' ? 'top-full left-1/2 transform -translate-x-1/2 translate-y-2 mt-1' :
       'right-full top-1/2 transform -translate-y-1/2 -translate-x-2 mr-1'}"
      role="tooltip"
      transition:fade={{ duration: 150 }}
    >
      {tooltip}
      <div 
        class="absolute w-0 h-0 border-4
        {tooltipPosition === 'top' ? 'top-full left-1/2 transform -translate-x-1/2 border-t-primary-100 border-r-transparent border-b-transparent border-l-transparent' :
         tooltipPosition === 'right' ? 'right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-r-primary-100 border-b-transparent border-l-transparent' :
         tooltipPosition === 'bottom' ? 'bottom-full left-1/2 transform -translate-x-1/2 border-t-transparent border-r-transparent border-b-primary-100 border-l-transparent' :
         'left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-r-transparent border-b-transparent border-l-primary-100'}"
        aria-hidden="true"
      ></div>
    </div>
  {/if}
</div>

<style>
  @keyframes fade {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  /* Add utility class to ensure tooltip positioning */
  .min-w-5 {
    min-width: 1.25rem;
  }
</style>