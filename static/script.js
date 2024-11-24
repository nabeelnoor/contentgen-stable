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
        word_count: wordCount,
        main_prompt: mainPrompt,
        language: language,
        content_style: contentStyle,
        keywords: document.getElementById('keywords').value
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
