<!-- src/lib/components/ui/Breadcrumbs.svelte -->
<script>
    export let items = [];
    export let separator = "/";
    export let maxItems = 0; // 0 = show all, > 0 = max items to show
    export let collapseBehavior = "middle"; // middle, start, end
    export let homeIcon = null;
    export let variant = "primary";
    export let size = "md";
    export let underline = false;
    export let separatorClass = "";
    export let ariaLabel = "Breadcrumbs";
    
    // Size classes
    const sizeClasses = {
      sm: "text-xs",
      md: "text-sm",
      lg: "text-base",
      xl: "text-lg"
    };
    
    // Link variant classes
    const variantClasses = {
      primary: {
        active: "text-primary-100 font-medium",
        inactive: "text-primary-400 hover:text-primary-300"
      },
      secondary: {
        active: "text-secondary-400 font-medium",
        inactive: "text-primary-400 hover:text-secondary-500"
      },
      accent: {
        active: "text-accent-400 font-medium",
        inactive: "text-primary-400 hover:text-accent-500"
      },
      light: {
        active: "text-background-900 font-medium",
        inactive: "text-background-700 hover:text-background-800"
      }
    };
    
    // Process items to handle collapsed breadcrumbs
    $: processedItems = (() => {
      if (!maxItems || items.length <= maxItems) {
        return items;
      }
      
      const ellipsis = { label: '...', href: null, disabled: true, isEllipsis: true };
      
      if (collapseBehavior === 'middle') {
        // Show first, last and some middle items
        const startCount = Math.ceil(maxItems / 2);
        const endCount = Math.floor(maxItems / 2);
        
        return [
          ...items.slice(0, startCount),
          ellipsis,
          ...items.slice(items.length - endCount)
        ];
      } else if (collapseBehavior === 'start') {
        // Show ellipsis at start and more items at end
        return [
          items[0],
          ellipsis,
          ...items.slice(-(maxItems - 1))
        ];
      } else if (collapseBehavior === 'end') {
        // Show more items at start and ellipsis at end
        return [
          ...items.slice(0, maxItems - 1),
          ellipsis,
          items[items.length - 1]
        ];
      }
      
      return items;
    })();
    
    // Generate a unique ID for each breadcrumb item for accessibility
    $: breadcrumbId = `breadcrumb-${Math.random().toString(36).substring(2, 9)}`;
  </script>
  
  <nav aria-label={ariaLabel}>
    <ol 
      class="flex flex-wrap items-center space-x-2 {sizeClasses[size] || sizeClasses.md}"
      aria-labelledby={breadcrumbId}
    >
      {#each processedItems as item, index}
        <li class="flex items-center">
          {#if index > 0}
            <span 
              class="mx-2 select-none text-primary-500 {separatorClass}" 
              aria-hidden="true"
            >
              {separator}
            </span>
          {/if}
          
          {#if item.href && !item.disabled && !item.isEllipsis}
            <!-- Link item -->
            <a 
              href={item.href} 
              class={`
                transition-colors duration-200
                ${index === processedItems.length - 1 
                  ? variantClasses[variant]?.active || variantClasses.primary.active 
                  : variantClasses[variant]?.inactive || variantClasses.primary.inactive}
                ${underline ? 'hover:underline' : ''}
                ${item.class || ''}
              `}
              aria-current={index === processedItems.length - 1 ? "page" : null}
              {...item.attributes || {}}
            >
              {#if index === 0 && homeIcon}
                <span aria-hidden="true" class="mr-1">{@html homeIcon}</span>
              {/if}
              {item.label}
            </a>
          {:else}
            <!-- Text item or disabled link -->
            <span 
              class={`
                ${item.isEllipsis ? 'text-primary-400' : ''}
                ${index === processedItems.length - 1 
                  ? variantClasses[variant]?.active || variantClasses.primary.active 
                  : 'text-primary-400'}
                ${item.disabled ? 'opacity-70 cursor-not-allowed' : ''}
                ${item.class || ''}
              `}
              aria-current={index === processedItems.length - 1 ? "page" : null}
              {...item.attributes || {}}
            >
              {#if index === 0 && homeIcon}
                <span aria-hidden="true" class="mr-1">{@html homeIcon}</span>
              {/if}
              {item.label}
            </span>
          {/if}
        </li>
      {/each}
    </ol>
  </nav>