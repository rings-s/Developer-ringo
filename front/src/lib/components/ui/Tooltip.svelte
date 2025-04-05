<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  
  export let text = "";
  export let position = "top";
  export let trigger = "hover"; // hover, click, focus, manual
  export let arrow = true;
  export let delay = 300; // delay in ms before showing
  export let hideDelay = 100; // delay in ms before hiding
  export let maxWidth = "200px";
  export let theme = "dark"; // dark, light, colored
  export let offset = 8; // distance from the target element
  export let closeOnEsc = true; // close tooltip when escape key is pressed
  export let closeOnClickOutside = true; // close tooltip when clicking outside
  export let visible = false; // for manual control
  export let interactive = false; // allows interaction with tooltip content
  export let placement = "auto"; // auto, fixed
  export let transition = "fade"; // fade, scale, slide
  export let duration = 150; // transition duration in ms
  export let id = ""; // Custom ID for the tooltip
  export let zIndex = 50; // z-index for tooltip
  export let ariaLabel = ""; // Custom aria label
  
  let tooltipVisible = false;
  let tooltipElement;
  let triggerElement;
  let arrowElement;
  let showTimeout;
  let hideTimeout;
  let initialPosition = position;
  let finalPosition = position;
  let observer;
  const dispatch = createEventDispatcher();
  
  // Generate a unique ID if not provided
  const uniqueId = Math.random().toString(36).substring(2, 11);
  $: tooltipId = id || `tooltip-${uniqueId}`;
  
  // Determine if the tooltip is shown based on manual or automatic control
  $: tooltipVisible = trigger === 'manual' ? visible : tooltipVisible;
  
  // Watch for visible prop changes if in manual mode
  $: if (trigger === 'manual') {
    tooltipVisible = visible;
    if (tooltipVisible) {
      onShow();
    } else {
      onHide();
    }
  }
  
  // Position classes
  const positionClasses = {
    top: "bottom-full left-1/2 transform -translate-x-1/2",
    right: "left-full top-1/2 transform -translate-y-1/2",
    bottom: "top-full left-1/2 transform -translate-x-1/2",
    left: "right-full top-1/2 transform -translate-y-1/2",
    "top-start": "bottom-full left-0",
    "top-end": "bottom-full right-0",
    "right-start": "left-full top-0",
    "right-end": "left-full bottom-0",
    "bottom-start": "top-full left-0",
    "bottom-end": "top-full right-0",
    "left-start": "right-full top-0",
    "left-end": "right-full bottom-0",
  };
  
  // Arrow classes
  const arrowClasses = {
    top: "bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full border-t-current border-r-transparent border-b-transparent border-l-transparent",
    right: "left-0 top-1/2 transform -translate-y-1/2 -translate-x-full border-t-transparent border-r-current border-b-transparent border-l-transparent",
    bottom: "top-0 left-1/2 transform -translate-x-1/2 -translate-y-full border-t-transparent border-r-transparent border-b-current border-l-transparent",
    left: "right-0 top-1/2 transform -translate-y-1/2 translate-x-full border-t-transparent border-r-transparent border-b-transparent border-l-current",
    "top-start": "bottom-0 left-4 transform translate-y-full border-t-current border-r-transparent border-b-transparent border-l-transparent",
    "top-end": "bottom-0 right-4 transform translate-y-full border-t-current border-r-transparent border-b-transparent border-l-transparent",
    "right-start": "left-0 top-4 transform -translate-x-full border-t-transparent border-r-current border-b-transparent border-l-transparent",
    "right-end": "left-0 bottom-4 transform -translate-x-full border-t-transparent border-r-current border-b-transparent border-l-transparent",
    "bottom-start": "top-0 left-4 transform -translate-y-full border-t-transparent border-r-transparent border-b-current border-l-transparent",
    "bottom-end": "top-0 right-4 transform -translate-y-full border-t-transparent border-r-transparent border-b-current border-l-transparent",
    "left-start": "right-0 top-4 transform translate-x-full border-t-transparent border-r-transparent border-b-transparent border-l-current",
    "left-end": "right-0 bottom-4 transform translate-x-full border-t-transparent border-r-transparent border-b-transparent border-l-current",
  };
  
  // Theme classes
  const themeClasses = {
    dark: "bg-primary-100 text-background-800",
    light: "bg-background-800 text-primary-100 border border-primary-700",
    colored: "bg-primary-500 text-background-900",
  };
  
  // Transition CSS
  const transitionCSS = {
    fade: {
      entering: "opacity-0",
      entered: "opacity-100 transition-opacity",
      exiting: "opacity-0 transition-opacity",
      duration
    },
    scale: {
      entering: "opacity-0 scale-95",
      entered: "opacity-100 scale-100 transition-all",
      exiting: "opacity-0 scale-95 transition-all",
      duration
    },
    slide: {
      top: {
        entering: "opacity-0 translate-y-2",
        entered: "opacity-100 translate-y-0 transition-all",
        exiting: "opacity-0 translate-y-2 transition-all",
      },
      right: {
        entering: "opacity-0 -translate-x-2",
        entered: "opacity-100 translate-x-0 transition-all",
        exiting: "opacity-0 -translate-x-2 transition-all",
      },
      bottom: {
        entering: "opacity-0 -translate-y-2",
        entered: "opacity-100 translate-y-0 transition-all",
        exiting: "opacity-0 -translate-y-2 transition-all",
      },
      left: {
        entering: "opacity-0 translate-x-2",
        entered: "opacity-100 translate-x-0 transition-all",
        exiting: "opacity-0 translate-x-2 transition-all",
      },
      duration
    }
  };
  
  // Handle showing the tooltip
  function showTooltip() {
    if (showTimeout) clearTimeout(showTimeout);
    if (hideTimeout) clearTimeout(hideTimeout);
    
    showTimeout = setTimeout(() => {
      tooltipVisible = true;
      onShow();
    }, delay);
  }
  
  // Handle hiding the tooltip
  function hideTooltip() {
    if (showTimeout) clearTimeout(showTimeout);
    if (hideTimeout) clearTimeout(hideTimeout);
    
    if (interactive && triggerElement && tooltipElement) {
      // For interactive tooltips, only hide when mouse leaves both trigger and tooltip
      hideTimeout = setTimeout(() => {
        if (!isMouseOverElements()) {
          tooltipVisible = false;
          onHide();
        }
      }, hideDelay);
    } else {
      // Normal hide behavior
      hideTimeout = setTimeout(() => {
        tooltipVisible = false;
        onHide();
      }, hideDelay);
    }
  }
  
  // Check if mouse is over either the trigger or tooltip element
  function isMouseOverElements() {
    const isOverTooltip = document.querySelector(':hover') === tooltipElement;
    const isOverTrigger = document.querySelector(':hover') === triggerElement;
    return isOverTooltip || isOverTrigger;
  }
  
  // Called when tooltip is shown
  function onShow() {
    dispatch('show');
    
    // Position the tooltip after it's visible
    tick().then(() => {
      updatePosition();
      
      // Setup intersection observer to detect when tooltip is out of view
      if (placement === 'auto' && tooltipElement) {
        setupPositionObserver();
      }
    });
  }
  
  // Called when tooltip is hidden
  function onHide() {
    dispatch('hide');
    if (observer) {
      observer.disconnect();
    }
  }
  
  // Click handler
  function handleClick(event) {
    if (trigger === 'click') {
      if (tooltipVisible) {
        hideTooltip();
      } else {
        showTooltip();
      }
    }
  }
  
  // Mouse enter handler
  function handleMouseEnter() {
    if (trigger === 'hover') {
      showTooltip();
    }
  }
  
  // Mouse leave handler
  function handleMouseLeave() {
    if (trigger === 'hover') {
      hideTooltip();
    }
  }
  
  // Focus handler
  function handleFocus() {
    if (trigger === 'focus') {
      showTooltip();
    }
  }
  
  // Blur handler
  function handleBlur() {
    if (trigger === 'focus') {
      hideTooltip();
    }
  }
  
  // Document click handler for closing on outside click
  function handleDocumentClick(event) {
    if (
      closeOnClickOutside &&
      tooltipVisible &&
      triggerElement &&
      tooltipElement &&
      !triggerElement.contains(event.target) &&
      !tooltipElement.contains(event.target)
    ) {
      tooltipVisible = false;
      onHide();
    }
  }
  
  // Keydown handler for ESC key
  function handleKeydown(event) {
    if (closeOnEsc && tooltipVisible && event.key === 'Escape') {
      tooltipVisible = false;
      onHide();
    }
  }
  
  // Update tooltip position
  function updatePosition() {
    if (!tooltipElement || !triggerElement) return;
    
    const triggerRect = triggerElement.getBoundingClientRect();
    const tooltipRect = tooltipElement.getBoundingClientRect();
    
    let offsetDistance = typeof offset === 'number' ? offset : parseInt(offset) || 8;
    
    // Determine final position (for 'auto' placement)
    finalPosition = initialPosition;
    
    if (placement === 'auto') {
      // Check if tooltip would be out of view and adjust position
      const viewportHeight = window.innerHeight;
      const viewportWidth = window.innerWidth;
      
      if (initialPosition === 'top' && triggerRect.top < tooltipRect.height + offsetDistance) {
        finalPosition = 'bottom';
      } else if (initialPosition === 'bottom' && triggerRect.bottom + tooltipRect.height + offsetDistance > viewportHeight) {
        finalPosition = 'top';
      } else if (initialPosition === 'left' && triggerRect.left < tooltipRect.width + offsetDistance) {
        finalPosition = 'right';
      } else if (initialPosition === 'right' && triggerRect.right + tooltipRect.width + offsetDistance > viewportWidth) {
        finalPosition = 'left';
      }
    }
    
    // Apply position
    tooltipElement.style.position = 'fixed';
    tooltipElement.style.zIndex = zIndex;
    
    const positions = {
      top: () => {
        tooltipElement.style.bottom = `${window.innerHeight - triggerRect.top + offsetDistance}px`;
        tooltipElement.style.left = `${triggerRect.left + triggerRect.width / 2}px`;
        tooltipElement.style.transform = 'translateX(-50%)';
      },
      right: () => {
        tooltipElement.style.left = `${triggerRect.right + offsetDistance}px`;
        tooltipElement.style.top = `${triggerRect.top + triggerRect.height / 2}px`;
        tooltipElement.style.transform = 'translateY(-50%)';
      },
      bottom: () => {
        tooltipElement.style.top = `${triggerRect.bottom + offsetDistance}px`;
        tooltipElement.style.left = `${triggerRect.left + triggerRect.width / 2}px`;
        tooltipElement.style.transform = 'translateX(-50%)';
      },
      left: () => {
        tooltipElement.style.right = `${window.innerWidth - triggerRect.left + offsetDistance}px`;
        tooltipElement.style.top = `${triggerRect.top + triggerRect.height / 2}px`;
        tooltipElement.style.transform = 'translateY(-50%)';
      },
      'top-start': () => {
        tooltipElement.style.bottom = `${window.innerHeight - triggerRect.top + offsetDistance}px`;
        tooltipElement.style.left = `${triggerRect.left}px`;
      },
      'top-end': () => {
        tooltipElement.style.bottom = `${window.innerHeight - triggerRect.top + offsetDistance}px`;
        tooltipElement.style.right = `${window.innerWidth - triggerRect.right}px`;
      },
      'right-start': () => {
        tooltipElement.style.left = `${triggerRect.right + offsetDistance}px`;
        tooltipElement.style.top = `${triggerRect.top}px`;
      },
      'right-end': () => {
        tooltipElement.style.left = `${triggerRect.right + offsetDistance}px`;
        tooltipElement.style.bottom = `${window.innerHeight - triggerRect.bottom}px`;
      },
      'bottom-start': () => {
        tooltipElement.style.top = `${triggerRect.bottom + offsetDistance}px`;
        tooltipElement.style.left = `${triggerRect.left}px`;
      },
      'bottom-end': () => {
        tooltipElement.style.top = `${triggerRect.bottom + offsetDistance}px`;
        tooltipElement.style.right = `${window.innerWidth - triggerRect.right}px`;
      },
      'left-start': () => {
        tooltipElement.style.right = `${window.innerWidth - triggerRect.left + offsetDistance}px`;
        tooltipElement.style.top = `${triggerRect.top}px`;
      },
      'left-end': () => {
        tooltipElement.style.right = `${window.innerWidth - triggerRect.left + offsetDistance}px`;
        tooltipElement.style.bottom = `${window.innerHeight - triggerRect.bottom}px`;
      },
    };
    
    // Apply the positioning
    if (positions[finalPosition]) {
      positions[finalPosition]();
    }
    
    // Position the arrow
    if (arrow && arrowElement) {
      // Reset any previous styles
      arrowElement.removeAttribute('style');
      
      // Apply classes based on the final position
      arrowElement.className = `absolute w-0 h-0 border-4 ${arrowClasses[finalPosition] || arrowClasses.top}`;
    }
  }
  
  // Setup intersection observer to detect when tooltip is out of view
  function setupPositionObserver() {
    if (typeof IntersectionObserver === 'undefined' || !tooltipElement) return;
    
    if (observer) {
      observer.disconnect();
    }
    
    observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting) {
          // Tooltip is out of view, try another position
          if (finalPosition === 'top') finalPosition = 'bottom';
          else if (finalPosition === 'bottom') finalPosition = 'top';
          else if (finalPosition === 'left') finalPosition = 'right';
          else if (finalPosition === 'right') finalPosition = 'left';
          
          updatePosition();
        }
      },
      { threshold: 0.5 }
    );
    
    observer.observe(tooltipElement);
  }
  
  // Setup event listeners
  function setupEventListeners() {
    if (trigger === 'click' || closeOnClickOutside) {
      document.addEventListener('click', handleDocumentClick);
    }
    
    if (closeOnEsc) {
      document.addEventListener('keydown', handleKeydown);
    }
    
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);
  }
  
  // Remove event listeners and cleanup
  function cleanupEventListeners() {
    if (trigger === 'click' || closeOnClickOutside) {
      document.removeEventListener('click', handleDocumentClick);
    }
    
    if (closeOnEsc) {
      document.removeEventListener('keydown', handleKeydown);
    }
    
    window.removeEventListener('resize', updatePosition);
    window.removeEventListener('scroll', updatePosition);
    
    if (observer) {
      observer.disconnect();
    }
    
    if (showTimeout) clearTimeout(showTimeout);
    if (hideTimeout) clearTimeout(hideTimeout);
  }
  
  onMount(() => {
    initialPosition = position;
    finalPosition = position;
    
    setupEventListeners();
  });
  
  onDestroy(() => {
    cleanupEventListeners();
  });
</script>

<div 
  bind:this={triggerElement}
  class="inline-block {$$restProps.class || ''}" 
  on:mouseenter={handleMouseEnter}
  on:mouseleave={handleMouseLeave}
  on:focus={handleFocus}
  on:blur={handleBlur}
  on:click={handleClick}
  aria-describedby={tooltipVisible ? tooltipId : null}
>
  <slot />
  
  {#if tooltipVisible && text}
    <div
      bind:this={tooltipElement}
      id={tooltipId}
      class="fixed max-w-[{maxWidth}] px-2 py-1 text-xs font-medium rounded shadow-lg
             {themeClasses[theme] || themeClasses.dark}
             {transition === 'slide' 
                ? transitionCSS.slide[finalPosition?.split('-')[0] || 'top'].entered
                : transitionCSS[transition]?.entered || transitionCSS.fade.entered}
             pointer-events-{interactive ? 'auto' : 'none'}"
      style="transition-duration: {duration}ms; z-index: {zIndex};"
      role="tooltip"
      aria-label={ariaLabel || null}
    >
      {#if typeof text === 'string'}
        {text}
      {:else}
        <slot name="content" />
      {/if}
      
      <!-- Arrow -->
      {#if arrow}
        <div
          bind:this={arrowElement}
          class="absolute w-0 h-0 border-4 {arrowClasses[finalPosition] || arrowClasses.top}"
          aria-hidden="true"
        ></div>
      {/if}
    </div>
  {/if}
</div>