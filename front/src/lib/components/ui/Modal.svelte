<script>
  import { fade, fly, scale } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  
  export let open = false;
  export let title = "";
  export let size = "md";
  export let closeOnBackdropClick = true;
  export let closeOnEsc = true;
  export let hideCloseButton = false;
  export let position = "center";
  export let animation = "scale";
  export let persistent = false;
  export let rounded = "lg";
  export let fullScreen = false;
  export let contentScrollable = true;
  export let backdrop = true;
  export let closeButton = "×";
  export let preventScroll = true;
  export let ariaLabelledBy = "";
  export let ariaDescribedBy = "";
  export let initialFocus = null; // Element to focus when modal opens
  
  let modalElement;
  let modalContentElement;
  let closeButtonElement;
  let previousBodyStyle = {};
  let previousActiveElement = null;
  const dispatch = createEventDispatcher();

  onMount(() => {
    // Store original body styles to restore later
    previousBodyStyle = {
      overflow: document.body.style.overflow,
      paddingRight: document.body.style.paddingRight
    };
    
    // Store currently focused element to restore focus later
    previousActiveElement = document.activeElement;
  });
  
  onDestroy(() => {
    // Make sure to reset body scroll when component is destroyed
    if (open && preventScroll) {
      resetBodyScroll();
    }
  });
  
  // Watch for open state changes
  $: if (open) {
    if (preventScroll) {
      lockBodyScroll();
    }
    
    // Set focus to the first focusable element or custom focus target
    setTimeout(() => {
      if (initialFocus && initialFocus.focus) {
        initialFocus.focus();
      } else if (closeButtonElement && !hideCloseButton) {
        closeButtonElement.focus();
      } else if (modalContentElement) {
        const focusableElements = modalContentElement.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        } else {
          modalContentElement.focus();
        }
      }
    }, 50);
  } else if (previousActiveElement && preventScroll) {
    resetBodyScroll();
    
    // Return focus to previously focused element when modal closes
    if (previousActiveElement && previousActiveElement.focus) {
      try {
        previousActiveElement.focus();
      } catch (e) {
        console.warn('Failed to restore focus:', e);
      }
    }
  }
  
  // Handle closing the modal
  function close() {
    if (!persistent) {
      open = false;
      dispatch('close');
    } else {
      // If modal is persistent, animate a "shake" effect
      if (modalElement) {
        modalElement.classList.add('modal-shake');
        setTimeout(() => {
          if (modalElement) {
            modalElement.classList.remove('modal-shake');
          }
        }, 600);
      }
    }
  }
  
  // Handle backdrop click
  function onBackdropClick() {
    if (closeOnBackdropClick && !persistent) {
      close();
    }
  }
  
  // Prevent click propagation for modal content
  function onModalClick(e) {
    e.stopPropagation();
  }
  
  // Size classes for the modal dialog
  const sizeClasses = {
    xs: "max-w-xs",
    sm: "max-w-sm",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
    "2xl": "max-w-6xl",
    "3xl": "max-w-7xl",
    full: "max-w-full mx-4",
  };
  
  // Position classes for the modal
  const positionClasses = {
    center: "items-center justify-center",
    top: "items-start justify-center pt-10",
    "top-left": "items-start justify-start p-4",
    "top-right": "items-start justify-end p-4",
    "bottom": "items-end justify-center pb-10",
    "bottom-left": "items-end justify-start p-4",
    "bottom-right": "items-end justify-end p-4",
    "left": "items-center justify-start p-4",
    "right": "items-center justify-end p-4",
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
  
  // Animation transitions
  const animations = {
    scale: {
      in: scale,
      inParams: { 
        duration: 200,
        start: 0.95,
        opacity: 0,
        easing: quintOut
      }
    },
    fly: {
      in: fly,
      inParams: { 
        duration: 200,
        y: 20,
        opacity: 0,
        easing: quintOut
      }
    },
    fade: {
      in: fade,
      inParams: { 
        duration: 200
      }
    },
  };
  
  // Handle escape key press
  function handleKeydown(e) {
    if (open && closeOnEsc && e.key === 'Escape' && !persistent) {
      close();
    }
  }
  
  // Lock body scroll when modal opens
  function lockBodyScroll() {
    // Only if not already locked and browser is available
    if (typeof document !== 'undefined') {
      // Get the scrollbar width
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      
      // Store current body overflow style
      previousBodyStyle = {
        overflow: document.body.style.overflow,
        paddingRight: document.body.style.paddingRight
      };
      
      // Prevent body scrolling
      document.body.style.overflow = 'hidden';
      
      // Add padding equal to scrollbar width to prevent content shifting
      if (scrollbarWidth > 0) {
        document.body.style.paddingRight = `${scrollbarWidth}px`;
      }
    }
  }
  
  // Reset body scroll when modal closes
  function resetBodyScroll() {
    // Only if browser is available
    if (typeof document !== 'undefined') {
      // Restore previous body styles
      document.body.style.overflow = previousBodyStyle.overflow || '';
      document.body.style.paddingRight = previousBodyStyle.paddingRight || '';
    }
  }
  
  // Trap focus inside modal for accessibility
  function trapFocus(e) {
    if (!modalElement || !open) return;
    
    // Find all focusable elements
    const focusableElements = modalElement.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    // If Tab key pressed
    if (e.key === 'Tab') {
      // If Shift+Tab on first element, wrap to last
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
      // If Tab on last element, wrap to first
      else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  }

  // Generate unique ID for ARIA attributes if not provided
  $: modalId = ariaLabelledBy || `modal-${Math.random().toString(36).substring(2, 11)}`;
  $: contentId = ariaDescribedBy || `modal-content-${Math.random().toString(36).substring(2, 11)}`;
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <div 
    class="fixed inset-0 z-50 overflow-y-auto"
    aria-labelledby={title ? modalId : undefined}
    role="dialog"
    aria-modal="true"
    on:keydown={trapFocus}
  >
    <!-- Backdrop -->
    {#if backdrop}
      <div 
        class="fixed inset-0 bg-primary-100 transition-opacity"
        style="backdrop-filter: blur(2px);"
        class:bg-opacity-50={backdrop === true}
        class:bg-opacity-75={backdrop === "dark"}
        class:bg-opacity-25={backdrop === "light"}
        in:fade={{ duration: 150 }}
        out:fade={{ duration: 100 }}
        on:click={onBackdropClick}
        aria-hidden="true"
      ></div>
    {/if}
    
    <!-- Modal container -->
    <div class={`flex min-h-screen ${positionClasses[position] || positionClasses.center}`}>
      <!-- Modal content -->
      <div 
        bind:this={modalElement}
        class={`w-full ${!fullScreen ? sizeClasses[size] || sizeClasses.md : 'max-w-full min-h-screen m-0'} 
                bg-background-800 ${!fullScreen ? roundedClasses[rounded] || roundedClasses.lg : ''} 
                shadow-xl overflow-hidden transform transition-all`}
        in:animations[animation].in={animations[animation].inParams}
        on:click={onModalClick}
      >
        {#if title || $$slots.header}
          <!-- Header -->
          <div class="px-4 py-3 bg-background-700 border-b border-primary-700 flex items-center justify-between">
            <slot name="header">
              {#if title}
                <h3 id={modalId} class="text-lg font-medium text-primary-100">{title}</h3>
              {/if}
            </slot>
            
            {#if !hideCloseButton}
              <button
                bind:this={closeButtonElement}
                type="button"
                class="text-primary-300 hover:text-primary-100 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                on:click={close}
                aria-label="Close"
              >
                {#if typeof closeButton === 'string'}
                  <span class="text-2xl font-medium">{closeButton}</span>
                {:else}
                  {@html closeButton}
                {/if}
              </button>
            {/if}
          </div>
        {/if}
        
        <!-- Body -->
        <div 
          bind:this={modalContentElement}
          id={contentId}
          class={`${contentScrollable ? 'overflow-y-auto' : ''} ${fullScreen ? 'max-h-screen' : 'max-h-[calc(100vh-200px)]'} p-6`}
          tabindex={title ? 0 : -1}
        >
          <slot />
        </div>
        
        {#if $$slots.footer}
          <!-- Footer -->
          <div class="px-4 py-3 bg-background-700 border-t border-primary-700 flex justify-end space-x-2">
            <slot name="footer" />
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
  }
  
  .modal-shake {
    animation: shake 0.6s cubic-bezier(.36,.07,.19,.97) both;
  }
</style>