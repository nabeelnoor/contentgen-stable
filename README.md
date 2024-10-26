# AI Content Generator

This project is a web application that uses Google's Gemini AI to generate content based on user input. It's built with Flask for the backend and uses HTML, CSS (Tailwind), and JavaScript for the frontend.

## Features

- Generate content using AI based on user-specified parameters
- Customizable tone of writing
- Option to provide brand voice examples
- Adjustable word count for generated content
- Responsive web interface

## Technologies Used

- Backend: Python, Flask
- Frontend: HTML, Tailwind CSS, JavaScript
- AI: Google Generative AI (Gemini)

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

4. Run the application:
   ```
   python app.py
   ```

5. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. Fill out the form with your desired parameters:
   - Select the tone of writing
   - Provide an example of brand voice (optional)
   - Specify the desired word count
   - Enter the main prompt for content generation

2. Click "Generate Content"
3. View the generated content in the results section

## Deployment

This application is configured for deployment on Heroku. The `Procfile` is already set up for this purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
