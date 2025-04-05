<script>
  import { createEventDispatcher, onMount, tick, onDestroy } from 'svelte';
  import { slide, fade } from 'svelte/transition';
  
  export let tabs = [];
  export let activeTab = tabs.length > 0 ? tabs[0]?.id : null;
  export let variant = "line";
  export let size = "md";
  export let fullWidth = false;
  export let vertical = false;
  export let alignTabs = "start";
  export let rounded = "md";
  export let animated = true;
  export let scrollable = false;
  export let iconPosition = "left"; // left, top, right
  export let stacked = false;
  export let ariaLabel = "Tab navigation";
  export let id = "";
  
  let tabsRef;
  let tabsContainerRef;
  let indicatorStyle = "";
  let activeTabElement;
  let isScrolling = false;
  let scrollTimeout;
  let resizeObserver;
  let tabRefs = [];
  const dispatch = createEventDispatcher();
  
  // Generate a unique ID for accessibility with fallback for server-side rendering
  $: panelBaseId = id || `tabs-${Math.random().toString(36).substring(2, 9)}`;
  
  // Variant classes with Skeleton styling
  const variantClasses = {
    line: {
      tablist: "border-b border-surface-700",
      tab: "border-b-2 border-transparent",
      activeTab: "border-primary-500 text-primary-400",
      inactiveTab: "text-surface-300 hover:text-surface-100 hover:border-surface-700",
    },
    pill: {
      tablist: "",
      tab: "rounded-token",
      activeTab: "bg-primary-500 text-surface-900",
      inactiveTab: "text-surface-300 hover:text-surface-100 hover:bg-surface-700 hover:bg-opacity-20",
    },
    card: {
      tablist: "border-b border-surface-700",
      tab: "rounded-tl-token rounded-tr-token border border-transparent border-b-0",
      activeTab: "bg-surface-800 border-surface-700 text-surface-100",
      inactiveTab: "text-surface-300 hover:text-surface-100 hover:bg-surface-700 hover:bg-opacity-20",
    },
    button: {
      tablist: "bg-surface-700 bg-opacity-20 p-1.5 rounded-token", // Increased padding
      tab: "rounded-token",
      activeTab: "bg-primary-500 text-surface-900 shadow-sm",
      inactiveTab: "text-surface-300 hover:text-surface-100",
    },
    none: {
      tablist: "",
      tab: "",
      activeTab: "text-primary-500",
      inactiveTab: "text-surface-300 hover:text-surface-100",
    },
  };
  
  // Size classes - improved padding with consistent Skeleton spacing
  const sizeClasses = {
    sm: "py-2 px-3 text-sm",
    md: "py-2.5 px-4 text-base", 
    lg: "py-3 px-5 text-lg",
  };
  
  // Convert alignment string to class
  const alignmentClasses = {
    start: "justify-start",
    center: "justify-center",
    end: "justify-end",
    between: "justify-between",
    around: "justify-around",
    evenly: "justify-evenly",
  };
  
  // Rounded corner classes to match Skeleton's design tokens
  const roundedClasses = {
    none: "rounded-none",
    sm: "rounded-sm",
    md: "rounded-md",
    lg: "rounded-lg",
    xl: "rounded-xl",
    full: "rounded-full",
  };
  
  // Initialize tabRefs array
  $: {
    tabRefs = Array(tabs.length).fill(null);
  }
  
  // Update activeTabElement when activeTab changes
  $: {
    if (tabRefs.length > 0) {
      const activeIndex = tabs.findIndex(tab => tab.id === activeTab);
      if (activeIndex >= 0) {
        activeTabElement = tabRefs[activeIndex];
        tick().then(updatePosition);
      }
    }
  }
  
  // Update the active tab indicator position
  function updatePosition() {
    if (variant !== 'line' || !tabsRef || !activeTabElement) return;
    
    // Get the active tab element's position within the tabs container
    const tabRect = activeTabElement.getBoundingClientRect();
    const tabsRect = tabsRef.getBoundingClientRect();
    
    if (vertical) {
      // For vertical tabs, set indicator height and top position
      const top = activeTabElement.offsetTop;
      const height = tabRect.height;
      indicatorStyle = `top: ${top}px; height: ${height}px; width: 3px; left: 0;`; // Wider indicator
    } else {
      // For horizontal tabs, set indicator width and left position
      const left = activeTabElement.offsetLeft;
      const width = tabRect.width;
      indicatorStyle = `left: ${left}px; width: ${width}px; height: 3px; bottom: 0;`; // Thicker indicator
    }
  }
  
  // Handle tab selection
  function selectTab(tabId, index) {
    activeTab = tabId;
    dispatch('change', { tabId, index });
    
    // Update active tab indicator after DOM update
    tick().then(() => {
      updatePosition();
      
      // If scrollable, ensure the selected tab is visible
      if (scrollable && tabsContainerRef) {
        const selectedTab = tabsContainerRef.children[index];
        if (selectedTab) {
          const containerRect = tabsContainerRef.getBoundingClientRect();
          const tabRect = selectedTab.getBoundingClientRect();
          
          if (vertical) {
            // For vertical scrolling
            if (tabRect.top < containerRect.top) {
              tabsContainerRef.scrollTop -= (containerRect.top - tabRect.top);
            } else if (tabRect.bottom > containerRect.bottom) {
              tabsContainerRef.scrollTop += (tabRect.bottom - containerRect.bottom);
            }
          } else {
            // For horizontal scrolling
            if (tabRect.left < containerRect.left) {
              tabsContainerRef.scrollLeft -= (containerRect.left - tabRect.left);
            } else if (tabRect.right > containerRect.right) {
              tabsContainerRef.scrollLeft += (tabRect.right - containerRect.right);
            }
          }
        }
      }
    });
  }
  
  // Handle keyboard navigation
  function handleKeydown(event, index) {
    if (event.key === 'ArrowRight' || (vertical && event.key === 'ArrowDown')) {
      // Move to next tab
      event.preventDefault();
      const nextIndex = (index + 1) % tabs.length;
      selectTab(tabs[nextIndex].id, nextIndex);
    } else if (event.key === 'ArrowLeft' || (vertical && event.key === 'ArrowUp')) {
      // Move to previous tab
      event.preventDefault();
      const prevIndex = (index - 1 + tabs.length) % tabs.length;
      selectTab(tabs[prevIndex].id, prevIndex);
    } else if (event.key === 'Home') {
      // Move to first tab
      event.preventDefault();
      selectTab(tabs[0].id, 0);
    } else if (event.key === 'End') {
      // Move to last tab
      event.preventDefault();
      selectTab(tabs[tabs.length - 1].id, tabs.length - 1);
    }
  }
  
  // Debounced scroll handler for shadow indicators
  function handleScroll() {
    if (isScrolling) {
      clearTimeout(scrollTimeout);
    } else {
      isScrolling = true;
    }
    
    // Set a timeout to stop the scrolling state
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
    }, 100);
  }
  
  // Setup resize observer to handle window/layout changes
  function setupResizeObserver() {
    if (typeof window === 'undefined' || !tabsRef) return;
    
    if (resizeObserver) {
      resizeObserver.disconnect();
    }
    
    try {
      if (typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(() => {
          updatePosition();
        });
        
        resizeObserver.observe(tabsRef);
      } else {
        // Fallback for browsers without ResizeObserver
        window.addEventListener('resize', updatePosition);
      }
    } catch (error) {
      console.warn('ResizeObserver error:', error);
      // Fallback
      window.addEventListener('resize', updatePosition);
    }
  }
  
  onMount(() => {
    // Initial indicator update
    updatePosition();
    
    // Setup resize observer
    setupResizeObserver();
    
    return () => {
      // Cleanup
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', updatePosition);
      }
    };
  });
  
  onDestroy(() => {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    if (resizeObserver) {
      resizeObserver.disconnect();
    }
  });
  
  // Compute tablist classes
  $: tablistClasses = [
    vertical ? "tabs-list-vertical" : "tabs-list",
    vertical ? "" : alignmentClasses[alignTabs] || alignmentClasses.start,
    variantClasses[variant]?.tablist || variantClasses.line.tablist,
    scrollable ? (vertical ? "overflow-y-auto" : "overflow-x-auto") : "",
    scrollable ? "relative scrollbar-thin scrollbar-thumb-primary-500 scrollbar-track-transparent" : "",
    $$restProps.class || "",
  ].filter(Boolean).join(" ");
  
  // Compute content wrapper classes - improved spacing
  $: contentClasses = [
    "tab-content",
    animated ? "transition-all duration-200" : "",
  ].filter(Boolean).join(" ");
  
  // Compute tab classes to match design tokens
  $: getTabClasses = (isActive, index) => [
    "tab",
    sizeClasses[size] || sizeClasses.md,
    variant === 'pill' ? roundedClasses.full : roundedClasses[rounded] || roundedClasses.md,
    variantClasses[variant]?.tab || variantClasses.line.tab,
    isActive 
      ? variantClasses[variant]?.activeTab || variantClasses.line.activeTab 
      : variantClasses[variant]?.inactiveTab || variantClasses.line.inactiveTab,
    stacked || iconPosition === 'top' ? 'tab-stacked' : 'tab-inline',
    fullWidth && !vertical ? 'flex-1' : '',
    index > 0 && !vertical ? 'ml-1.5' : '',
    index > 0 && vertical ? 'mt-1.5' : '',
  ].filter(Boolean).join(" ");
</script>

<div class="tabs {vertical ? 'tabs-vertical' : ''}" aria-label={ariaLabel} id={`${panelBaseId}-wrapper`}>
  <!-- Tab header container -->
  <div 
    bind:this={tabsRef}
    class="tabs-container {vertical ? 'tabs-container-vertical' : ''} {vertical && scrollable ? 'max-h-96' : ''}"
    role="tablist"
    aria-orientation={vertical ? "vertical" : "horizontal"}
    id={`${panelBaseId}-tablist`}
  >
    <!-- Shadow indicators if scrollable -->
    {#if scrollable && !vertical}
      <div class="relative">
        <div 
          class="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-surface-500 to-transparent pointer-events-none transition-opacity duration-200"
          class:opacity-0={!isScrolling || tabsContainerRef?.scrollLeft === 0}
          class:opacity-100={isScrolling && tabsContainerRef?.scrollLeft > 0}
          aria-hidden="true"
        ></div>
        
        <div 
          class="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-surface-500 to-transparent pointer-events-none transition-opacity duration-200"
          class:opacity-0={!isScrolling || (tabsContainerRef && tabsContainerRef.scrollLeft + tabsContainerRef.clientWidth >= tabsContainerRef.scrollWidth)}
          class:opacity-100={isScrolling && tabsContainerRef && tabsContainerRef.scrollLeft + tabsContainerRef.clientWidth < tabsContainerRef.scrollWidth}
          aria-hidden="true"
        ></div>
      </div>
    {/if}
    
    <!-- Tabs navigation -->
    <div 
      bind:this={tabsContainerRef}
      class={tablistClasses}
      on:scroll={scrollable ? handleScroll : null}
    >
      {#each tabs as tab, index}
        {@const isActive = activeTab === tab.id}
        <button
          id={`tab-${panelBaseId}-${tab.id}`}
          role="tab"
          aria-selected={isActive}
          aria-controls={`panel-${panelBaseId}-${tab.id}`}
          tabindex={isActive ? 0 : -1}
          class={getTabClasses(isActive, index)}
          on:click={() => selectTab(tab.id, index)}
          on:keydown={event => handleKeydown(event, index)}
          bind:this={tabRefs[index]}
        >
          {#if tab.icon && (iconPosition === 'left' || iconPosition === 'top')}
            <span class="tab-icon {iconPosition === 'top' ? 'mb-1.5' : 'mr-2.5'} {stacked ? 'mb-1.5' : ''}" aria-hidden="true">
              {@html tab.icon}
            </span>
          {/if}
          
          <span class="tab-label">{tab.label}</span>
          
          {#if tab.icon && iconPosition === 'right'}
            <span class="tab-icon ml-2.5" aria-hidden="true">
              {@html tab.icon}
            </span>
          {/if}
          
          {#if tab.badge}
            <span class="tab-badge {iconPosition === 'right' ? 'ml-2.5' : 'ml-2.5'} {isActive ? 'badge-active' : 'badge-inactive'}">
              {tab.badge}
              <span class="sr-only">Items</span>
            </span>
          {/if}
        </button>
      {/each}
      
      <!-- Active tab indicator for line variant -->
      {#if variant === 'line' && activeTabElement}
        <div 
          class="indicator"
          style={indicatorStyle}
          aria-hidden="true"
        ></div>
      {/if}
    </div>
  </div>
  
  <!-- Tab content panels -->
  <div class="panels {vertical ? 'panels-vertical' : ''}">
    {#each tabs as tab, index}
      {#if activeTab === tab.id}
        <div 
          id={`panel-${panelBaseId}-${tab.id}`}
          role="tabpanel"
          aria-labelledby={`tab-${panelBaseId}-${tab.id}`}
          tabindex="0"
          class={contentClasses}
          in:fade={{ duration: animated ? 150 : 0 }}
        >
          <!-- Use indexed slots as a fallback mechanism -->
          {#if index === 0}
            <slot name="tab-0">
              <slot name="content-0">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 1}
            <slot name="tab-1">
              <slot name="content-1">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 2}
            <slot name="tab-2">
              <slot name="content-2">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 3}
            <slot name="tab-3">
              <slot name="content-3">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 4}
            <slot name="tab-4">
              <slot name="content-4">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 5}
            <slot name="tab-5">
              <slot name="content-5">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 6}
            <slot name="tab-6">
              <slot name="content-6">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 7}
            <slot name="tab-7">
              <slot name="content-7">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 8}
            <slot name="tab-8">
              <slot name="content-8">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else if index === 9}
            <slot name="tab-9">
              <slot name="content-9">
                <p class="text-surface-300">Content for {tab.label}</p>
              </slot>
            </slot>
          {:else}
            <slot name="tab-extra">
              <p class="text-surface-300">Content for {tab.label}</p>
            </slot>
          {/if}
        </div>
      {/if}
    {/each}
  </div>
</div>

<style>
  /* Skeleton-style Tabs Component */
  .tabs {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: var(--space-6, 1.5rem);
  }
  
  .tabs-vertical {
    flex-direction: row;
  }
  
  .tabs-container {
    position: relative;
    width: 100%;
  }
  
  .tabs-container-vertical {
    flex-shrink: 0;
    padding-right: var(--space-5, 1.25rem);
  }
  
  /* Tabs list */
  .tabs-list {
    display: flex;
    flex-wrap: nowrap;
    position: relative;
  }
  
  .tabs-list-vertical {
    display: flex;
    flex-direction: column;
    position: relative;
  }
  
  /* Tab button */
  .tab {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    white-space: nowrap;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    outline: none;
  }
  
  .tab:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }
  
  .tab-inline {
    flex-direction: row;
    align-items: center;
  }
  
  .tab-stacked {
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .tab-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  
  .tab-label {
    display: inline-block;
  }
  
  .tab-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    min-width: 1.5rem;
    height: 1.5rem;
  }
  
  .badge-active {
    background-color: var(--color-surface-200);
    color: var(--color-surface-800);
  }
  
  .badge-inactive {
    background-color: var(--color-surface-700);
    color: var(--color-surface-100);
  }
  
  /* Active tab indicator */
  .indicator {
    position: absolute;
    background-color: var(--color-primary-500);
    transition: all 0.3s ease-in-out;
    z-index: 1;
  }
  
  /* Tab panels */
  .panels {
    flex: 1;
    margin-top: var(--space-4, 1rem);
    min-width: 0;
  }
  
  .panels-vertical {
    padding-left: var(--space-5, 1.25rem);
    border-left: 1px solid var(--color-surface-700, #495057);
  }
  
  .tab-content {
    padding: var(--space-5, 1.25rem) 0;
  }
  
  /* Utility classes */
  .overflow-x-auto {
    overflow-x: auto;
  }
  
  .overflow-y-auto {
    overflow-y: auto;
  }
  
  /* Scrollbar styling for smooth scrolling */
  .scrollbar-thin {
    scrollbar-width: thin;
  }
  
  .scrollbar-thumb-primary-500::-webkit-scrollbar-thumb {
    background-color: var(--color-primary-500);
  }
  
  .scrollbar-track-transparent::-webkit-scrollbar-track {
    background-color: transparent;
  }
  
  /* Rounded classes */
  .rounded-md {
    border-radius: 0.375rem;
  }
  
  .rounded-lg {
    border-radius: 0.5rem;
  }
  
  .rounded-full {
    border-radius: 9999px;
  }
  
  .rounded-token {
    border-radius: var(--rounded-token, 0.5rem);
  }
  
  /* Utility border and spacing classes */
  .border-b {
    border-bottom-width: 1px;
    border-bottom-style: solid;
  }
  
  .border-b-2 {
    border-bottom-width: 2px;
    border-bottom-style: solid;
  }
  
  .border-transparent {
    border-color: transparent;
  }
  
  .border-surface-700 {
    border-color: var(--color-surface-700);
  }
  
  /* Responsive styling adjustment */
  @media (max-width: 768px) {
    .tabs-vertical {
      flex-direction: column;
    }
    
    .tabs-container-vertical {
      padding-right: 0;
    }
    
    .panels-vertical {
      padding-left: 0;
      border-left: none;
      margin-top: var(--space-4, 1rem);
    }
  }
</style>