function initTheme() {
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.classList.add('dark');
        document.getElementById('moonIcon').classList.remove('hidden');
        document.getElementById('sunIcon').classList.add('hidden');
    }
}

// Initialize theme
initTheme();

// Add theme toggle functionality
document.getElementById('themeToggle').addEventListener('click', function() {
    const html = document.documentElement;
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');
    
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
        localStorage.setItem('theme', 'light');
    } else {
        html.classList.add('dark');
        moonIcon.classList.remove('hidden');
        sunIcon.classList.add('hidden');
        localStorage.setItem('theme', 'dark');
    }
});

// Character count updates
function updateCharCount(inputId, countId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(countId);
    
    input.addEventListener('input', function() {
        counter.textContent = this.value.length;
    });
}

// Priority slider updates
function updatePriorityValue(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const value = document.getElementById(valueId);
    
    slider.addEventListener('input', function() {
        value.textContent = this.value;
    });
}

// Initialize character counters
updateCharCount('main_prompt', 'main_prompt_count');
updateCharCount('knowledge_source_1', 'knowledge_source_1_count');
updateCharCount('knowledge_source_2', 'knowledge_source_2_count');
updateCharCount('brand_voice', 'brand_voice_count');

// Initialize priority sliders
updatePriorityValue('priority_1', 'priority_1_value');
updatePriorityValue('priority_2', 'priority_2_value');

document.getElementById('contentForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const tone = document.getElementById('tone').value;
    const brandVoice = document.getElementById('brand_voice').value;
    const wordCount = document.getElementById('word_count').value;
    const mainPrompt = document.getElementById('main_prompt').value;
    const language = document.getElementById('language').value;
    const contentStyle = document.getElementById('content_style').value;

    const data = {
        tone: tone,
        brand_voice: brandVoice,
        target_audience: document.getElementById('target_audience').value,
        word_count: wordCount,
        main_prompt: mainPrompt,
        language: language,
        content_style: contentStyle,
        keywords: document.getElementById('keywords').value,
        create_title: document.getElementById('create_title').checked,
        create_slug: document.getElementById('create_slug').checked,
        create_meta: document.getElementById('create_meta').checked,
        knowledge_source_1: document.getElementById('knowledge_source_1').value,
        knowledge_source_2: document.getElementById('knowledge_source_2').value,
        priority_1: document.getElementById('priority_1').value,
        priority_2: document.getElementById('priority_2').value
    };

    fetch('/generate-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.content) {
            // Create a new div for formatted content
            const contentDiv = document.getElementById('generatedContent');
            
            // Convert markdown-like syntax to HTML
            let formattedContent = data.content
                // Convert headers
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Convert bullet points
                .replace(/\* (.*?)(\n|$)/g, '<li>$1</li>')
                // Convert numbered lists
                .replace(/\d\. (.*?)(\n|$)/g, '<li>$1</li>')
                // Convert paragraphs
                .split('\n\n').join('</p><p>');

            // Wrap bullet points in ul tags
            if (formattedContent.includes('<li>')) {
                formattedContent = '<ul>' + formattedContent + '</ul>';
            }

            // Add initial paragraph tag
            formattedContent = '<p>' + formattedContent + '</p>';
            
            // Set the formatted HTML content
            contentDiv.innerHTML = formattedContent;
            
            // Add some basic styling
            contentDiv.classList.add('generated-content');
        } else {
            document.getElementById('generatedContent').innerHTML = 
                "<p class='error'>Error: Unable to generate content.</p>";
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
