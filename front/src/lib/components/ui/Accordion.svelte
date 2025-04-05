<script>
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  
  export let items = [];
  export let multiple = false;
  export let expanded = [];
  export let variant = "default";
  export let bordered = true;
  export let dividers = true;
  export let iconPosition = "right";
  export let chevronIcon = true;
  export let rounded = true;
  export let flush = false;
  export let elevated = false;
  export let size = "default"; // New prop for size variants
  export let spacing = "normal"; // New prop for spacing control
  export let maxWidth = "full"; // New prop for container max width
  export let ariaLabel = "Accordion";
  
  let accordionElement;
  let itemRefs = [];
  const dispatch = createEventDispatcher();
  
  // Generate unique IDs for each item (improved for better uniqueness)
  $: itemIds = items.map((_, i) => `accordion-${i}-${Math.random().toString(36).slice(2, 9)}`);
  
  // Initialize itemRefs array
  $: {
    itemRefs = Array(items.length).fill(null);
  }
  
  // Normalize the expanded prop into an array
  function normalizeExpanded(value) {
    if (Array.isArray(value)) return value;
    if (!value) return [];
    return [value];
  }
  
  // Get the current expanded state
  $: expandedState = normalizeExpanded(expanded);
  
  // Limit to one item if not in multiple mode
  $: expandedStateFixed = !multiple && expandedState.length > 1 
    ? [expandedState[0]] 
    : expandedState;
  
  // Variant classes with improved Skeleton-style consistency and spacing
  const variantClasses = {
    default: {
      wrapper: "bg-surface-900 border-surface-700",
      header: "bg-surface-800/10 hover:bg-surface-800/20",
      content: "bg-surface-900"
    },
    primary: {
      wrapper: "bg-primary-900 border-primary-700",
      header: "bg-primary-800/50 hover:bg-primary-800/70",
      content: "bg-primary-900"
    },
    secondary: {
      wrapper: "bg-secondary-900 border-secondary-700",
      header: "bg-secondary-800/50 hover:bg-secondary-800/70",
      content: "bg-secondary-900"
    },
    tertiary: {
      wrapper: "bg-tertiary-900 border-tertiary-700",
      header: "bg-tertiary-800/50 hover:bg-tertiary-800/70",
      content: "bg-tertiary-900"
    },
    ghost: {
      wrapper: "bg-transparent border-surface-700/50",
      header: "hover:bg-surface-800/10",
      content: "bg-transparent"
    }
  };
  
  // Size classes for consistent sizing
  const sizeClasses = {
    sm: {
      header: "p-3 text-sm",
      content: "p-3",
      icon: "w-4 h-4"
    },
    default: {
      header: "p-4 text-base",
      content: "p-4",
      icon: "w-5 h-5"
    },
    lg: {
      header: "p-5 text-lg",
      content: "p-5",
      icon: "w-6 h-6"
    }
  };
  
  // Spacing classes for better layout control
  const spacingClasses = {
    compact: "space-y-1",
    normal: "space-y-2",
    relaxed: "space-y-3"
  };
  
  // Width classes for responsive design
  const widthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    "3xl": "max-w-3xl",
    "4xl": "max-w-4xl",
    "5xl": "max-w-5xl",
    "6xl": "max-w-6xl",
    "7xl": "max-w-7xl",
    "full": "max-w-full"
  };
  
  // Toggle an item's expanded state
  function toggleItem(index) {
    const itemId = items[index].id || index;
    
    if (multiple) {
      // For multiple mode, toggle the clicked item
      if (expandedStateFixed.includes(itemId)) {
        expanded = expandedStateFixed.filter(id => id !== itemId);
      } else {
        expanded = [...expandedStateFixed, itemId];
      }
    } else {
      // For single mode, replace with the clicked item or collapse if it's already expanded
      if (expandedStateFixed.includes(itemId)) {
        expanded = [];
      } else {
        expanded = [itemId];
      }
    }
    
    dispatch('change', { expanded });
  }
  
  // Check if an item is expanded
  function isExpanded(index) {
    const itemId = items[index].id || index;
    return expandedStateFixed.includes(itemId);
  }
  
  // Keyboard navigation
  function handleKeydown(event, index) {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        focusItem(Math.min(index + 1, items.length - 1));
        break;
      case 'ArrowUp':
        event.preventDefault();
        focusItem(Math.max(index - 1, 0));
        break;
      case 'Home':
        event.preventDefault();
        focusItem(0);
        break;
      case 'End':
        event.preventDefault();
        focusItem(items.length - 1);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        toggleItem(index);
        break;
    }
  }
  
  // Focus a specific item by index
  function focusItem(index) {
    if (itemRefs[index]) {
      itemRefs[index].focus();
    }
  }
</script>

<div 
  class="accordion {spacingClasses[spacing] || spacingClasses.normal}"
  role="presentation"
  aria-label={ariaLabel}
  bind:this={accordionElement}
>
  {#each items as item, index}
    {@const isItemExpanded = isExpanded(index)}
    <div 
      class="accordion-item {!flush ? (bordered ? 'border' : 'border-0') : ''}
        {!flush && rounded ? 'rounded-container-token' : ''}
        {variantClasses[variant]?.wrapper || variantClasses.default.wrapper}
        {elevated ? 'shadow-md hover:shadow-lg transition-shadow duration-300' : ''}
        {widthClasses[maxWidth] || widthClasses.full}
        overflow-hidden"
      id={`accordion-section-${itemIds[index]}`}
    >
      <!-- Header -->
      <h3 class="m-0">
        <button
          bind:this={itemRefs[index]}
          class="accordion-header
            {sizeClasses[size]?.header || sizeClasses.default.header}
            {variantClasses[variant]?.header || variantClasses.default.header}"
          id={`accordion-button-${itemIds[index]}`}
          aria-expanded={isItemExpanded}
          aria-controls={`accordion-panel-${itemIds[index]}`}
          on:click={() => toggleItem(index)}
          on:keydown={event => handleKeydown(event, index)}
        >
          <div class="accordion-header-content">
            {#if iconPosition === 'left' && chevronIcon}
              <span 
                class="accordion-icon {isItemExpanded ? 'rotate-90' : 'rotate-0'}"
                aria-hidden="true"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class={sizeClasses[size]?.icon || "w-5 h-5"}>
                  <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
                </svg>
              </span>
            {/if}
            
            <span class="accordion-title">
              {#if item.title}
                {item.title}
              {:else if index === 0}
                <slot name="title-0">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 1}
                <slot name="title-1">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 2}
                <slot name="title-2">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 3}
                <slot name="title-3">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 4}
                <slot name="title-4">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 5}
                <slot name="title-5">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 6}
                <slot name="title-6">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 7}
                <slot name="title-7">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 8}
                <slot name="title-8">
                  Accordion Item {index + 1}
                </slot>
              {:else if index === 9}
                <slot name="title-9">
                  Accordion Item {index + 1}
                </slot>
              {:else}
                Accordion Item {index + 1}
              {/if}
            </span>
            
            {#if iconPosition === 'right' && chevronIcon}
              <span 
                class="accordion-icon {isItemExpanded ? 'rotate-180' : 'rotate-0'}"
                aria-hidden="true"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class={sizeClasses[size]?.icon || "w-5 h-5"}>
                  <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                </svg>
              </span>
            {/if}
          </div>
        </button>
      </h3>
      
      <!-- Content panel -->
      {#if isItemExpanded}
        <div
          id={`accordion-panel-${itemIds[index]}`}
          role="region"
          aria-labelledby={`accordion-button-${itemIds[index]}`}
          class="accordion-content {variantClasses[variant]?.content || variantClasses.default.content}"
          transition:slide={{ duration: 300, easing: cubicOut }}
        >
          <div class="accordion-content-inner {sizeClasses[size]?.content || sizeClasses.default.content}">
            {#if item.content}
              <div class="text-surface-300">{item.content}</div>
            {:else if index === 0}
              <slot name="content-0">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 1}
              <slot name="content-1">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 2}
              <slot name="content-2">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 3}
              <slot name="content-3">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 4}
              <slot name="content-4">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 5}
              <slot name="content-5">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 6}
              <slot name="content-6">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 7}
              <slot name="content-7">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 8}
              <slot name="content-8">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else if index === 9}
              <slot name="content-9">
                <div class="text-surface-300">Content for accordion item {index + 1}</div>
              </slot>
            {:else}
              <div class="text-surface-300">Content for accordion item {index + 1}</div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  {/each}
</div>

<style>
  /* Skeleton-style Accordion */
  .accordion {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
  
  .accordion-item {
    margin-bottom: var(--space-2, 0.5rem);
  }
  
  .accordion-header {
    width: 100%;
    text-align: left;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    outline: none;
    border: none;
    background: transparent;
  }
  
  .accordion-header:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
  
  .accordion-header-content {
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-between; 
  }
  
  .accordion-title {
    flex: 1;
    color: var(--color-surface-50, #f8f9fa);
  }
  
  .accordion-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transform-origin: center;
    transition: transform 0.3s ease-in-out;
    color: var(--color-surface-400, #adb5bd);
    flex-shrink: 0;
    margin-left: var(--space-3, 0.75rem);
    margin-right: var(--space-3, 0.75rem);
  }
  
  /* Left icon positioning */
  .accordion-header-content:has(.accordion-icon:first-child) .accordion-title {
    margin-left: var(--space-3, 0.75rem);
  }
  
  .accordion-content {
    overflow: hidden;
  }
  
  .accordion-content-inner {
    color: var(--color-surface-300, #adb5bd);
    font-size: var(--text-base, 1rem);
    line-height: 1.6;
  }
  
  /* Variants and sizes */
  .rounded-container-token {
    border-radius: var(--rounded-container, 0.5rem);
  }

  /* Shadow and hover effects */
  .shadow-md {
    box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06));
  }
  
  .hover\:shadow-lg:hover {
    box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05));
  }

  /* Spacing utility classes */
  .space-y-1 > * + * {
    margin-top: var(--space-1, 0.25rem);
  }
  
  .space-y-2 > * + * {
    margin-top: var(--space-2, 0.5rem);
  }
  
  .space-y-3 > * + * {
    margin-top: var(--space-3, 0.75rem);
  }
</style>