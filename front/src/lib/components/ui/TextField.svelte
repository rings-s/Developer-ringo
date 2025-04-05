<!-- src/lib/components/ui/TextField.svelte -->
<script>
  import { createEventDispatcher, onMount, tick } from 'svelte';
  
  export let type = "text";
  export let id = "";
  export let name = "";
  export let label = "";
  export let value = "";
  export let placeholder = "";
  export let disabled = false;
  export let readonly = false;
  export let required = false;
  export let error = "";
  export let helpText = "";
  export let variant = "default"; // default, filled, outlined, underlined
  export let size = "md";
  export let icon = null;
  export let iconPosition = "left";
  export let trailingIcon = null;
  export let autocomplete = "";
  export let clearable = false;
  export let maxlength = null;
  export let loading = false;
  export let borderless = false;
  export let rounded = false;
  export let showCounter = false;
  export let animate = true;
  export let ariaLabel = "";
  export let ariaDescribedBy = "";
  
  let inputElement;
  let focused = false;
  let isDirty = false;
  let isTouched = false;
  let debounceTimeout;
  let caretPosition = 0;
  const dispatch = createEventDispatcher();
  
  // Generate an ID if none provided
  $: uniqueId = id || `text-field-${Math.random().toString(36).substring(2, 11)}`;
  
  // Error and help IDs for aria-describedby
  $: errorId = error ? `${uniqueId}-error` : null;
  $: helpId = helpText ? `${uniqueId}-help` : null;
  
  // Combined aria-describedby with custom, error, and help IDs
  $: finalAriaDescribedBy = [ariaDescribedBy, errorId, helpId].filter(Boolean).join(' ') || null;
  
  onMount(() => {
    // Clean up any timeouts on unmount
    return () => {
      if (debounceTimeout) clearTimeout(debounceTimeout);
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
  
  // Handle focus events
  function handleFocus(event) {
    focused = true;
    isTouched = true;
    dispatch('focus', event);
  }
  
  function handleBlur(event) {
    focused = false;
    dispatch('blur', event);
  }
  
  // Handle input with debounce for performance
  function handleInput(event) {
    // Save current caret position
    caretPosition = event.target.selectionStart;
    
    // Mark as dirty on first input
    if (!isDirty) isDirty = true;
    
    // Debounce dispatching changes
    if (debounceTimeout) clearTimeout(debounceTimeout);
    
    // Immediately update the value
    value = event.target.value;
    
    // Debounce dispatching the event for better performance
    debounceTimeout = setTimeout(() => {
      dispatch('input', { target: inputElement, value });
      
      // Restore caret position if needed
      if (document.activeElement === inputElement) {
        inputElement.setSelectionRange(caretPosition, caretPosition);
      }
    }, 10);
  }
  
  // Clear the input
  function clearInput() {
    value = "";
    isDirty = true;
    
    // Focus the input after clearing
    tick().then(() => {
      inputElement.focus();
      // Dispatch event after clearing
      dispatch('input', { target: inputElement, value: "" });
      dispatch('clear');
    });
  }
  
  // Compute character count
  $: charCount = value ? value.length : 0;
  $: charLimit = maxlength !== null ? maxlength : false;
  $: tooLong = charLimit && charCount > charLimit;
  
  // Compute animated label class
  $: floatingLabel = animate && label;
  $: labelClasses = [
    "block text-primary-300 font-medium transition-all duration-200",
    floatingLabel ? "pointer-events-none absolute" : "mb-1",
    floatingLabel && (focused || value) ? "-translate-y-6 scale-75 origin-left" : "",
    error ? "text-danger-500" : "",
    disabled ? "text-primary-400" : "",
  ].join(" ");
  
  // Compute final input wrapper classes
  $: wrapperClasses = [
    "relative",
    "mb-6", // Margin bottom to accommodate floating label & error message
  ].join(" ");
  
  // Compute final input classes
  $: inputClasses = [
    "w-full transition-all duration-200 outline-none",
    sizeClasses[size] || sizeClasses.md,
    !borderless ? "border" : "",
    rounded ? "rounded-lg" : "rounded",
    error ? "border-danger-500 focus:ring-danger-400" : variants[variant] || variants.default,
    icon && iconPosition === "left" ? "pl-10" : "",
    trailingIcon || (clearable && value) ? "pr-10" : "",
    disabled ? "bg-background-600/50 text-primary-300 cursor-not-allowed" : "",
    floatingLabel ? "pt-6" : "",
    "focus:ring-4 focus:ring-opacity-30",
    error ? "focus:ring-danger-400" : "focus:ring-primary-400",
    loading ? "animate-pulse" : "",
    $$restProps.class || "",
  ].join(" ");
</script>

<div class={wrapperClasses}>
  <!-- Label -->
  {#if label}
    <label 
      for={uniqueId}
      class={labelClasses}
      style={floatingLabel ? "top: 0.75rem; left: 0.75rem;" : ""}
    >
      {label}
      {#if required}
        <span class="text-danger-400 ml-1">*</span>
      {/if}
    </label>
  {/if}
  
  <div class="relative">
    <!-- Left Icon -->
    {#if icon && iconPosition === "left"}
      <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        <span class="text-primary-400" aria-hidden="true">{@html icon}</span>
      </div>
    {/if}
    
    <!-- Input Field -->
    <input
      bind:this={inputElement}
      {type}
      id={uniqueId}
      {name}
      {placeholder}
      {value}
      {disabled}
      {readonly}
      {required}
      {autocomplete}
      maxlength={charLimit ? charLimit : null}
      class={inputClasses}
      on:input={handleInput}
      on:change={event => dispatch('change', event)}
      on:focus={handleFocus}
      on:blur={handleBlur}
      aria-label={ariaLabel || label || null}
      aria-invalid={error ? "true" : "false"}
      aria-describedby={finalAriaDescribedBy}
      {...$$restProps}
    />
    
    <!-- Trailing Icon or Clear Button -->
    {#if (trailingIcon || (clearable && value)) && !disabled && !readonly}
      <div class="absolute inset-y-0 right-0 flex items-center pr-3">
        {#if clearable && value}
          <button 
            type="button" 
            class="text-primary-400 hover:text-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full focus:ring-opacity-50 transition-colors"
            on:click={clearInput}
            aria-label="Clear"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5" aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        {:else if trailingIcon}
          <span class="text-primary-400" aria-hidden="true">{@html trailingIcon}</span>
        {/if}
      </div>
    {/if}
    
    <!-- Loading Indicator -->
    {#if loading}
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="animate-spin w-5 h-5 text-primary-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    {/if}
  </div>
  
  <!-- Character Counter -->
  {#if showCounter && charLimit}
    <div class="mt-1 text-xs flex justify-end">
      <span class={tooLong ? "text-danger-500" : "text-primary-400"}>
        {charCount} / {charLimit}
      </span>
    </div>
  {/if}
  
  <!-- Error or Help Text -->
  {#if error}
    <p id={errorId} class="mt-1 text-sm text-danger-500">{error}</p>
  {:else if helpText}
    <p id={helpId} class="mt-1 text-sm text-primary-400">{helpText}</p>
  {/if}
</div>