// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Launch Dashboard functionality
document.getElementById('launchDashboard').addEventListener('click', function() {
    // Check if Streamlit is running
    fetch('http://localhost:8501')
        .then(response => {
            if (response.ok) {
                // Streamlit is running, open it
                window.open('http://localhost:8501', '_blank');
            } else {
                throw new Error('Streamlit not running');
            }
        })
        .catch(error => {
            // Streamlit is not running, show instructions
            showDashboardInstructions();
        });
});

function showDashboardInstructions() {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 10px;
        max-width: 500px;
        text-align: center;
    `;
    
    content.innerHTML = `
        <h3 style="color: #1f4e79; margin-bottom: 1rem;">🚀 Start the Dashboard</h3>
        <p style="margin-bottom: 1.5rem;">The Streamlit dashboard needs to be started first. Follow these steps:</p>
        <ol style="text-align: left; margin-bottom: 1.5rem; padding-left: 1.5rem;">
            <li>Open Command Prompt or Terminal</li>
            <li>Navigate to: <code style="background: #f0f0f0; padding: 2px 4px;">cd "c:\\Users\\Armaa\\OneDrive\\Desktop\\Lead generator"</code></li>
            <li>Run: <code style="background: #f0f0f0; padding: 2px 4px;">streamlit run app.py</code></li>
            <li>Click this button again once the dashboard is running</li>
        </ol>
        <button onclick="this.parentElement.parentElement.remove()" style="
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        ">Got it!</button>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Add active navigation highlighting
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        if (window.pageYOffset >= sectionTop) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});