<!-- src/lib/components/ui/Pagination.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    
    export let totalItems = 0;
    export let itemsPerPage = 10;
    export let currentPage = 1;
    export let siblingCount = 1;
    export let showArrows = true;
    export let showEllipsis = true;
    export let showFirstLast = false;
    export let variant = "default";
    export let size = "md";
    export let rounded = true;
    export let totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
    export let ariaLabel = "Pagination";
    
    const dispatch = createEventDispatcher();
    
    // Size classes
    const sizeClasses = {
      sm: "h-7 w-7 text-xs",
      md: "h-9 w-9 text-sm",
      lg: "h-11 w-11 text-base",
    };
    
    // Variant classes
    const variantClasses = {
      default: {
        active: "bg-primary-500 text-background-900 border-primary-500",
        inactive: "bg-background-800 text-primary-300 border-primary-700 hover:bg-primary-700/20",
        disabled: "bg-background-700 text-primary-500 border-primary-800 opacity-50 cursor-not-allowed"
      },
      outline: {
        active: "bg-transparent text-primary-500 border-primary-500",
        inactive: "bg-transparent text-primary-300 border-primary-700 hover:text-primary-500",
        disabled: "bg-transparent text-primary-500 border-primary-800 opacity-50 cursor-not-allowed"
      },
      solid: {
        active: "bg-primary-500 text-background-900 border-primary-500",
        inactive: "bg-primary-700 text-primary-200 border-primary-700 hover:bg-primary-600",
        disabled: "bg-primary-800 text-primary-500 border-primary-800 opacity-50 cursor-not-allowed"
      }
    };
    
    // Generate pagination range
    $: paginationRange = generatePaginationRange(totalPages, currentPage, siblingCount);
    
    function generatePaginationRange(totalPages, currentPage, siblingCount) {
      // Ensure currentPage is within bounds
      const current = Math.max(1, Math.min(currentPage, totalPages));
      
      // Calculate range bounds
      const leftSiblingIndex = Math.max(current - siblingCount, 1);
      const rightSiblingIndex = Math.min(current + siblingCount, totalPages);
      
      // Determine if we should show ellipsis
      const shouldShowLeftDots = leftSiblingIndex > 2;
      const shouldShowRightDots = rightSiblingIndex < totalPages - 1;
      
      // Always include first and last pages
      const firstPageIndex = 1;
      const lastPageIndex = totalPages;
      
      // Basic case: no ellipsis needed
      if (!showEllipsis || totalPages <= siblingCount * 2 + 3) {
        return Array.from({ length: totalPages }, (_, i) => i + 1);
      }
      
      // Case: left ellipsis only
      if (!shouldShowLeftDots && shouldShowRightDots) {
        const leftItemCount = 3 + 2 * siblingCount;
        const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
        
        return [...leftRange, 'DOTS', lastPageIndex];
      }
      
      // Case: right ellipsis only
      if (shouldShowLeftDots && !shouldShowRightDots) {
        const rightItemCount = 3 + 2 * siblingCount;
        const rightRange = Array.from(
          { length: rightItemCount },
          (_, i) => totalPages - rightItemCount + i + 1
        );
        
        return [firstPageIndex, 'DOTS', ...rightRange];
      }
      
      // Case: both ellipses
      if (shouldShowLeftDots && shouldShowRightDots) {
        const middleRange = Array.from(
          { length: rightSiblingIndex - leftSiblingIndex + 1 },
          (_, i) => leftSiblingIndex + i
        );
        
        return [firstPageIndex, 'DOTS', ...middleRange, 'DOTS', lastPageIndex];
      }
    }
    
    // Change page handler
    function changePage(page) {
      if (page !== currentPage && page >= 1 && page <= totalPages) {
        currentPage = page;
        dispatch('change', { page, totalPages });
      }
    }
    
    // Check if a button is the active page
    function isActive(page) {
      return page === currentPage;
    }
    
    // Check if a button should be disabled
    function isDisabled(page) {
      return page < 1 || page > totalPages;
    }
    
    // Button classes based on state and variant
    function getButtonClass(page) {
      if (typeof page === 'number') {
        if (isActive(page)) {
          return variantClasses[variant]?.active || variantClasses.default.active;
        } else {
          return variantClasses[variant]?.inactive || variantClasses.default.inactive;
        }
      } else if (isDisabled(page)) {
        return variantClasses[variant]?.disabled || variantClasses.default.disabled;
      } else {
        return variantClasses[variant]?.inactive || variantClasses.default.inactive;
      }
    }
  </script>
  
  <nav aria-label={ariaLabel} class="flex justify-center" role="navigation">
    <ul class="inline-flex list-none p-0 m-0 items-center">
      {#if showFirstLast}
        <!-- First page button -->
        <li>
          <button
            type="button"
            class={`
              flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
              border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500
              mr-1
              ${rounded ? 'rounded-lg' : ''}
              ${isDisabled(1) ? variantClasses[variant]?.disabled || variantClasses.default.disabled : variantClasses[variant]?.inactive || variantClasses.default.inactive}
            `}
            aria-label="Go to first page"
            disabled={isDisabled(1) || currentPage === 1}
            on:click={() => changePage(1)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M15.79 14.77a.75.75 0 01-1.06.02l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 111.04 1.08L11.832 10l3.938 3.71a.75.75 0 01.02 1.06zm-6 0a.75.75 0 01-1.06.02l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 111.04 1.08L5.832 10l3.938 3.71a.75.75 0 01.02 1.06z" clip-rule="evenodd" />
            </svg>
          </button>
        </li>
      {/if}
      
      {#if showArrows}
        <!-- Previous page button -->
        <li>
          <button
            type="button"
            class={`
              flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
              border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500
              mr-1
              ${rounded ? 'rounded-lg' : ''}
              ${isDisabled(currentPage - 1) ? variantClasses[variant]?.disabled || variantClasses.default.disabled : variantClasses[variant]?.inactive || variantClasses.default.inactive}
            `}
            aria-label="Go to previous page"
            disabled={isDisabled(currentPage - 1)}
            on:click={() => changePage(currentPage - 1)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
            </svg>
          </button>
        </li>
      {/if}
      
      <!-- Page buttons -->
      {#each paginationRange as page, i}
        <li>
          {#if page === 'DOTS'}
            <span 
              class={`
                flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
                mx-1 text-primary-400
              `}
              aria-hidden="true"
            >
              ...
            </span>
          {:else}
            <button
              type="button"
              class={`
                flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
                border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500
                mx-1
                ${rounded ? 'rounded-lg' : ''}
                ${getButtonClass(page)}
              `}
              aria-label={`Go to page ${page}`}
              aria-current={isActive(page) ? 'page' : undefined}
              on:click={() => changePage(page)}
            >
              {page}
            </button>
          {/if}
        </li>
      {/each}
      
      {#if showArrows}
        <!-- Next page button -->
        <li>
          <button
            type="button"
            class={`
              flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
              border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500
              ml-1
              ${rounded ? 'rounded-lg' : ''}
              ${isDisabled(currentPage + 1) ? variantClasses[variant]?.disabled || variantClasses.default.disabled : variantClasses[variant]?.inactive || variantClasses.default.inactive}
            `}
            aria-label="Go to next page"
            disabled={isDisabled(currentPage + 1)}
            on:click={() => changePage(currentPage + 1)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
            </svg>
          </button>
        </li>
      {/if}
      
      {#if showFirstLast}
        <!-- Last page button -->
        <li>
          <button
            type="button"
            class={`
              flex items-center justify-center ${sizeClasses[size] || sizeClasses.md}
              border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500
              ml-1
              ${rounded ? 'rounded-lg' : ''}
              ${isDisabled(totalPages) || currentPage === totalPages ? variantClasses[variant]?.disabled || variantClasses.default.disabled : variantClasses[variant]?.inactive || variantClasses.default.inactive}
            `}
            aria-label="Go to last page"
            disabled={isDisabled(totalPages) || currentPage === totalPages}
            on:click={() => changePage(totalPages)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M10.21 14.77a.75.75 0 01.02-1.06L14.168 10 10.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              <path fill-rule="evenodd" d="M4.21 14.77a.75.75 0 01.02-1.06L8.168 10 4.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
            </svg>
          </button>
        </li>
      {/if}
    </ul>
  </nav>