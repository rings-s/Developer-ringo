<!-- src/lib/components/ui/Toast.svelte -->
<script>
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    
    export let message = "";
    export let title = "";
    export let variant = "primary";
    export let icon = true;
    export let dismissible = true;
    export let duration = 5000; // ms to display toast before auto-dismissing (0 = never)
    export let position = "bottom-right"; // top, top-right, top-left, bottom, bottom-right, bottom-left
    export let action = null; // text for action button
    export let elevation = "lg";
    export let compact = false;
    export let visible = true;
    export let id = "";
    export let maxWidth = "380px";
    
    let toastElement;
    let timeoutId;
    let dismissing = false;
    let actionTriggered = false;
    const dispatch = createEventDispatcher();
    
    $: uniqueId = id || `toast-${Math.random().toString(36).substring(2, 11)}`;
    
    // Variant icons
    const variantIcons = {
      primary: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>`,
      secondary: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>`,
      success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>`,
      danger: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
               </svg>`,
      warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>`,
      info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
             </svg>`,
    };
    
    // Position classes
    const positionClasses = {
      "top": "top-4 left-1/2 transform -translate-x-1/2",
      "top-right": "top-4 right-4",
      "top-left": "top-4 left-4",
      "bottom": "bottom-4 left-1/2 transform -translate-x-1/2",
      "bottom-right": "bottom-4 right-4",
      "bottom-left": "bottom-4 left-4",
    };
    
    // Variant classes
    const variantClasses = {
      primary: "bg-primary-800 text-primary-100 border-primary-600",
      secondary: "bg-secondary-800 text-primary-100 border-secondary-600",
      success: "bg-green-800 text-primary-100 border-green-600",
      danger: "bg-danger-800 text-primary-100 border-danger-600",
      warning: "bg-yellow-800 text-primary-100 border-yellow-600",
      info: "bg-blue-800 text-primary-100 border-blue-600",
    };
    
    // Elevation classes
    const elevationClasses = {
      none: "",
      sm: "shadow-sm",
      md: "shadow",
      lg: "shadow-lg",
      xl: "shadow-xl",
    };
    
    // Action button classes based on variant
    const actionButtonClasses = {
      primary: "text-primary-100 hover:text-primary-300 focus:ring-primary-500",
      secondary: "text-primary-100 hover:text-secondary-300 focus:ring-secondary-500",
      success: "text-primary-100 hover:text-green-300 focus:ring-green-500",
      danger: "text-primary-100 hover:text-danger-300 focus:ring-danger-500",
      warning: "text-primary-100 hover:text-yellow-300 focus:ring-yellow-500",
      info: "text-primary-100 hover:text-blue-300 focus:ring-blue-500",
    };
    
    // Animation values based on position for entrance
    function getAnimationParams() {
      if (position.includes('top')) {
        return { y: -20 };
      } else if (position.includes('bottom')) {
        return { y: 20 };
      } else if (position.includes('left')) {
        return { x: -20 };
      } else if (position.includes('right')) {
        return { x: 20 };
      } else {
        return { y: -20 };
      }
    }
    
    // Auto-dismiss handling
    onMount(() => {
      if (duration > 0 && visible) {
        startDismissTimer();
      }
    });
    
    // Clear timer on unmount
    onDestroy(() => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    });
    
    // Watch for visibility changes
    $: if (visible && duration > 0 && !timeoutId) {
      startDismissTimer();
    } else if (!visible && timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    
    // Start timer for auto-dismiss
    function startDismissTimer() {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      timeoutId = setTimeout(() => {
        dismiss();
      }, duration);
    }
    
    // Handle manual dismiss
    function dismiss() {
      if (!dismissing) {
        dismissing = true;
        visible = false;
        timeoutId = null;
        dispatch('dismiss');
      }
    }
    
    // Handle action button click
    function handleAction() {
      actionTriggered = true;
      dismiss();
      dispatch('action');
    }
    
    // Pause timer on mouse enter
    function handleMouseEnter() {
      if (timeoutId && duration > 0) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    }
    
    // Restart timer on mouse leave
    function handleMouseLeave() {
      if (duration > 0 && visible && !dismissing && !actionTriggered) {
        startDismissTimer();
      }
    }
    
    // Handle keyboard events
    function handleKeydown(event) {
      if (event.key === 'Escape' && dismissible) {
        dismiss();
      }
    }
    
    // Compute final toast classes
    $: toastClasses = [
      "fixed",
      "flex items-start",
      positionClasses[position] || positionClasses["bottom-right"],
      "rounded-lg border-l-4",
      elevationClasses[elevation] || elevationClasses.lg,
      variantClasses[variant] || variantClasses.primary,
      compact ? "p-2" : "p-4",
      "w-full min-w-min",
      "z-50",
      $$restProps.class || ""
    ].join(" ");
  </script>
  
  {#if visible}
    <div
      bind:this={toastElement}
      id={uniqueId}
      class={toastClasses}
      style="max-width: {maxWidth};"
      role="alert"
      aria-live="assertive"
      in:fly={getAnimationParams()}
      out:fade
      on:mouseenter={handleMouseEnter}
      on:mouseleave={handleMouseLeave}
      on:keydown={handleKeydown}
      tabindex="0"
    >
      {#if icon}
        <div class="flex-shrink-0 mr-3" aria-hidden="true">
          {@html variantIcons[variant] || variantIcons.primary}
        </div>
      {/if}
      
      <div class="flex-1 min-w-0">
        {#if title}
          <h4 class="text-sm font-semibold mb-0.5">{title}</h4>
        {/if}
        
        <div class={`${title ? 'text-xs' : 'text-sm'}`}>
          {#if typeof message === 'string'}
            {message}
          {:else}
            <slot />
          {/if}
        </div>
        
        {#if action}
          <button
            type="button"
            class={`mt-2 text-sm font-medium ${actionButtonClasses[variant] || actionButtonClasses.primary} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50 rounded`}
            on:click={handleAction}
          >
            {action}
          </button>
        {/if}
      </div>
      
      {#if dismissible}
        <div class="flex-shrink-0 ml-2">
          <button
            type="button"
            class="text-primary-400 hover:text-primary-200 transition-colors"
            aria-label="Dismiss"
            on:click={dismiss}
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      {/if}
    </div>
  {/if}