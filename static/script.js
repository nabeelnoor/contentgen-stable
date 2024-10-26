document.getElementById('contentForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const tone = document.getElementById('tone').value;
    const brandVoice = document.getElementById('brand_voice').value;
    const wordCount = document.getElementById('word_count').value;
    const mainPrompt = document.getElementById('main_prompt').value;
    const language = document.getElementById('language').value;

    const data = {
        tone: tone,
        brand_voice: brandVoice,
        word_count: wordCount,
        main_prompt: mainPrompt,
        language: language
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
            document.getElementById('generatedContent').textContent = data.content;
        } else {
            document.getElementById('generatedContent').textContent = "Error: Unable to generate content.";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('generatedContent').textContent = "Error: Unable to generate content.";
    });
});
