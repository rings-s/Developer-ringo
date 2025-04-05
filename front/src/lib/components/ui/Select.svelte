<script>
  import { createEventDispatcher, onMount, tick } from 'svelte';
  
  export let id = "";
  export let name = "";
  export let label = "";
  export let options = [];
  export let value = "";
  export let placeholder = "";
  export let disabled = false;
  export let required = false;
  export let error = "";
  export let helpText = "";
  export let size = "md";
  export let variant = "default";
  export let searchable = false;
  export let clearable = false;
  export let multiple = false;
  export let creatable = false;
  export let customItem = false;
  export let loading = false;
  export let borderless = false;
  export let rounded = false;
  export let animate = true;
  export let ariaLabel = "";
  export let ariaLabelledBy = "";
  
  let selectId;
  let selectElement;
  let isOpen = false;
  let focused = false;
  let searchTerm = "";
  let selectedValues = multiple ? (Array.isArray(value) ? [...value] : []) : value;
  let highlightedIndex = -1;
  let optionsContainer;
  let searchInput;
  let listboxVisible = false;
  const dispatch = createEventDispatcher();
  
  // Generate ID if not provided
  $: selectId = id || `select-${Math.random().toString(36).substring(2, 11)}`;
  
  // Error and help IDs for aria-describedby
  $: errorId = error ? `${selectId}-error` : null;
  $: helpId = helpText ? `${selectId}-help` : null;
  
  // Combined aria-describedby with custom, error, and help IDs
  $: ariaDescribedBy = [errorId, helpId].filter(Boolean).join(' ') || null;
  
  onMount(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (selectElement && !selectElement.contains(event.target)) {
        isOpen = false;
        listboxVisible = false;
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
  
  // Size classes
  const sizeClasses = {
    sm: "py-1.5 px-2 text-sm",
    md: "py-2 px-3",
    lg: "py-2.5 px-4 text-lg",
  };
  
  // Variant classes
  const variants = {
    default: "bg-background-800 border-primary-700 focus:border-primary-500",
    filled: "bg-background-600 border-transparent focus:bg-background-700",
    outlined: "bg-transparent border-primary-700 focus:border-primary-500",
    underlined: "bg-transparent border-0 border-b-2 border-primary-700 rounded-none focus:border-primary-500",
  };
  
  // Toggle dropdown
  function toggleDropdown() {
    if (!disabled) {
      isOpen = !isOpen;
      
      if (isOpen) {
        // Reset search term and highlighted index
        searchTerm = "";
        highlightedIndex = -1;
        
        // Focus search input if searchable
        if (searchable) {
          tick().then(() => {
            if (searchInput) {
              searchInput.focus();
              listboxVisible = true;
            }
          });
        } else {
          listboxVisible = true;
        }
      } else {
        // Hide dropdown content
        listboxVisible = false;
      }
      
      dispatch('toggle', { isOpen });
    }
  }
  
  // Handle selection of an option
  function selectOption(option, index) {
    if (multiple) {
      const valueIndex = selectedValues.findIndex(val => val === option.value);
      
      if (valueIndex === -1) {
        selectedValues = [...selectedValues, option.value];
      } else {
        selectedValues = selectedValues.filter(val => val !== option.value);
      }
      
      value = selectedValues;
    } else {
      selectedValues = option.value;
      value = option.value;
      isOpen = false;
      listboxVisible = false;
    }
    
    highlightedIndex = index;
    dispatch('change', { value });
  }
  
  // Clear selection
  function clearSelection(event) {
    event.stopPropagation();
    
    if (multiple) {
      selectedValues = [];
      value = [];
    } else {
      selectedValues = "";
      value = "";
    }
    
    dispatch('change', { value });
  }
  
  // Handle keyboard navigation
  function handleKeydown(event) {
    if (disabled) return;
    
    const filteredOptions = searchable && searchTerm ? 
      options.filter(option => 
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      ) : 
      options;
    
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (!isOpen) {
        toggleDropdown();
      } else {
        highlightedIndex = Math.min(highlightedIndex + 1, filteredOptions.length - 1);
        scrollOptionIntoView();
      }
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (isOpen) {
        highlightedIndex = Math.max(highlightedIndex - 1, 0);
        scrollOptionIntoView();
      }
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (isOpen && highlightedIndex >= 0 && filteredOptions[highlightedIndex]) {
        selectOption(filteredOptions[highlightedIndex], highlightedIndex);
      } else {
        toggleDropdown();
      }
    } else if (event.key === 'Escape') {
      event.preventDefault();
      isOpen = false;
      listboxVisible = false;
    } else if (event.key === 'Tab') {
      isOpen = false;
      listboxVisible = false;
    } else if (!searchable && /^[a-zA-Z0-9]$/.test(event.key)) {
      // Type to select when not in search mode
      const startsWith = filteredOptions.findIndex(option => 
        option.label.toLowerCase().startsWith(event.key.toLowerCase())
      );
      
      if (startsWith !== -1) {
        highlightedIndex = startsWith;
        scrollOptionIntoView();
      }
    }
  }
  
  // Scroll the highlighted option into view
  function scrollOptionIntoView() {
    tick().then(() => {
      if (optionsContainer && optionsContainer.children[highlightedIndex]) {
        optionsContainer.children[highlightedIndex].scrollIntoView({
          block: 'nearest',
          behavior: 'smooth'
        });
      }
    });
  }
  
  // Handle focus events
  function handleFocus() {
    focused = true;
    dispatch('focus');
  }
  
  function handleBlur() {
    focused = false;
    dispatch('blur');
  }
  
  // Check if an option is selected
  function isSelected(optionValue) {
    if (multiple) {
      return selectedValues.includes(optionValue);
    } else {
      return selectedValues === optionValue;
    }
  }
  
  // Create a new option if creatable is true
  function createOption() {
    if (creatable && searchTerm) {
      const newOption = { value: searchTerm, label: searchTerm };
      options = [...options, newOption];
      selectOption(newOption, options.length - 1);
      searchTerm = "";
    }
  }
  
  // Get display value
  $: displayValue = (() => {
    if (multiple) {
      if (selectedValues.length === 0) return "";
      
      if (selectedValues.length === 1) {
        const selectedOption = options.find(opt => opt.value === selectedValues[0]);
        return selectedOption ? selectedOption.label : "";
      } else {
        return `${selectedValues.length} selected`;
      }
    } else {
      const selectedOption = options.find(opt => opt.value === selectedValues);
      return selectedOption ? selectedOption.label : "";
    }
  })();
  
  // Filter options based on search term
  $: filteredOptions = searchable && searchTerm ? 
    options.filter(option => 
      option.label.toLowerCase().includes(searchTerm.toLowerCase())
    ) : 
    options;
  
  // Compute animated label class
  $: floatingLabel = animate && label;
  $: labelClasses = [
    "block text-primary-300 font-medium transition-all duration-200",
    floatingLabel ? "pointer-events-none absolute" : "mb-1",
    floatingLabel && (focused || value) ? "-translate-y-6 scale-75 origin-left" : "",
    error ? "text-danger-500" : "",
    disabled ? "text-primary-400" : "",
  ].join(" ");
  
  // Compute final select wrapper classes
  $: wrapperClasses = [
    "relative",
    "mb-6", // Margin bottom to accommodate floating label & error message
  ].join(" ");
  
  // Compute final select classes
  $: selectClasses = [
    "w-full transition-all duration-200 outline-none appearance-none cursor-pointer",
    sizeClasses[size] || sizeClasses.md,
    !borderless ? "border" : "",
    rounded ? "rounded-lg" : "rounded",
    error ? "border-danger-500 focus:ring-danger-400" : variants[variant] || variants.default,
    "pr-10", // Space for dropdown icon
    disabled ? "bg-background-600/50 text-primary-300 cursor-not-allowed" : "",
    floatingLabel ? "pt-6" : "",
    "focus:ring-4 focus:ring-opacity-30",
    error ? "focus:ring-danger-400" : "focus:ring-primary-400",
    loading ? "animate-pulse" : "",
    $$restProps.class || "",
  ].join(" ");
  
  // Compute custom dropdown classes
  $: dropdownClasses = [
    "absolute z-30 w-full mt-1 overflow-auto bg-background-800 border border-primary-700 shadow-xl",
    rounded ? "rounded-lg" : "rounded",
    "max-h-60",
  ].join(" ");
</script>

<div class={wrapperClasses} bind:this={selectElement}>
  <!-- Label -->
  {#if label}
    <label 
      for={selectId}
      class={labelClasses}
      style={floatingLabel ? "top: 0.75rem; left: 0.75rem;" : ""}
      id={ariaLabelledBy || null}
    >
      {label}
      {#if required}
        <span class="text-danger-400 ml-1">*</span>
      {/if}
    </label>
  {/if}
  
  <div class="relative">
    <!-- Custom dropdown display -->
    {#if customItem || searchable || multiple}
      <div 
        class={selectClasses}
        tabindex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-owns={`${selectId}-listbox`}
        aria-haspopup="listbox"
        aria-disabled={disabled}
        aria-label={ariaLabel || label || null}
        aria-labelledby={ariaLabelledBy || null}
        aria-describedby={ariaDescribedBy || null}
        aria-invalid={error ? "true" : "false"}
        on:click={toggleDropdown}
        on:keydown={handleKeydown}
        on:focus={handleFocus}
        on:blur={handleBlur}
      >
        <!-- Selected items display -->
        <div class="flex flex-wrap gap-1 items-center">
          {#if multiple && Array.isArray(selectedValues) && selectedValues.length > 0}
            {#if !isOpen}
              {#each selectedValues as selectedValue}
                {@const selectedOption = options.find(opt => opt.value === selectedValue)}
                {#if selectedOption}
                  <span class="inline-flex items-center px-2 py-0.5 bg-primary-600 text-background-900 text-sm rounded-full">
                    {selectedOption.label}
                    <button 
                      type="button" 
                      class="ml-1 text-background-900 hover:text-background-700 focus:outline-none" 
                      on:click|stopPropagation={() => {
                        selectedValues = selectedValues.filter(val => val !== selectedValue);
                        value = selectedValues;
                        dispatch('change', { value });
                      }}
                      aria-label={`Remove ${selectedOption.label}`}
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </span>
                {/if}
              {/each}
            {/if}
          {:else if displayValue}
            <span>{displayValue}</span>
          {:else}
            <span class="text-primary-400">{placeholder || "Select an option..."}</span>
          {/if}
        </div>
      </div>
    {:else}
      <!-- Native select for basic use cases -->
      <select
        id={selectId}
        {name}
        bind:value={selectedValues}
        {disabled}
        {required}
        class={selectClasses}
        on:change={event => {
          value = event.target.value;
          dispatch('change', { value });
        }}
        on:focus={handleFocus}
        on:blur={handleBlur}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={ariaDescribedBy || null}
        aria-label={ariaLabel || null}
        aria-labelledby={ariaLabelledBy || null}
        {...$$restProps}
      >
        {#if placeholder}
          <option value="" disabled selected>{placeholder}</option>
        {/if}
        
        {#each options as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    {/if}
    
    <!-- Dropdown icon -->
    <div class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none" aria-hidden="true">
      {#if loading}
        <svg class="animate-spin w-5 h-5 text-primary-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {:else}
        <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      {/if}
    </div>
    
    <!-- Clearable button if value is set -->
    {#if clearable && (multiple ? selectedValues.length > 0 : selectedValues) && !disabled}
      <div class="absolute inset-y-0 right-8 flex items-center">
        <button 
          type="button" 
          class="text-primary-400 hover:text-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full focus:ring-opacity-50 transition-colors"
          on:click={clearSelection}
          aria-label="Clear selection"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    {/if}
    
    <!-- Custom dropdown menu for advanced features -->
    {#if isOpen && listboxVisible && (customItem || searchable || multiple)}
      <div 
        class={dropdownClasses} 
        id={`${selectId}-listbox`} 
        role="listbox"
        aria-multiselectable={multiple}
        aria-activedescendant={highlightedIndex >= 0 ? `${selectId}-option-${highlightedIndex}` : null}
      >
        {#if searchable}
          <div class="sticky top-0 p-2 bg-background-800 border-b border-primary-700">
            <input
              bind:this={searchInput}
              type="text" 
              bind:value={searchTerm}
              placeholder="Search..."
              autocomplete="off"
              class="w-full px-2 py-1 bg-background-700 border border-primary-600 rounded text-primary-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              on:input={() => {
                highlightedIndex = 0;
              }}
              on:keydown={event => {
                // Prevent dropdown from closing when typing
                event.stopPropagation();
              }}
              aria-controls={`${selectId}-listbox`}
            />
          </div>
        {/if}
        
        <div class="py-1" bind:this={optionsContainer}>
          {#each filteredOptions as option, index}
            <div
              id={`${selectId}-option-${index}`}
              role="option"
              aria-selected={isSelected(option.value)}
              class={`px-4 py-2 cursor-pointer transition-colors
                ${highlightedIndex === index ? 'bg-primary-600 text-background-900' : 'hover:bg-primary-700'}
                ${isSelected(option.value) ? 'bg-primary-500/20' : ''}`}
              on:click={() => selectOption(option, index)}
              on:mouseenter={() => highlightedIndex = index}
              on:mouseleave={() => highlightedIndex = -1}
            >
              {#if customItem}
                <slot name="option" option={option} selected={isSelected(option.value)}>
                  <div class="flex items-center">
                    {#if multiple}
                      <input type="checkbox" checked={isSelected(option.value)} class="mr-2" aria-hidden="true" tabindex="-1" />
                    {/if}
                    {option.label}
                  </div>
                </slot>
              {:else}
                <div class="flex items-center">
                  {#if multiple}
                    <div class="flex items-center justify-center w-4 h-4 mr-2 border border-primary-400 rounded">
                      {#if isSelected(option.value)}
                        <svg class="w-3 h-3 text-primary-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                        </svg>
                      {/if}
                    </div>
                  {/if}
                  {option.label}
                </div>
              {/if}
            </div>
          {/each}
          
          {#if filteredOptions.length === 0}
            <div class="px-4 py-2 text-primary-400 text-center">
              {#if creatable && searchTerm}
                <button 
                  class="text-primary-500 hover:underline focus:outline-none"
                  on:click={createOption}
                  type="button"
                >
                  Create "{searchTerm}"
                </button>
              {:else}
                No options found
              {/if}
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Error or Help Text -->
  {#if error}
    <p id={errorId} class="mt-1 text-sm text-danger-500">{error}</p>
  {:else if helpText}
    <p id={helpId} class="mt-1 text-sm text-primary-400">{helpText}</p>
  {/if}
</div>