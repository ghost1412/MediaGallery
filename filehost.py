import subprocess
import os
from flask import Flask, render_template, send_from_directory, render_template_string, request, redirect, url_for, send_file
from urllib.parse import quote
from PIL import Image
from functools import lru_cache

app = Flask(__name__)

# Path to your media folder
MEDIA_FOLDER = r'G:\path'  # Update this path to your folder
THUMBNAIL_FOLDER = os.path.join(MEDIA_FOLDER, 'thumbnails')

# Create the thumbnail folder if it does not exist
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

# Function to safely encode folder names and filenames for URLs
def safe_url(name):
    return quote(name)  # Safely encode spaces and special characters

def format_path(path):
    # Correct path formatting for Windows and ensure proper quoting
    return path.replace(' ', '\ ')  # Escape spaces with a backslash for Windows
# Function to generate a thumbnail for an image with caching
@lru_cache(maxsize=128)  # Cache thumbnails in memory
def generate_image_thumbnail(image_path, thumbnail_path, size=(200, 200)):
    try:
        # Check if the thumbnail already exists
        if not os.path.exists(thumbnail_path):
            # Open an image file
            with Image.open(image_path) as img:
                # Resize it to the thumbnail size
                img.thumbnail(size)
                # Save the thumbnail to the thumbnail folder
                img.save(thumbnail_path)
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")

# Function to generate a video thumbnail

def format_path(path):
    # Replace spaces with escaped spaces for Windows compatibility
    return path.replace(' ', '\ ')  # Escape spaces with a backslash for Windows

@lru_cache(maxsize=128)  # Cache video thumbnails in memory
def generate_video_thumbnail(video_path, thumbnail_path, size=(200, 200)):
    try:
        # Make sure paths are formatted correctly for Windows
        video_path = video_path.replace("\\", "/")  # Convert backslashes to forward slashes
        thumbnail_path = thumbnail_path.replace("\\", "/")  # Convert backslashes to forward slashes

        # Ensure paths are properly quoted for spaces
        video_path = format_path(video_path)
        thumbnail_path = format_path(video_path)

        # Debugging: print paths to ensure they're correct
        print(f"Video Path: {video_path}")
        print(f"Thumbnail Path: {thumbnail_path}")
        
        # Check if the thumbnail already exists
        if not os.path.exists(thumbnail_path):
            # Use ffmpeg to generate the video thumbnail
            command = [
                'ffmpeg', '-i', video_path, '-ss', '00:00:01', '-vframes', '1', '-vf', f'scale={size[0]}:{size[1]}', thumbnail_path
            ]
            print(f"Running command: {' '.join(command)}")  # Debugging: print the command
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"ffmpeg output: {result.stdout.decode()}")
            print(f"ffmpeg error: {result.stderr.decode()}")
    except Exception as e:
        print(f"Error generating thumbnail for {video_path}: {e}")



@app.route('/')
def index():
    try:
        # List files and directories in the root directory
        items = os.listdir(MEDIA_FOLDER)
        directories = [item for item in items if os.path.isdir(os.path.join(MEDIA_FOLDER, item))]
        files = [item for item in items if os.path.isfile(os.path.join(MEDIA_FOLDER, item))]

        # Separate image files for previews
        images = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        videos = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        return render_template('index.html', directories=directories, images=images, videos=videos)

    except Exception as e:
        return f"Error: {e}"

@app.route('/media/<path:filename>')
def serve_file(filename):
    try:
        # Serve the file (image or video) from the MEDIA_FOLDER
        return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return f"Error: {e}"

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    try:
        # Serve the thumbnail from the THUMBNAIL_FOLDER
        return send_from_directory(THUMBNAIL_FOLDER, filename)
    except Exception as e:
        return f"Error: {e}"

@app.route('/view_image/<path:filename>')
def view_image(filename):
    try:
        # Decode and extract the directory and file name
        directory = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        
        # Full image path
        full_image_path = os.path.join(MEDIA_FOLDER, directory, file_name)
        if not os.path.exists(full_image_path):
            return f"Error: Image {filename} not found."
        
        # List all image files in the directory
        image_files = [f for f in os.listdir(os.path.join(MEDIA_FOLDER, directory)) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        # Sort the image files for consistent order
        image_files.sort()
        
        # Ensure the current image exists in the list before accessing index
        if file_name not in image_files:
            return f"Error: {file_name} is not in the list of available images."
        
        # Get the current image's index
        current_index = image_files.index(file_name)
        
        # Get the previous and next image
        prev_image = image_files[current_index - 1] if current_index > 0 else image_files[-1]
        next_image = image_files[current_index + 1] if current_index < len(image_files) - 1 else image_files[0]
        
        # HTML Content with fullscreen image view and navigation arrows
        html_content = f"""
        <html>
        <head>
            <title>Viewing Image: {file_name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                    text-align: center;
                    overflow: hidden;
                }}
                .image-container {{
                    position: relative;
                    width: 100vw;
                    height: 100vh;
                    overflow: hidden;
                }}
                .image-container img {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    object-position: center;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }}
                .nav-buttons {{
                    position: absolute;
                    top: 50%;
                    width: 100%;
                    display: flex;
                    justify-content: space-between;
                    transform: translateY(-50%);
                    font-size: 3em;
                    color: white;
                    z-index: 10;
                    opacity: 0.8;
                    transition: opacity 0.3s ease;
                }}
                .nav-buttons a {{
                    text-decoration: none;
                    color: white;
                    background-color: rgba(0, 0, 0, 0.6);
                    padding: 10px;
                    border-radius: 50%;
                    transition: background-color 0.3s ease;
                }}
                .nav-buttons a:hover {{
                    background-color: rgba(0, 0, 0, 0.9);
                }}
                .nav-buttons .prev {{
                    left: 10px;
                }}
                .nav-buttons .next {{
                    right: 10px;
                }}
                .controls {{
                    position: absolute;
                    bottom: 20px;
                    width: 100%;
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    z-index: 10;
                }}
                .download-btn, .back-btn, .home-btn {{
                    padding: 10px 20px;
                    background-color: #007BFF;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 16px;
                }}
                .download-btn:hover, .back-btn:hover, .home-btn:hover {{
                    background-color: #0056b3;
                }}
                .download-btn {{
                    background-color: #28a745;
                }}
                .download-btn:hover {{
                    background-color: #218838;
                }}
                @media (max-width: 768px) {{
                    .nav-buttons {{
                        font-size: 2.5em;
                    }}
                    .download-btn, .back-btn, .home-btn {{
                        font-size: 14px;
                    }}
                }}
            </style>
        </head>
        <body>
            <h1>Viewing Image: {file_name}</h1>
            <div class="image-container">
                <img src="/media/{safe_url(directory + '/' + file_name)}" alt="{file_name}">
                
                <!-- Navigation Buttons -->
                <div class="nav-buttons">
                    <a href="/view_image/{safe_url(directory + '/' + prev_image)}" class="prev">&lt;</a>
                    <a href="/view_image/{safe_url(directory + '/' + next_image)}" class="next">&gt;</a>
                </div>
            </div>
            
            <!-- Control Buttons -->
            <div class="controls">
                <a href="/media/{safe_url(directory + '/' + file_name)}" class="download-btn" download>Download</a>
                <a href="/directory/{safe_url(directory)}" class="back-btn">Back to Directory</a>
                <a href="/" class="home-btn">Home</a>
            </div>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        return f"Error: {e}"


@app.route('/directory/<path:directory>')
def serve_directory(directory):
    try:
        # Decode the directory path and list contents
        directory = directory.replace('%20', ' ').replace('%26', '&')  # Decode spaces and '&'
        full_path = os.path.join(MEDIA_FOLDER, directory)
        
        if not os.path.exists(full_path):
            return f"Error: Directory {full_path} does not exist."
        
        items = os.listdir(full_path)
        directories = [item for item in items if os.path.isdir(os.path.join(full_path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(full_path, item))]
        
        # Separate image files for previews
        images = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        # Separate video files for previews
        videos = [file for file in files if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        
        # Pagination: Number of items per page
        items_per_page = 100
        page = int(request.args.get('page', 1))  # Default to page 1 if not specified
        start = (page - 1) * items_per_page
        end = start + items_per_page
        
        # Paginate images and videos
        paginated_images = images[start:end]
        paginated_videos = videos[start:end]
        
        # Total number of pages
        total_images = len(images)
        total_videos = len(videos)
        total_pages_images = (total_images // items_per_page) + (1 if total_images % items_per_page else 0)
        total_pages_videos = (total_videos // items_per_page) + (1 if total_videos % items_per_page else 0)
        
        # HTML Content to list files in the subdirectory
        html_content = f"""
        <html>
        <head>
            <title>Contents of {directory}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; }}
                h1, h2 {{ text-align: center; color: #333; }}
                .container {{
                    display: flex;
                    justify-content: center;
                    flex-wrap: wrap;
                    gap: 20px;
                    padding: 20px;
                }}
                .preview {{
                    text-align: center;
                    background-color: white;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;
                    width: 220px;
                    position: relative;
                }}
                .preview:hover {{
                    transform: scale(1.05);
                }}
                .preview img, .preview video {{
                    width: 200px;
                    height: 200px;
                    object-fit: cover;
                    border-radius: 8px;
                }}
                .preview a {{
                    display: block;
                    margin-top: 10px;
                    text-decoration: none;
                    color: #007BFF;
                    font-weight: bold;
                }}
                .preview a:hover {{
                    text-decoration: underline;
                }}
                .download-btn {{
                    margin-top: 10px;
                    display: inline-block;
                    padding: 5px 10px;
                    background-color: #28a745;
                    color: white;
                    border-radius: 4px;
                    text-decoration: none;
                }}
                .download-btn:hover {{
                    background-color: #218838;
                }}
                .folder-list {{
                    display: flex;
                    justify-content: center;
                    flex-wrap: wrap;
                    gap: 20px;
                    padding: 20px;
                }}
                .folder-item {{
                    text-align: center;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 20px;
                    width: 200px;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease, background-color 0.3s ease;
                }}
                .folder-item:hover {{
                    transform: scale(1.05);
                    background-color: #45a049;
                }}
                .folder-item a {{
                    color: white;
                    text-decoration: none;
                }}
                .folder-item a:hover {{
                    text-decoration: underline;
                }}
                .pagination {{
                    text-align: center;
                    margin-top: 20px;
                }}
                .pagination a {{
                    padding: 5px 10px;
                    text-decoration: none;
                    background-color: #007BFF;
                    color: white;
                    margin: 0 5px;
                    border-radius: 5px;
                }}
                .pagination a:hover {{
                    background-color: #0056b3;
                }}
                .pagination span {{
                    padding: 5px 10px;
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <h1>Contents of {directory}</h1>
            <h2>Directories:</h2>
            <div class="folder-list">
        """
        
        # Generate directory links with improved styling
        for subdir in directories:
            html_content += f'<div class="folder-item"><a href="/directory/{safe_url(directory + "/" + subdir)}">{subdir}</a></div>'
        html_content += "</div>"
        
        html_content += "<h2>Images:</h2><div class='container'>"
        for image in paginated_images:
            # Generate thumbnail for each image
            image_path = os.path.join(full_path, image)
            thumbnail_path = os.path.join(THUMBNAIL_FOLDER, image)
            
            # Generate thumbnail (cached if previously done)
            generate_image_thumbnail(image_path, thumbnail_path)
            
            html_content += f"""
                <div class="preview">
                    <a href="/view_image/{safe_url(directory + '/' + image)}">
                        <img src="/thumbnails/{safe_url(image)}" alt="{image}">
                    </a>
                    <a href="/media/{safe_url(directory + '/' + image)}" class="download-btn" download>Download</a>
                </div>
            """
        html_content += "</div>"
        
        html_content += "<h2>Videos:</h2><div class='container'>"
        for video in paginated_videos:
            # Generate video thumbnail for each video
            video_path = os.path.join(full_path, video)
            video_thumbnail_path = os.path.join(THUMBNAIL_FOLDER, video + ".jpg")
            
            # Generate thumbnail (cached if previously done)
            generate_video_thumbnail(video_path, video_thumbnail_path)
            
            html_content += f"""
                <div class="preview">
                    <a href="/media/{safe_url(directory + '/' + video)}">
                        <video width="200" height="200" controls>
                            <source src="/media/{safe_url(directory + '/' + video)}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </a>
                    <a href="/media/{safe_url(directory + '/' + video)}" class="download-btn" download>Download</a>
                </div>
            """
        html_content += "</div>"

        # Pagination controls for images
        html_content += "<div class='pagination'>"
        if page > 1:
            html_content += f'<a href="/directory/{safe_url(directory)}?page={page - 1}">Prev</a>'
        html_content += f'<span>Page {page} of {total_pages_images}</span>'
        if page < total_pages_images:
            html_content += f'<a href="/directory/{safe_url(directory)}?page={page + 1}">Next</a>'
        html_content += "</div>"

        # Pagination controls for videos
        html_content += "<div class='pagination'>"
        if page > 1:
            html_content += f'<a href="/directory/{safe_url(directory)}?page={page - 1}">Prev</a>'
        html_content += f'<span>Page {page} of {total_pages_videos}</span>'
        if page < total_pages_videos:
            html_content += f'<a href="/directory/{safe_url(directory)}?page={page + 1}">Next</a>'
        html_content += "</div>"

        html_content += "</body></html>"
        return render_template_string(html_content)

    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
