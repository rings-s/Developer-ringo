<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { slide, fade } from 'svelte/transition';
  
  export let title = "";
  export let subtitle = "";
  export let collapsible = false;
  export let collapsed = false;
  export let footer = false;
  export let hover = false;
  export let clickable = false;
  export let elevation = "md";
  export let variant = "default";
  export let rounded = "lg";
  export let loading = false;
  export let noPadding = false;
  export let gradient = false;
  export let flat = false;
  export let outlined = false;
  export let headerBorder = true;
  export let footerBorder = true;
  export let id = "";
  export let ariaLabelledBy = "";
  export let ariaDescribedBy = "";
  
  let isCollapsed = collapsed;
  let cardElement;
  let uniqueId;
  let contentElement;
  let contentResizeObserver;
  let contentHeight = 'auto';
  const dispatch = createEventDispatcher();
  
  // Generate unique IDs for ARIA attributes
  onMount(() => {
    uniqueId = Math.random().toString(36).substring(2, 11);
    
    // Set up ResizeObserver for smooth collapse animation
    if (collapsible && contentElement) {
      contentResizeObserver = new ResizeObserver(entries => {
        if (!isCollapsed && entries && entries[0]) {
          contentHeight = `${entries[0].contentRect.height}px`;
        }
      });
      
      contentResizeObserver.observe(contentElement);
    }
    
    return () => {
      if (contentResizeObserver) {
        contentResizeObserver.disconnect();
      }
    };
  });
  
  // Elevation (shadow) classes with improved Skeleton-like styles
  const elevationClasses = {
    none: "",
    sm: "shadow-sm hover:shadow",
    md: "shadow hover:shadow-md",
    lg: "shadow-md hover:shadow-lg",
    xl: "shadow-lg hover:shadow-xl",
  };
  
  // Rounded corner classes
  const roundedClasses = {
    none: "rounded-none",
    sm: "rounded-sm",
    md: "rounded",
    lg: "rounded-lg",
    xl: "rounded-xl",
    full: "rounded-3xl",
  };
  
  // Variant classes with Skeleton-like styling
  const variantClasses = {
    default: "bg-surface-900 border-surface-700",
    primary: "bg-primary-900 border-primary-700",
    secondary: "bg-secondary-900 border-secondary-700",
    accent: "bg-tertiary-900 border-tertiary-700",
    danger: "bg-error-900 border-error-700",
  };
  
  function toggleCollapse() {
    isCollapsed = !isCollapsed;
    dispatch('toggle', { collapsed: isCollapsed });
  }
  
  function handleClick(event) {
    if (clickable) {
      // Don't trigger when clicking elements like buttons inside the card
      if (event.target === cardElement || cardElement.contains(event.target)) {
        if (!event.target.closest('button, a, input, select, textarea')) {
          dispatch('click');
        }
      }
    }
  }
  
  // Generate IDs for accessibility
  $: titleId = ariaLabelledBy || (title ? `card-title-${id || uniqueId}` : '');
  $: contentId = ariaDescribedBy || `card-content-${id || uniqueId}`;
  
  // Compute final classes with Skeleton styling
  $: cardClasses = [
    "card",
    "transition-all duration-200 overflow-hidden",
    !flat && !outlined ? variantClasses[variant] || variantClasses.default : "",
    flat ? "bg-transparent border-transparent" : "",
    outlined ? `bg-transparent ${variantClasses[variant].split(' ')[1] || 'border-surface-700'}` : "",
    !flat && !outlined ? "border" : outlined ? "border-2" : "",
    elevationClasses[elevation],
    roundedClasses[rounded] || roundedClasses.lg,
    hover ? "hover:shadow-lg transform hover:-translate-y-1 transition-transform" : "",
    clickable ? "cursor-pointer" : "",
    gradient ? gradient === true ? "bg-gradient-to-br from-primary-700 to-primary-900" : gradient : "",
    loading ? "animate-pulse" : "",
    $$restProps.class || "",
  ].join(" ");
</script>

<div 
  bind:this={cardElement}
  class={cardClasses}
  on:click={handleClick}
  role={clickable ? "button" : null}
  tabindex={clickable ? "0" : null}
  aria-labelledby={titleId || null}
  aria-describedby={contentId || null}
  id={id || null}
  on:keydown={e => clickable && (e.key === 'Enter' || e.key === ' ') ? handleClick(e) : null}
  {...$$restProps}
>
  {#if title || subtitle || $$slots.header || collapsible}
    <div class="card-header">
      <div class="space-y-1"> <!-- Added vertical spacing between title and subtitle -->
        {#if $$slots.header}
          <slot name="header" />
        {:else}
          {#if title}
            <h3 id={titleId} class="card-title">{title}</h3>
          {/if}
          {#if subtitle}
            <p class="card-subtitle">{subtitle}</p>
          {/if}
        {/if}
      </div>
      
      {#if collapsible}
        <button 
          type="button" 
          class="p-1.5 ml-4 text-surface-900 hover:text-surface-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500"
          on:click|stopPropagation={toggleCollapse}
          aria-expanded={!isCollapsed}
          aria-controls={contentId}
        >
          <svg class="w-5 h-5 transform transition-transform {isCollapsed ? '' : 'rotate-180'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
      {/if}
    </div>
  {/if}

  {#if !collapsible || (collapsible && !isCollapsed)}
    <div 
      bind:this={contentElement}
      id={contentId}
      class="card-body" 
      style={collapsible ? `height: ${isCollapsed ? '0' : contentHeight}; overflow: ${isCollapsed ? 'hidden' : 'visible'};` : ''}
      transition:slide={{ duration: 300 }}
    >
      <slot />
    </div>
  {/if}

  {#if (footer || $$slots.footer) && (!collapsible || (collapsible && !isCollapsed))}
    <div 
      class="card-footer"
      transition:fade={{ duration: 200 }}
    >
      <slot name="footer">
        {#if footer && typeof footer === 'string'}
          <p class="text-sm text-surface-300">{footer}</p>
        {/if}
      </slot>
    </div>
  {/if}
</div>

<style>
  /* Skeleton-style Card Components */
  .card {
    display: flex;
    flex-direction: column;
    position: relative;
    margin-bottom: var(--space-4, 1rem);
    width: 100%;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-4, 1rem) var(--space-5, 1.25rem);
    border-bottom: 1px solid var(--color-surface-500, rgba(132, 165, 157, 0.2));
    background-color: rgba(23, 23, 23, 0.05);
  }
  
  .card-title {
    font-size: var(--text-xl, 1.25rem);
    font-weight: 600;
    line-height: 1.2;
    margin: 0;
    color: var(--color-surface-100, #2C3930);
  }
  
  .card-subtitle {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-surface-300, #adb5bd);
    margin: 0;
  }
  
  .card-body {
    flex: 1;
    padding: var(--space-5, 1.25rem);
  }
  
  .card-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: var(--space-4, 1rem) var(--space-5, 1.25rem);
    border-top: 1px solid var(--color-surface-500, rgba(132, 165, 157, 0.2));
    background-color: rgba(23, 23, 23, 0.05);
    gap: var(--space-2, 0.5rem);
  }
  
  /* Card variants and modifiers can be extended */
  
  /* Responsive modifications */
  @media (max-width: 640px) {
    .card-header, .card-body, .card-footer {
      padding: var(--space-3, 0.75rem);
    }
  }
</style>