# MediaViewer - A Simple Media Browser and Viewer

**MediaViewer** is a lightweight, web-based application built with Flask that allows users to explore, view, and download media files from a structured directory. Whether you're working with images, videos, or both, MediaViewer provides an easy-to-navigate interface to browse and preview media in your collection.

---

## Features

- **Media Exploration**: Browse through folders and subdirectories of media files, including images (JPEG, PNG, GIF) and videos (MP4, AVI, MOV, MKV).
- **Thumbnail Generation**: Automatically generates thumbnails for images and video previews for quick browsing.
- **Image Viewer**: View images in full-screen mode with easy navigation between adjacent images.
- **Video Playback**: Play videos directly in the browser with built-in controls (play, pause, volume).
- **Download Support**: Download individual media files directly to your computer.
- **Responsive Design**: Clean, user-friendly interface that adapts to different screen sizes (desktop and mobile).
- **Pagination**: Efficient file listing with pagination support for large media collections.
- **Customizable Navigation**: Intuitive next/previous controls for image and video browsing.

---

## Technologies Used

- **Flask**: A Python-based micro web framework for building the backend.
- **Pillow (PIL)**: Python Imaging Library used for generating image thumbnails.
- **FFmpeg**: A multimedia framework used for generating video thumbnails.
- **HTML5 & CSS3**: Frontend technologies for rendering media files and styling the interface.
- **JavaScript**: For interactive elements and media controls (if needed).

---

## Installation

### Prerequisites

1. Python 3.6+ installed on your machine.
2. FFmpeg installed and added to your system’s PATH (required for generating video thumbnails).

### Steps to Run the Application:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/MediaViewer.git
