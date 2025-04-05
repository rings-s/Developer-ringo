<script>
    import { onMount, tick } from 'svelte';
    import { fade, fly, draw, scale } from 'svelte/transition';
    import { cubicOut, elasticOut } from 'svelte/easing';
    
    let mounted = false;
    let headerVisible = false;
    let cursorX = 0;
    let cursorY = 0;
    let observer;
    let heroSection;
    let scrollY = 0;
    let windowHeight;
    let windowWidth;
    
    // Split text animation variables
    let titleElement;
    let titleChars = [];
    let subtitleElement;
    let subtitleWords = [];
    
    // Handle cursor movement for interactive elements
    function handleMouseMove(event) {
      cursorX = event.clientX;
      cursorY = event.clientY;
    }
    
    // Handle scroll events
    function handleScroll() {
      scrollY = window.scrollY;
    }
    
    // Split text into characters for animation
    function splitTextIntoChars(element, setter) {
      if (!element) return;
      
      const text = element.textContent;
      element.textContent = '';
      
      const chars = text.split('');
      const charElements = [];
      
      chars.forEach((char, index) => {
        const span = document.createElement('span');
        span.textContent = char;
        span.style.display = 'inline-block';
        span.style.opacity = '0';
        span.style.transform = 'translateY(20px)';
        span.style.transitionProperty = 'opacity, transform';
        span.style.transitionDuration = '0.6s';
        span.style.transitionTimingFunction = 'cubic-bezier(0.215, 0.61, 0.355, 1)';
        span.style.transitionDelay = `${0.03 * index}s`;
        
        element.appendChild(span);
        charElements.push(span);
      });
      
      setter(charElements);
    }
    
    // Split text into words for animation
    function splitTextIntoWords(element, setter) {
      if (!element) return;
      
      const text = element.textContent;
      element.textContent = '';
      
      const words = text.split(' ');
      const wordElements = [];
      
      words.forEach((word, index) => {
        const span = document.createElement('span');
        span.textContent = word + (index < words.length - 1 ? ' ' : '');
        span.style.display = 'inline-block';
        span.style.opacity = '0';
        span.style.transform = 'translateY(20px)';
        span.style.transitionProperty = 'opacity, transform';
        span.style.transitionDuration = '0.8s';
        span.style.transitionTimingFunction = 'cubic-bezier(0.215, 0.61, 0.355, 1)';
        span.style.transitionDelay = `${0.08 * index + 0.3}s`;
        
        element.appendChild(span);
        wordElements.push(span);
      });
      
      setter(wordElements);
    }
    
    // Animate the split text
    function animateSplitText() {
      // Animate title characters
      titleChars.forEach(char => {
        char.style.opacity = '1';
        char.style.transform = 'translateY(0)';
      });
      
      // Animate subtitle words
      subtitleWords.forEach(word => {
        word.style.opacity = '1';
        word.style.transform = 'translateY(0)';
      });
    }
    
    // Initialize the Intersection Observer
    function setupIntersectionObserver() {
      if (typeof IntersectionObserver !== 'undefined') {
        observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              headerVisible = true;
              animateSplitText();
            }
          });
        }, { threshold: 0.1 });
        
        if (heroSection) {
          observer.observe(heroSection);
        }
      } else {
        // Fallback for browsers without Intersection Observer
        headerVisible = true;
        animateSplitText();
      }
    }
    
    // Safely calculate transform values to avoid SSR issues
    function getTransformX(baseValue) {
      if (typeof window === 'undefined' || !windowWidth) return 0;
      return (cursorX - windowWidth/2) / baseValue;
    }
    
    function getTransformY(baseValue) {
      if (typeof window === 'undefined' || !windowHeight) return 0;
      return (cursorY - windowHeight/2) / baseValue;
    }
    
    onMount(async () => {
      mounted = true;
      
      // Wait for DOM update
      await tick();
      
      // Setup text splitting
      if (titleElement) {
        splitTextIntoChars(titleElement, chars => {
          titleChars = chars;
        });
      }
      
      if (subtitleElement) {
        splitTextIntoWords(subtitleElement, words => {
          subtitleWords = words;
        });
      }
      
      // Setup observer
      setupIntersectionObserver();
      
      return () => {
        if (observer) {
          observer.disconnect();
        }
      };
    });
  </script>
  
  <svelte:window 
    on:mousemove={handleMouseMove} 
    on:scroll={handleScroll}
    bind:innerHeight={windowHeight}
    bind:innerWidth={windowWidth}
  />
  
  <section 
    class="hero-advanced" 
    id="home"
    bind:this={heroSection}
    style="--mouse-x: {cursorX}px; --mouse-y: {cursorY}px; --scroll-y: {scrollY}px;"
  >
    <!-- Diagonal section divider -->
    <div class="diagonal-divider"></div>
    
    <!-- Background mask effects -->
    <div class="mask-container">
      <div class="mask mask-1"></div>
      <div class="mask mask-2"></div>
      <div class="mask mask-3"></div>
    </div>
    
    <!-- Decorative grid lines -->
    <div class="grid-lines">
      <div class="v-line v-line-1"></div>
      <div class="v-line v-line-2"></div>
      <div class="v-line v-line-3"></div>
      <div class="h-line h-line-1"></div>
      <div class="h-line h-line-2"></div>
    </div>
    
    <!-- Interactive floating elements -->
    <div class="floating-elements">
      <div class="floating-element el-1" style="transform: translate({getTransformX(20)}px, {getTransformY(20)}px)">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="58" fill="none" stroke="var(--primary-600)" stroke-width="2" stroke-dasharray="10 5" />
          <circle cx="60" cy="60" r="30" fill="var(--primary-800)" fill-opacity="0.2" />
        </svg>
      </div>
      
      <div class="floating-element el-2" style="transform: translate({-getTransformX(25)}px, {-getTransformY(25)}px)">
        <svg width="80" height="80" viewBox="0 0 80 80">
          <rect x="10" y="10" width="60" height="60" fill="none" stroke="var(--secondary-500)" stroke-width="2" rx="10" />
          <path d="M20 40 L60 40 M40 20 L40 60" stroke="var(--secondary-500)" stroke-width="2" />
        </svg>
      </div>
      
      <div class="floating-element el-3" style="transform: translate({getTransformX(15)}px, {-getTransformY(15)}px)">
        <svg width="60" height="60" viewBox="0 0 60 60">
          <polygon points="30,5 55,30 30,55 5,30" fill="none" stroke="var(--accent-500)" stroke-width="2" />
          <circle cx="30" cy="30" r="10" fill="var(--accent-700)" fill-opacity="0.2" />
        </svg>
      </div>
    </div>
    
    <!-- Main content column layout -->
    <div class="content-wrapper">
      <!-- Left column: Primary content -->
      <div class="content-column primary-content">
        <!-- Creative mask effect for title -->
        <div class="title-container">
          <h1 class="masked-title" bind:this={titleElement}>
            RINGO CRAFT
          </h1>
          
          <div class="title-backdrop">
            <svg width="100%" height="100%" viewBox="0 0 400 200" preserveAspectRatio="none">
              {#if mounted}
                <path 
                  d="M0 100 Q100 80 200 100 Q300 120 400 100 L400 200 L0 200 Z"
                  fill="var(--primary-800)"
                  fill-opacity="0.1"
                  in:draw={{ duration: 1500, delay: 300, easing: cubicOut }}
                ></path>
              {/if}
            </svg>
          </div>
        </div>
        
        <!-- Subtitle with staggered word animation -->
        <p class="subtitle" bind:this={subtitleElement}>
          Building Tomorrow's Apps Today
        </p>
        
        <!-- Animated highlight feature items -->
        {#if mounted}
          <div class="feature-list">
            <div class="feature-item" in:fly={{ y: 20, duration: 800, delay: 600 }}>
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5"></path>
                  <path d="M2 12l10 5 10-5"></path>
                </svg>
              </div>
              <div class="feature-text">
                <h3>Web App Engine</h3>
                <p>Fueling Digital Experiences</p>
              </div>
            </div>
            
            <div class="feature-item" in:fly={{ y: 20, duration: 800, delay: 800 }}>
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="4 17 10 11 4 5"></polyline>
                  <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
              </div>
              <div class="feature-text">
                <h3>Mobile App Core</h3>
                <p>Driving On-the-Go Apps</p>
              </div>
            </div>
          </div>
        {/if}
        
        <!-- Call to action with animation -->
        {#if mounted}
          <div class="cta-container" in:fly={{ y: 20, duration: 800, delay: 1000 }}>
            <a href="#about" class="cta-primary">
              <span class="cta-text">Explore Portfolio</span>
              <span class="cta-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </span>
              <span class="cta-backdrop"></span>
            </a>
          </div>
        {/if}
      </div>
      
      <!-- Right column: Visual showcase -->
      <div class="content-column visual-showcase">
        {#if mounted}
          <!-- Animated mockup display -->
          <div class="mockup-container" in:scale={{ start: 0.8, duration: 1000, delay: 400, easing: elasticOut }}>
            <!-- Stylized device frame -->
            <div class="device-frame">
              <!-- Animated content inside mockup -->
              <div class="device-content">
                <!-- Creative visual elements -->
                <div class="visual-element vis-el-1"></div>
                <div class="visual-element vis-el-2"></div>
                <div class="visual-element vis-el-3"></div>
                <div class="visual-element vis-el-4"></div>
                
                <!-- Animated typing text effect -->
                <div class="typing-container">
                  <span class="typing-text">Digital craftsmanship</span>
                </div>
                
                <!-- Dot pattern -->
                <div class="dot-pattern"></div>
              </div>
              
              <!-- Device controls -->
              <div class="device-controls">
                <span class="control-dot"></span>
                <span class="control-dot"></span>
                <span class="control-dot"></span>
              </div>
            </div>
            
            <!-- Decorative elements behind device -->
            <div class="decorative-circle circle-large"></div>
            <div class="decorative-square"></div>
          </div>
        {/if}
        
        <!-- Floating context label -->
        {#if mounted}
          <div class="context-label" in:fly={{ x: 30, duration: 800, delay: 1200 }}>
            <span class="label-highlight">Cutting-edge</span>
            <span class="label-text">design focused on experience</span>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Scroll indicator -->
    {#if mounted}
      <div class="scroll-indicator" in:fade={{ duration: 800, delay: 1500 }}>
        <div class="scroll-text">Scroll to explore</div>
        <div class="scroll-arrow">
          <svg width="20" height="30" viewBox="0 0 20 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 2 L10 28 M5 23 L10 28 L15 23" stroke="var(--primary-400)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    {/if}
  </section>
  
  <style>
    /* Main hero container */
    .hero-advanced {
      position: relative;
      height: 100vh;
      min-height: 700px;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      padding: 3rem 0;
      isolation: isolate;
    }
    
    /* Diagonal section divider */
    .diagonal-divider {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, transparent 49.9%, var(--primary-900) 50%);
      opacity: 0.5;
      z-index: -1;
    }
    
    /* Mask effects for dynamic background */
    .mask-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -2;
      overflow: hidden;
    }
    
    .mask {
      position: absolute;
      border-radius: 50%;
      filter: blur(60px);
    }
    
    .mask-1 {
      top: -20%;
      right: -10%;
      width: 40vw;
      height: 40vw;
      background: var(--primary-700);
      opacity: 0.05;
      transform-origin: center;
      animation: pulse-slow 15s infinite alternate;
    }
    
    .mask-2 {
      bottom: -10%;
      left: -5%;
      width: 30vw;
      height: 30vw;
      background: var(--secondary-600);
      opacity: 0.07;
      animation: pulse-slow 12s infinite alternate-reverse;
    }
    
    .mask-3 {
      top: 40%;
      left: 35%;
      width: 20vw;
      height: 20vw;
      background: var(--accent-500);
      opacity: 0.03;
      animation: pulse-slow 18s infinite alternate;
    }
    
    /* Decorative grid lines */
    .grid-lines {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
    }
    
    .v-line, .h-line {
      position: absolute;
      background-color: var(--primary-800);
      opacity: 0.1;
    }
    
    .v-line {
      width: 1px;
      height: 100%;
      top: 0;
    }
    
    .h-line {
      width: 100%;
      height: 1px;
      left: 0;
    }
    
    .v-line-1 { left: 25%; }
    .v-line-2 { left: 50%; }
    .v-line-3 { left: 75%; }
    .h-line-1 { top: 33%; }
    .h-line-2 { top: 66%; }
    
    /* Floating elements that react to cursor */
    .floating-elements {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
      pointer-events: none;
    }
    
    .floating-element {
      position: absolute;
      transition: transform 0.5s cubic-bezier(0.215, 0.61, 0.355, 1);
    }
    
    .el-1 {
      top: 15%;
      left: 10%;
    }
    
    .el-2 {
      bottom: 20%;
      right: 15%;
    }
    
    .el-3 {
      top: 60%;
      left: 25%;
    }
    
    /* Main content wrapper */
    .content-wrapper {
      display: grid;
      grid-template-columns: 1fr;
      gap: 4rem;
      max-width: 1200px;
      width: 100%;
      padding: 0 2rem;
      margin: 0 auto;
    }
    
    @media (min-width: 1024px) {
      .content-wrapper {
        grid-template-columns: 5fr 6fr;
        gap: 2rem;
        padding: 0;
      }
    }
    
    /* Content columns */
    .content-column {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    
    /* Primary content (left column) */
    .primary-content {
      position: relative;
      z-index: 2;
    }
    
    /* Title with mask effect */
    .title-container {
      position: relative;
      margin-bottom: 1.5rem;
    }
    
    .masked-title {
      font-size: clamp(2.5rem, 5vw, 3.5rem);
      font-weight: 800;
      line-height: 1.1;
      color: var(--primary-100);
      position: relative;
      z-index: 1;
    }
    
    .title-backdrop {
      position: absolute;
      top: 0;
      left: -20px;
      width: calc(100% + 40px);
      height: 100%;
      z-index: -1;
    }
    
    /* Subtitle styling */
    .subtitle {
      font-size: clamp(1.1rem, 2vw, 1.25rem);
      font-weight: 400;
      color: var(--primary-300);
      line-height: 1.6;
      margin-bottom: 2.5rem;
      max-width: 540px;
    }
    
    /* Feature list */
    .feature-list {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }
    
    .feature-item {
      display: flex;
      align-items: flex-start;
      gap: 1rem;
    }
    
    .feature-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background-color: var(--primary-800);
      color: var(--primary-400);
    }
    
    .feature-text h3 {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
      color: var(--primary-200);
    }
    
    .feature-text p {
      font-size: 0.95rem;
      color: var(--primary-400);
      margin: 0;
    }
    
    /* Call to action */
    .cta-container {
      margin-top: 1rem;
    }
    
    .cta-primary {
      position: relative;
      display: inline-flex;
      align-items: center;
      padding: 0.875rem 2rem;
      border: none;
      background: none;
      font-size: 1rem;
      font-weight: 600;
      color: var(--primary-200);
      cursor: pointer;
      overflow: hidden;
      text-decoration: none;
    }
    
    .cta-text {
      position: relative;
      z-index: 2;
      transition: color 0.3s ease;
    }
    
    .cta-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-left: 0.5rem;
      position: relative;
      z-index: 2;
      transition: transform 0.3s ease;
    }
    
    .cta-backdrop {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(to right, var(--primary-500), var(--secondary-500));
      z-index: 1;
      opacity: 0.1;
      transition: opacity 0.3s ease;
      border-radius: 4px;
    }
    
    .cta-primary:hover .cta-icon {
      transform: translateX(5px);
    }
    
    .cta-primary:hover .cta-backdrop {
      opacity: 0.2;
    }
    
    .cta-primary:hover .cta-text {
      color: var(--primary-100);
    }
    
    /* Visual showcase (right column) */
    .visual-showcase {
      position: relative;
    }
    
    /* Mockup container */
    .mockup-container {
      position: relative;
      width: 100%;
      max-width: 480px;
      margin: 0 auto;
    }
    
    /* Device frame */
    .device-frame {
      position: relative;
      width: 100%;
      height: 0;
      padding-bottom: 68%; /* 16:9 aspect ratio */
      background: var(--primary-900);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      border: 2px solid var(--primary-700);
    }
    
    /* Device content */
    .device-content {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-900), var(--primary-800));
      overflow: hidden;
    }
    
    /* Visual elements inside device */
    .visual-element {
      position: absolute;
      border-radius: 8px;
    }
    
    .vis-el-1 {
      top: 15%;
      left: 10%;
      width: 30%;
      height: 20%;
      background: linear-gradient(to right, var(--primary-600), var(--primary-500));
      opacity: 0.2;
      animation: float-slow 10s infinite alternate;
    }
    
    .vis-el-2 {
      bottom: 20%;
      right: 15%;
      width: 25%;
      height: 15%;
      background: linear-gradient(to right, var(--secondary-600), var(--secondary-500));
      opacity: 0.3;
      animation: float-slow 12s infinite alternate-reverse;
    }
    
    .vis-el-3 {
      top: 45%;
      right: 25%;
      width: 15%;
      height: 25%;
      background: linear-gradient(to top, var(--accent-600), var(--accent-500));
      opacity: 0.15;
      animation: float-slow 15s infinite alternate;
    }
    
    .vis-el-4 {
      bottom: 15%;
      left: 20%;
      width: 20%;
      height: 10%;
      background: linear-gradient(to bottom, var(--primary-700), var(--primary-600));
      opacity: 0.2;
      animation: float-slow 8s infinite alternate-reverse;
    }
    
    /* Typing text effect */
    .typing-container {
      position: absolute;
      top: 65%;
      left: 50%;
      transform: translateX(-50%);
      font-size: 1.2rem;
      color: var(--primary-500);
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    
    .typing-text {
      position: relative;
      white-space: nowrap;
      border-right: 3px solid var(--primary-500);
      padding-right: 5px;
      animation: typing 3.5s steps(20) infinite alternate, blink 0.7s step-end infinite;
      overflow: hidden;
      display: inline-block;
      width: 0;
    }
    
    /* Dot pattern */
    .dot-pattern {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: radial-gradient(var(--primary-500) 1px, transparent 1px);
      background-size: 20px 20px;
      opacity: 0.05;
    }
    
    /* Device controls */
    .device-controls {
      position: absolute;
      top: 12px;
      left: 15px;
      display: flex;
      gap: 6px;
    }
    
    .control-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: var(--primary-500);
      opacity: 0.5;
    }
    
    /* Decorative elements */
    .decorative-circle {
      position: absolute;
      border-radius: 50%;
      background: conic-gradient(from 0deg, var(--primary-700), var(--primary-600), var(--primary-700));
      opacity: 0.05;
      z-index: -1;
    }
    
    .circle-large {
      width: 180%;
      height: 180%;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
    
    .decorative-square {
      position: absolute;
      width: 60%;
      height: 60%;
      bottom: -10%;
      right: -15%;
      background: var(--secondary-800);
      transform: rotate(15deg);
      opacity: 0.07;
      z-index: -2;
    }
    
    /* Context label */
    .context-label {
      position: absolute;
      top: 10%;
      right: 0;
      background: var(--background-800);
      padding: 0.75rem 1.5rem;
      border-radius: 30px;
      font-size: 0.875rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
      border: 1px solid var(--primary-700);
    }
    
    .label-highlight {
      font-weight: 700;
      color: var(--primary-300);
      margin-right: 0.5rem;
    }
    
    .label-text {
      color: var(--primary-400);
    }
    
    /* Scroll indicator */
    .scroll-indicator {
      position: absolute;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
    }
    
    .scroll-text {
      font-size: 0.85rem;
      color: var(--primary-400);
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    
    .scroll-arrow {
      animation: bounce 2s infinite;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .context-label {
        display: none;
      }
      
      .mockup-container {
        max-width: 90%;
      }
    }
    
    /* Animations */
    @keyframes pulse-slow {
      0% {
        transform: scale(1);
      }
      100% {
        transform: scale(1.2);
      }
    }
    
    @keyframes float-slow {
      0%, 100% {
        transform: translateY(0) translateX(0);
      }
      50% {
        transform: translateY(-10px) translateX(5px);
      }
    }
    
    @keyframes typing {
      0% {
        width: 0;
      }
      80%, 100% {
        width: 100%;
      }
    }
    
    @keyframes blink {
      from, to {
        border-color: transparent;
      }
      50% {
        border-color: var(--primary-500);
      }
    }
    
    @keyframes bounce {
      0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
      }
      40% {
        transform: translateY(-8px);
      }
      60% {
        transform: translateY(-4px);
      }
    }
  </style>