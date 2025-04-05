<script>
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    
    // Import components from your UI library
    import Card from '$lib/components/ui/Card.svelte';
    import Accordion from '$lib/components/ui/Accordion.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
    
    let visible = false;
    
    // Data for tabs
    const tabs = [
      { id: 'experience', label: 'Experience', icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>' },
      { id: 'education', label: 'Education', icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path></svg>' },
      { id: 'skills', label: 'Skills', icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>' }
    ];
    
    let activeTab = 'experience';
    
    // Data for accordion
    const accordionItems = [
      {
        title: 'Senior Developer at TechCorp',
        content: 'Led development of multiple web and mobile applications for enterprise clients. Managed a team of 5 developers and implemented CI/CD workflows that reduced deployment time by 40%.'
      },
      {
        title: 'Full Stack Developer at WebSolutions',
        content: 'Developed responsive web applications using React and Node.js. Implemented RESTful APIs and integrated with various third-party services. Reduced load times by 60% through optimization techniques.'
      },
      {
        title: 'Frontend Developer at CreativeApps',
        content: 'Created user interfaces for mobile and web applications. Worked closely with design team to implement pixel-perfect designs. Developed reusable component libraries that increased development efficiency.'
      }
    ];
    
    // Skills data for progress bars
    const skills = [
      { name: 'Frontend Development', value: 92 },
      { name: 'UI/UX Design', value: 85 },
      { name: 'Backend Development', value: 78 },
      { name: 'Mobile Development', value: 80 }
    ];
    
    // Tech stack for badges
    const techStack = [
      'JavaScript', 'TypeScript', 'React', 'Svelte', 'Node.js', 
      'Express', 'MongoDB', 'PostgreSQL', 'React Native', 
      'Flutter', 'AWS', 'Docker'
    ];
    
    onMount(() => {
      // Set up intersection observer to trigger animations when component is visible
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            visible = true;
            observer.disconnect();
          }
        });
      }, { threshold: 0.2 });
      
      // Observe this section
      const section = document.getElementById('about');
      if (section) observer.observe(section);
      
      return () => {
        observer.disconnect();
      };
    });
  </script>
  
  <section id="about" class="about-section">
    <div class="about-container">
      <!-- Section Header -->
      <header class="section-header">
        {#if visible}
          <div class="section-tag" in:fly={{ y: 20, duration: 600, delay: 100 }}>
            <span class="tag-line"></span>
            <span class="tag-text">About Me</span>
          </div>
          <h2 in:fly={{ y: 20, duration: 600, delay: 300 }}>Crafting Digital Experiences That Matter</h2>
        {/if}
      </header>
      
      <!-- Main Content Grid -->
      <div class="content-grid">
        <!-- Bio Column -->
        <div class="content-column">
          {#if visible}
            <div in:fly={{ y: 20, duration: 600, delay: 500 }}>
              <Card title="My Journey" elevation="lg">
                <div class="bio-content">
                  <p class="lead-text">I'm a passionate web and mobile developer with 5+ years of experience building elegant solutions for complex problems.</p>
                  
                  <p>My journey in development started with a curiosity about how things work, which evolved into a career focused on creating intuitive, efficient, and beautiful applications. I specialize in full-stack development with a particular emphasis on modern front-end technologies.</p>
                  
                  <p>When I'm not coding, you'll find me exploring new technologies, contributing to open-source projects, or sharing knowledge through my tech blog.</p>
                  
                  <!-- Stats Grid -->
                  <div class="stats-grid">
                    <div class="stat-item">
                      <span class="stat-number">5+</span>
                      <span class="stat-label">Years Experience</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-number">50+</span>
                      <span class="stat-label">Projects Completed</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-number">20+</span>
                      <span class="stat-label">Happy Clients</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-number">10+</span>
                      <span class="stat-label">Technologies</span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          {/if}
        </div>
        
        <!-- Skills Column -->
        <div class="content-column">
          {#if visible}
            <div in:fly={{ y: 20, duration: 600, delay: 700 }}>
              <Card title="Professional Profile" elevation="lg">
                <div class="tabs-container">
                  <Tabs 
                    {tabs} 
                    bind:activeTab 
                    variant="pill" 
                    stacked={false}
                    iconPosition="left"
                    animated={true}
                    size="md"
                    spacing="normal"
                  >
                    <!-- Experience tab content -->
                    <div class="tab-content" slot="tab-0">
                      <Accordion 
                        items={accordionItems} 
                        bordered={true}
                        iconPosition="right"
                        rounded={true}
                        size="md"
                        spacing="compact"
                        variant="default"
                      />
                    </div>
                    
                    <!-- Education tab content -->
                    <div class="tab-content" slot="tab-1">
                      <div class="education-content">
                        <div class="education-item">
                          <h3>Master's in Computer Science</h3>
                          <p class="education-meta">University of Technology, 2016-2018</p>
                          <p>Specialized in Software Engineering and Human-Computer Interaction. Graduated with distinction.</p>
                        </div>
                        <div class="education-item">
                          <h3>Bachelor's in Computer Engineering</h3>
                          <p class="education-meta">State Technical University, 2012-2016</p>
                          <p>Focused on software development and computer networks. Graduated with honors.</p>
                        </div>
                        <div class="education-item">
                          <h3>Certifications</h3>
                          <ul class="certification-list">
                            <li>AWS Certified Developer</li>
                            <li>Google Professional Cloud Developer</li>
                            <li>Certified Scrum Master</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Skills tab content -->
                    <div class="tab-content" slot="tab-2">
                      <div class="skills-content">
                        <div class="skill-bars">
                          {#each skills as skill}
                            <div class="skill-item">
                              <div class="skill-info">
                                <span class="skill-name">{skill.name}</span>
                                <span class="skill-percentage">{skill.value}%</span>
                              </div>
                              <ProgressBar 
                                value={skill.value} 
                                variant="primary" 
                                size="md" 
                                rounded={true}
                                backgroundColor="var(--primary-800)"
                              />
                            </div>
                          {/each}
                        </div>
                        
                        <h3 class="tech-stack-title">Tech Stack</h3>
                        <div class="tech-stack">
                          {#each techStack as tech}
                            <Badge 
                              variant="primary" 
                              outline={true} 
                              pill={true} 
                              size="md"
                            >
                              {tech}
                            </Badge>
                          {/each}
                        </div>
                      </div>
                    </div>
                  </Tabs>
                </div>
              </Card>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </section>
  
  <style>
    /* Section Layout */
    .about-section {
      padding: 6rem 0 8rem;
      position: relative;
      background-color: var(--background-500);
    }
    
    .about-container {
      width: 100%;
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 2rem;
    }
    
    /* Section Header */
    .section-header {
      text-align: center;
      margin-bottom: 6rem;
    }
    
    .section-tag {
      display: inline-flex;
      align-items: center;
      margin-bottom: 1.5rem;
    }
    
    .tag-line {
      display: inline-block;
      width: 3.5rem;
      height: 2px;
      background-color: var(--primary-500);
      margin-right: 1rem;
    }
    
    .tag-text {
      font-size: 1rem;
      font-weight: 600;
      color: var(--primary-500);
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    
    .section-header h2 {
      font-size: clamp(2.25rem, 5vw, 3rem);
      font-weight: 700;
      color: var(--primary-100);
      margin: 0;
      line-height: 1.2;
    }
    
    /* Content Grid */
    .content-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 3rem;
    }
    
    @media (min-width: 1024px) {
      .content-grid {
        grid-template-columns: 1fr 1fr;
        gap: 3.5rem;
      }
    }
    
    /* Bio Content */
    .bio-content {
      display: flex;
      flex-direction: column;
      gap: 1.75rem;
    }
    
    .lead-text {
      font-size: 1.25rem;
      font-weight: 500;
      color: var(--primary-200);
      line-height: 1.6;
      margin: 0;
    }
    
    .bio-content p {
      color: var(--primary-300);
      line-height: 1.7;
      margin: 0;
    }
    
    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 2.5rem;
      margin-top: 1rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--primary-700);
    }
    
    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
    
    .stat-number {
      font-size: 2.5rem;
      font-weight: 700;
      color: var(--primary-500);
      line-height: 1;
      margin-bottom: 0.75rem;
    }
    
    .stat-label {
      font-size: 0.9rem;
      color: var(--primary-300);
    }
    
    /* Tabs Container */
    .tabs-container {
      padding: 0;
    }
    
    /* Tab Content */
    .tab-content {
      padding: 1rem 0.5rem;
      border-radius: 0.5rem;
    }
    
    /* Education Styles */
    .education-content {
      display: flex;
      flex-direction: column;
      gap: 2.5rem;
      padding: 0.75rem;
    }
    
    .education-item h3 {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--primary-200);
      margin: 0 0 0.75rem 0;
      padding: 0 0 0.5rem 0;
      border-bottom: 1px solid rgba(132, 165, 157, 0.15);
    }
    
    .education-meta {
      font-size: 0.9rem;
      color: var(--primary-400);
      margin-bottom: 1rem;
      font-style: italic;
    }
    
    .certification-list {
      padding-left: 1.75rem;
      margin: 1.25rem 0 0.75rem;
    }
    
    .certification-list li {
      margin-bottom: 0.75rem;
      color: var(--primary-300);
      position: relative;
    }
    
    .certification-list li::before {
      content: "";
      position: absolute;
      left: -1rem;
      top: 0.5rem;
      width: 0.35rem;
      height: 0.35rem;
      background-color: var(--primary-500);
      border-radius: 50%;
    }
    
    .certification-list li:last-child {
      margin-bottom: 0;
    }
    
    /* Skills Styles */
    .skills-content {
      display: flex;
      flex-direction: column;
      gap: 2rem;
      padding: 0.75rem;
    }
    
    .skill-bars {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
    
    .skill-item {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .skill-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }
    
    .skill-name {
      font-weight: 500;
      color: var(--primary-300);
    }
    
    .skill-percentage {
      color: var(--primary-400);
      font-weight: 600;
    }
    
    .tech-stack-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: var(--primary-200);
      margin: 1.5rem 0 1.25rem;
    }
    
    .tech-stack {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    
    /* Card title customization */
    :global(.card h3.text-lg) {
      padding: 1rem 1.5rem !important;
      margin: 0 !important;
      border-bottom: 1px solid var(--primary-700) !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .about-section {
        padding: 4rem 0 6rem;
      }
      
      .section-header {
        margin-bottom: 4rem;
      }
      
      .stats-grid {
        gap: 2rem;
      }
      
      .about-container {
        padding: 0 1.5rem;
      }
    }
    
    @media (max-width: 480px) {
      .stats-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
      }
      
      .about-container {
        padding: 0 1.25rem;
      }
    }
  </style>