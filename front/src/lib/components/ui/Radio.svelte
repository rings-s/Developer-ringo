<!-- src/lib/components/ui/Radio.svelte -->

<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  export let id = "";
  export let name = "";
  export let label = "";
  export let value = "";
  export let group = "";
  export let disabled = false;
  export let required = false;
  export let error = "";
  export let size = "md";
  export let variant = "primary";
  export let withRipple = true;
  export let ariaLabel = "";
  export let ariaLabelledBy = "";
  export let ariaDescribedBy = "";
  
  let radioElement;
  let rippleElement;
  let rippleTimeout;
  const dispatch = createEventDispatcher();
  
  // Generate an ID if none provided
  $: uniqueId = id || (label ? `radio-${name}-${value}`.toLowerCase().replace(/\s+/g, '-') : "");
  
  // Error ID for aria-describedby
  $: errorId = error && uniqueId ? `${uniqueId}-error` : null;
  
  // Combined aria-describedby with custom and error IDs
  $: finalAriaDescribedBy = [ariaDescribedBy, errorId].filter(Boolean).join(' ') || null;
  
  onMount(() => {
    return () => {
      clearTimeout(rippleTimeout);
    };
  });
  
  // Size classes for the radio
  const sizeClasses = {
    sm: "w-3.5 h-3.5",
    md: "w-4 h-4",
    lg: "w-5 h-5",
    xl: "w-6 h-6"
  };
  
  // Size classes for the label
  const labelSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
    xl: "text-xl"
  };
  
  // Variant classes for the radio
  const variantClasses = {
    primary: "text-primary-500 focus:ring-primary-500",
    secondary: "text-secondary-500 focus:ring-secondary-500",
    accent: "text-accent-500 focus:ring-accent-500",
    danger: "text-danger-500 focus:ring-danger-500"
  };
  
  // Handle change
  function handleChange(event) {
    group = event.target.value;
    dispatch('change', { value: group });
  }
  
  // Ripple effect for the radio
  function createRipple(event) {
    if (!withRipple || disabled) return;
    
    if (rippleElement) {
      rippleElement.remove();
    }
    
    rippleElement = document.createElement('span');
    rippleElement.classList.add('radio-ripple');
    
    const diameter = Math.max(radioElement.offsetWidth, radioElement.offsetHeight) * 2;
    rippleElement.style.width = `${diameter}px`;
    rippleElement.style.height = `${diameter}px`;
    
    const rect = radioElement.getBoundingClientRect();
    rippleElement.style.left = `${event.clientX - rect.left - diameter / 2}px`;
    rippleElement.style.top = `${event.clientY - rect.top - diameter / 2}px`;
    
    radioElement.parentNode.appendChild(rippleElement);
    
    clearTimeout(rippleTimeout);
    rippleTimeout = setTimeout(() => {
      if (rippleElement && rippleElement.parentNode) {
        rippleElement.remove();
      }
    }, 600);
  }
  
  // Handle keyboard interactions
  function handleKeydown(event) {
    if (event.key === ' ' || event.key === 'Enter') {
      // Don't create ripple on keyboard events to avoid positioning issues
      if (!disabled) {
        group = value;
        dispatch('change', { value: group });
      }
    }
  }
</script>

<div class="flex items-center mb-2">
  <div class="relative">
    <input
      bind:this={radioElement}
      type="radio"
      {id}
      {name}
      {value}
      {disabled}
      {required}
      bind:group
      class={`rounded-full border-primary-700 ${sizeClasses[size] || sizeClasses.md} ${variantClasses[variant] || variantClasses.primary}
              ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'} 
              ${error ? 'border-danger-500' : ''}
              transition-all duration-200`}
      aria-invalid={error ? "true" : "false"}
      aria-describedby={finalAriaDescribedBy}
      aria-label={ariaLabel || null}
      aria-labelledby={ariaLabelledBy || null}
      on:change={handleChange}
      on:keydown={handleKeydown}
      on:focus={() => dispatch('focus')}
      on:blur={() => dispatch('blur')}
      on:mousedown={createRipple}
      {...$$restProps}
    />
  </div>
  
  <div class="ml-3">
    {#if label}
      <label 
        for={id} 
        class={`font-medium text-primary-100 ${labelSizeClasses[size] || labelSizeClasses.md} ${disabled ? 'opacity-60' : ''} cursor-pointer`}
      >
        {label}
        {#if required}
          <span class="text-danger-500 ml-1">*</span>
        {/if}
      </label>
    {/if}
    
    {#if error}
      <p id={errorId} class="mt-1 text-sm text-danger-500">{error}</p>
    {/if}
    
    {#if $$slots.default}
      <div class="mt-1 text-sm text-primary-300">
        <slot></slot>
      </div>
    {/if}
  </div>
</div>

<style>
  .radio-ripple {
    position: absolute;
    background-color: rgba(132, 165, 157, 0.3);
    border-radius: 50%;
    transform: scale(0);
    animation: ripple 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    pointer-events: none;
    z-index: -1;
  }
  
  @keyframes ripple {
    to {
      transform: scale(1);
      opacity: 0;
    }
  }
</style>