<script>
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    
    // Service categories data
    const serviceCategories = [
      {
        id: 'web-development',
        title: 'Web Development',
        description: 'Modern, responsive websites and web applications built with the latest technologies.',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-10 w-10"><path d="m18 16 4-4-4-4"></path><path d="m6 8-4 4 4 4"></path><path d="m14.5 4-5 16"></path></svg>`,
        services: [
          {
            title: 'Custom Website Development',
            description: 'Tailored websites designed to meet your unique business needs and goals.',
            price: 'Starting at $2,500',
            features: ['Responsive design', 'SEO optimization', 'Performance tuning', 'CMS integration']
          },
          {
            title: 'E-commerce Solutions',
            description: 'Full-featured online stores that drive sales and enhance customer experience.',
            price: 'Starting at $3,500',
            features: ['Product management', 'Secure checkout', 'Inventory tracking', 'Payment gateway integration']
          },
          {
            title: 'Web Application Development',
            description: 'Powerful, scalable web applications that solve complex business challenges.',
            price: 'Starting at $5,000',
            features: ['Custom functionality', 'User authentication', 'Data management', 'Third-party API integration']
          }
        ]
      },
      {
        id: 'digital-marketing',
        title: 'Digital Marketing',
        description: 'Data-driven strategies to increase your online presence and drive qualified traffic.',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-10 w-10"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>`,
        services: [
          {
            title: 'Search Engine Optimization (SEO)',
            description: 'Improve your website`s visibility in search results and drive organic traffic.',
            price: 'Starting at $800/month',
            features: ['Keyword research', 'On-page optimization', 'Content strategy', 'Performance tracking']
          },
          {
            title: 'Pay-Per-Click Advertising (PPC)',
            description: 'Targeted ad campaigns that deliver immediate results and measurable ROI.',
            price: 'Starting at $1,000/month',
            features: ['Campaign strategy', 'Ad creation', 'Audience targeting', 'Conversion tracking']
          },
          {
            title: 'Social Media Marketing',
            description: 'Engage with your audience and build your brand on the platforms that matter most.',
            price: 'Starting at $750/month',
            features: ['Content creation', 'Community management', 'Paid social campaigns', 'Performance analytics']
          }
        ]
      },
      {
        id: 'ux-design',
        title: 'UX/UI Design',
        description: 'User-centered design that creates intuitive, engaging digital experiences.',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-10 w-10"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"></path><path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"></path><path d="M12 2v2"></path><path d="M12 22v-2"></path><path d="m17 20.66-1-1.73"></path><path d="M11 10.27 7 3.34"></path><path d="m20.66 17-1.73-1"></path><path d="m3.34 7 1.73 1"></path><path d="M14 12h8"></path><path d="M2 12h8"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m17 3.34-1 1.73"></path><path d="m7 20.66 1-1.73"></path></svg>`,
        services: [
          {
            title: 'User Experience Design',
            description: 'Research-based design that optimizes user flows and creates seamless interactions.',
            price: 'Starting at $3,000',
            features: ['User research', 'Wireframing', 'Usability testing', 'Information architecture']
          },
          {
            title: 'User Interface Design',
            description: 'Visually stunning interfaces that align with your brand and delight your users.',
            price: 'Starting at $2,500',
            features: ['Visual design', 'Interaction design', 'Responsive layouts', 'Design systems']
          },
          {
            title: 'App Design',
            description: 'Intuitive, engaging mobile app designs that drive downloads and user retention.',
            price: 'Starting at $4,000',
            features: ['App wireframing', 'UI design', 'Prototype creation', 'Design specifications']
          }
        ]
      }
    ];
    
    // Testimonials data
    const testimonials = [
      {
        quote: "Working with this team transformed our online presence. Our new website has increased lead generation by 40% in just three months.",
        author: "Sarah Johnson",
        company: "Elevate Marketing",
        image: "https://i.pravatar.cc/150?img=1"
      },
      {
        quote: "The SEO services have been a game-changer for our business. We're now ranking on the first page for our key terms, and the traffic is converting.",
        author: "Michael Chen",
        company: "Pacific Technologies",
        image: "https://i.pravatar.cc/150?img=4"
      },
      {
        quote: "The UX redesign of our app led to a 30% increase in user engagement and dramatically reduced our customer support inquiries.",
        author: "Amanda Rodriguez",
        company: "Fintech Solutions",
        image: "https://i.pravatar.cc/150?img=5"
      }
    ];
    
    // FAQs data
    const faqs = [
      {
        question: "What is your typical process for a new project?",
        answer: "Our process typically includes discovery, planning, design, development, testing, and launch phases. We start with understanding your business goals and requirements, create a detailed project plan, design and develop the solution, thoroughly test it, and then launch. We also provide post-launch support to ensure everything runs smoothly."
      },
      {
        question: "How long does it usually take to complete a website?",
        answer: "Project timelines vary based on complexity, but a typical website takes 6-12 weeks from concept to launch. Simple websites might be completed in 4-6 weeks, while complex web applications can take 3-6 months. We'll provide a detailed timeline during our initial consultation based on your specific requirements."
      },
      {
        question: "Do you provide ongoing maintenance and support?",
        answer: "Yes, we offer various maintenance and support packages to keep your digital assets secure, updated, and performing optimally. These include regular updates, security monitoring, performance optimization, content updates, and technical support. We can customize a maintenance plan that meets your specific needs and budget."
      },
      {
        question: "How do you measure the success of your services?",
        answer: "We establish clear KPIs at the beginning of each project aligned with your business goals. For websites, we track metrics like traffic, conversion rates, and engagement. For marketing services, we monitor metrics such as search rankings, click-through rates, and lead generation. We provide regular reports and insights on these metrics."
      },
      {
        question: "What makes your agency different from others?",
        answer: "We distinguish ourselves through our strategic approach, technical expertise, and commitment to results. Unlike agencies that focus only on aesthetics, we align our work with your business objectives. Our team brings extensive experience across industries, and we prioritize transparent communication throughout the process. We consider ourselves a partner in your success, not just a service provider."
      }
    ];
    
    // Active FAQ for accordion functionality
    let activeFaq = -1;
    
    function toggleFaq(index) {
      activeFaq = activeFaq === index ? -1 : index;
    }
    
    // For tracking animations
    let isVisible = false;
    
    onMount(() => {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            isVisible = true;
            observer.disconnect();
          }
        });
      }, { threshold: 0.1 });
      
      const section = document.getElementById('services-section');
      if (section) observer.observe(section);
      
      return () => observer.disconnect();
    });
  </script>
  
  <svelte:head>
    <title>Our Services | Professional Web Development, Marketing & Design</title>
    <meta name="description" content="Explore our comprehensive range of web development, digital marketing, and UX/UI design services tailored to help your business grow online.">
  </svelte:head>
  
  <main id="services-section">
    <!-- Hero Section -->
    <section class="hero">
      <div class="container mx-auto px-4 py-16 md:py-24">
        <div class="max-w-2xl mx-auto text-center">
          {#if isVisible}
            <div in:fly={{ y: -20, duration: 500, delay: 100 }}>
              <h1 class="h1">Expert Solutions for Digital Success</h1>
              <p class="lead mt-4 mb-8">We provide end-to-end services to help your business thrive in the digital landscape.</p>
              <div class="flex flex-wrap justify-center gap-4">
                <a href="#contact" class="btn variant-filled-primary">Get Started</a>
                <a href="#categories" class="btn variant-ghost">Learn More</a>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </section>
    
    <!-- Service Categories Section -->
    <section id="categories" class="py-16 bg-surface-50-900-token">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="h2">Our Service Categories</h2>
          <p class="lead max-w-2xl mx-auto mt-4">Comprehensive solutions tailored to your specific business needs</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          {#each serviceCategories as category, index}
            {#if isVisible}
              <div 
                class="card p-6 h-full"
                in:fly={{ y: 20, duration: 500, delay: 200 + index * 100 }}
              >
                <div class="text-primary-500 mb-4">{@html category.icon}</div>
                <h3 class="h3 mb-2">{category.title}</h3>
                <p class="mb-4">{category.description}</p>
                <a href={`#${category.id}`} class="anchor">View Services →</a>
              </div>
            {/if}
          {/each}
        </div>
      </div>
    </section>
    
    <!-- Detailed Services Sections -->
    {#each serviceCategories as category, categoryIndex}
      <section id={category.id} class="py-16 {categoryIndex % 2 !== 0 ? 'bg-surface-50-900-token' : ''}">
        <div class="container mx-auto px-4">
          <div class="text-center mb-16">
            <h2 class="h2">{category.title}</h2>
            <p class="lead max-w-2xl mx-auto mt-4">{category.description}</p>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {#each category.services as service, serviceIndex}
              {#if isVisible}
                <div 
                  class="card p-0 h-full flex flex-col"
                  in:fly={{ y: 20, duration: 500, delay: 200 + serviceIndex * 100 }}
                >
                  <div class="p-6 flex-1">
                    <h3 class="h3 mb-2">{service.title}</h3>
                    <p class="mb-4">{service.description}</p>
                    <p class="font-semibold text-primary-500">{service.price}</p>
                    
                    <ul class="mt-4 space-y-2">
                      {#each service.features as feature}
                        <li class="flex items-start">
                          <svg class="h-5 w-5 text-success-500 mr-2 mt-0.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                          </svg>
                          <span>{feature}</span>
                        </li>
                      {/each}
                    </ul>
                  </div>
                  
                  <div class="p-6 border-t border-surface-300-600-token">
                    <a href="#contact" class="btn variant-filled-primary w-full">Request a Quote</a>
                  </div>
                </div>
              {/if}
            {/each}
          </div>
        </div>
      </section>
    {/each}
    
    <!-- Testimonials Section -->
    <section class="py-16 bg-surface-50-900-token">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="h2">What Our Clients Say</h2>
          <p class="lead max-w-2xl mx-auto mt-4">Hear from the businesses we've helped succeed</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          {#each testimonials as testimonial, index}
            {#if isVisible}
              <div 
                class="card p-6 h-full"
                in:fly={{ y: 20, duration: 500, delay: 200 + index * 100 }}
              >
                <div class="flex items-center mb-4">
                  <img 
                    src={testimonial.image} 
                    alt={testimonial.author} 
                    class="w-12 h-12 rounded-full mr-4"
                    width="48"
                    height="48"
                    loading="lazy"
                  />
                  <div>
                    <p class="font-bold">{testimonial.author}</p>
                    <p class="text-sm">{testimonial.company}</p>
                  </div>
                </div>
                <blockquote class="italic">"<span>{testimonial.quote}</span>"</blockquote>
              </div>
            {/if}
          {/each}
        </div>
      </div>
    </section>
    
    <!-- FAQs Section -->
    <section id="faq" class="py-16">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="h2">Frequently Asked Questions</h2>
          <p class="lead max-w-2xl mx-auto mt-4">Get answers to common questions about our services</p>
        </div>
        
        <div class="max-w-3xl mx-auto">
          {#each faqs as faq, index}
            {#if isVisible}
              <div 
                class="card p-0 mb-4 overflow-hidden"
                in:fly={{ y: 20, duration: 300, delay: 100 + index * 50 }}
              >
                <button 
                  class="w-full p-6 text-left font-semibold flex justify-between items-center"
                  on:click={() => toggleFaq(index)}
                  aria-expanded={activeFaq === index}
                  aria-controls={`faq-content-${index}`}
                >
                  <span>{faq.question}</span>
                  <svg 
                    class="h-5 w-5 transform transition-transform duration-200 {activeFaq === index ? 'rotate-180' : ''}" 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                  >
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
                
                {#if activeFaq === index}
                  <div 
                    id={`faq-content-${index}`}
                    class="px-6 pb-6"
                    transition:fly={{ y: -10, duration: 200 }}
                  >
                    <p>{faq.answer}</p>
                  </div>
                {/if}
              </div>
            {/if}
          {/each}
        </div>
      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-16 bg-primary-500 text-white">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto text-center">
          {#if isVisible}
            <div in:fly={{ y: 20, duration: 500 }}>
              <h2 class="h2 !text-white">Ready to Transform Your Digital Presence?</h2>
              <p class="lead mt-4 mb-8 !text-white opacity-90">Get in touch today to discuss how we can help your business grow.</p>
              <a href="#contact" class="btn bg-white text-primary-700 hover:bg-primary-100">Schedule a Consultation</a>
            </div>
          {/if}
        </div>
      </div>
    </section>
    
    <!-- Contact Form Section -->
    <section id="contact" class="py-16">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="h2">Get in Touch</h2>
            <p class="lead max-w-2xl mx-auto mt-4">Fill out the form below and we'll get back to you within 24 hours</p>
          </div>
          
          <div class="card p-8">
            <form>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="form-group">
                  <label for="name" class="form-label">Full Name</label>
                  <input 
                    id="name" 
                    type="text" 
                    class="input" 
                    placeholder="Your name" 
                    required
                  />
                </div>
                
                <div class="form-group">
                  <label for="email" class="form-label">Email Address</label>
                  <input 
                    id="email" 
                    type="email" 
                    class="input" 
                    placeholder="your@email.com" 
                    required
                  />
                </div>
              </div>
              
              <div class="form-group mb-6">
                <label for="service" class="form-label">Service of Interest</label>
                <select id="service" class="select">
                  <option value="" disabled selected>Select a service</option>
                  {#each serviceCategories as category}
                    <optgroup label={category.title}>
                      {#each category.services as service}
                        <option value={service.title}>{service.title}</option>
                      {/each}
                    </optgroup>
                  {/each}
                </select>
              </div>
              
              <div class="form-group mb-6">
                <label for="message" class="form-label">Message</label>
                <textarea 
                  id="message" 
                  class="textarea" 
                  rows="5" 
                  placeholder="Tell us about your project and requirements..."
                  required
                ></textarea>
              </div>
              
              <div class="form-group">
                <button type="submit" class="btn variant-filled-primary w-full md:w-auto">Submit Request</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  </main>
  
  <style>
    /* Typography */
    .h1 {
      font-size: 2.5rem;
      line-height: 1.2;
      font-weight: 700;
      letter-spacing: -0.025em;
    }
    
    .h2 {
      font-size: 2rem;
      line-height: 1.3;
      font-weight: 700;
      letter-spacing: -0.025em;
    }
    
    .h3 {
      font-size: 1.25rem;
      line-height: 1.4;
      font-weight: 600;
    }
    
    .lead {
      font-size: 1.125rem;
      line-height: 1.6;
      color: var(--color-surface-700-200-token);
    }
    
    /* Card Component */
    .card {
      background-color: var(--color-surface-100-800-token);
      border: 1px solid var(--color-surface-300-600-token);
      border-radius: var(--rounded-container-token, 0.5rem);
      box-shadow: var(--shadow-sm);
      transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    
    .card:hover {
      box-shadow: var(--shadow-md);
    }
    
    /* Button Components */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: 500;
      padding: 0.625rem 1.25rem;
      border-radius: var(--rounded-token, 0.5rem);
      transition: all 0.2s ease-in-out;
      cursor: pointer;
    }
    
    .variant-filled-primary {
      background-color: var(--color-primary-500);
      color: var(--color-primary-500-contrast);
    }
    
    .variant-filled-primary:hover {
      background-color: var(--color-primary-600);
    }
    
    .variant-ghost {
      background-color: transparent;
      border: 1px solid var(--color-surface-300-600-token);
    }
    
    .variant-ghost:hover {
      background-color: var(--color-surface-100-800-token);
    }
    
    /* Form Components */
    .form-group {
      margin-bottom: 1rem;
    }
    
    .form-label {
      display: block;
      margin-bottom: 0.375rem;
      font-weight: 500;
    }
    
    .input, .select, .textarea {
      width: 100%;
      padding: 0.625rem;
      border: 1px solid var(--color-surface-300-600-token);
      border-radius: var(--rounded-token, 0.375rem);
      background-color: var(--color-surface-100-800-token);
      transition: border-color 0.2s ease-in-out;
    }
    
    .input:focus, .select:focus, .textarea:focus {
      outline: none;
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 2px var(--color-primary-500-rgb-values, 59, 130, 246) / 0.1;
    }
    
    /* Link styles */
    .anchor {
      color: var(--color-primary-500);
      font-weight: 500;
      text-decoration: none;
      transition: color 0.2s ease-in-out;
    }
    
    .anchor:hover {
      color: var(--color-primary-700);
      text-decoration: underline;
    }
    
    /* Utility Classes */
    .mx-auto {
      margin-left: auto;
      margin-right: auto;
    }
    
    .container {
      width: 100%;
      max-width: 1280px;
    }
    
    .px-4 {
      padding-left: 1rem;
      padding-right: 1rem;
    }
    
    .py-16 {
      padding-top: 4rem;
      padding-bottom: 4rem;
    }
    
    .mt-4 {
      margin-top: 1rem;
    }
    
    .mb-4 {
      margin-bottom: 1rem;
    }
    
    .mb-8 {
      margin-bottom: 2rem;
    }
    
    .mb-16 {
      margin-bottom: 4rem;
    }
    
    .mr-2 {
      margin-right: 0.5rem;
    }
    
    .mr-4 {
      margin-right: 1rem;
    }
    
    .mt-0\.5 {
      margin-top: 0.125rem;
    }
    
    .text-center {
      text-align: center;
    }
    
    .text-left {
      text-align: left;
    }
    
    .text-sm {
      font-size: 0.875rem;
    }
    
    .font-bold {
      font-weight: 700;
    }
    
    .font-semibold {
      font-weight: 600;
    }
    
    .italic {
      font-style: italic;
    }
    
    .text-white {
      color: white;
    }
    
    .text-primary-500 {
      color: var(--color-primary-500);
    }
    
    .text-primary-700 {
      color: var(--color-primary-700);
    }
    
    .text-success-500 {
      color: var(--color-success-500, #10b981);
    }
    
    .bg-primary-500 {
      background-color: var(--color-primary-500);
    }
    
    .bg-surface-50-900-token {
      background-color: var(--color-surface-50-900-token);
    }
    
    .flex {
      display: flex;
    }
    
    .flex-col {
      flex-direction: column;
    }
    
    .flex-wrap {
      flex-wrap: wrap;
    }
    
    .items-center {
      align-items: center;
    }
    
    .items-start {
      align-items: flex-start;
    }
    
    .justify-center {
      justify-content: center;
    }
    
    .justify-between {
      justify-between: space-between;
    }
    
    .space-y-2 > * + * {
      margin-top: 0.5rem;
    }
    
    .gap-4 {
      gap: 1rem;
    }
    
    .gap-6 {
      gap: 1.5rem;
    }
    
    .gap-8 {
      gap: 2rem;
    }
    
    .w-full {
      width: 100%;
    }
    
    .w-12 {
      width: 3rem;
    }
    
    .h-12 {
      height: 3rem;
    }
    
    .w-5 {
      width: 1.25rem;
    }
    
    .h-5 {
      height: 1.25rem;
    }
    
    .max-w-2xl {
      max-width: 42rem;
    }
    
    .max-w-3xl {
      max-width: 48rem;
    }
    
    .rounded-full {
      border-radius: 9999px;
    }
    
    .grid {
      display: grid;
    }
    
    .grid-cols-1 {
      grid-template-columns: repeat(1, minmax(0, 1fr));
    }
    
    .transform {
      transform: translateX(var(--tw-translate-x)) translateY(var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
    }
    
    .transition-transform {
      transition-property: transform;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .duration-200 {
      transition-duration: 200ms;
    }
    
    .rotate-180 {
      --tw-rotate: 180deg;
    }
    
    .h-full {
      height: 100%;
    }
    
    .overflow-hidden {
      overflow: hidden;
    }
    
    .p-0 {
      padding: 0;
    }
    
    .p-6 {
      padding: 1.5rem;
    }
    
    .p-8 {
      padding: 2rem;
    }
    
    .border-t {
      border-top-width: 1px;
      border-top-style: solid;
    }
    
    .border-surface-300-600-token {
      border-color: var(--color-surface-300-600-token);
    }
    
    .opacity-90 {
      opacity: 0.9;
    }
    
    /* Media Queries */
    @media (min-width: 768px) {
      .md\:py-24 {
        padding-top: 6rem;
        padding-bottom: 6rem;
      }
      
      .md\:grid-cols-2 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      
      .md\:grid-cols-3 {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      
      .md\:w-auto {
        width: auto;
      }
    }
    
    @media (min-width: 1024px) {
      .lg\:grid-cols-3 {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      
      .h1 {
        font-size: 3rem;
      }
      
      .h2 {
        font-size: 2.25rem;
      }
      
      .h3 {
        font-size: 1.5rem;
      }
    }
    
    /* Fix for dark mode text */
    .dark .text-white {
      color: white !important;
    }
  </style>