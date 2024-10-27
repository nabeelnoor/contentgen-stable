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
        content_style: contentStyle
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
